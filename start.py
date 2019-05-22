# coding=utf-8
from weibo import WeiBo
import re
import requests
import functools
import threading
from time import sleep
from random import randint
from bs4 import BeautifulSoup
from datetime import timedelta
from copy import deepcopy

from headers import firefox_request_header
from firefox_driver import login_weibo, is_expiry_sub
from constants import MAX_TURN_PAGE, COOKIES_JSON
from utils import get_chinese_str, make_dirs, is_path_exists, \
    dump_dict_to_json, loads_json, get_html, \
    get_fcl_users, get_latest_fcl_comment_ids, get_cookies, \
    get_fcl_users_name, get_fcl_user_tag, Mine, \
    write_latest_fcl_comment_ids
from logger import Logger


LOG = Logger()


class ParsedWeiboError(ValueError):
    pass


def initial_configure() -> None:
    if not is_path_exists(COOKIES_JSON):
        login_weibo()


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        LOG.info(f'call {func.__name__}():')
        return func(*args, **kw)
    return wrapper


def get_weibo_page_url_and_number(initial=1) -> iter:
    current_number = initial
    page_tplt = 'https://weibo.cn/?page={}'
    while current_number <= MAX_TURN_PAGE:
        yield page_tplt.format(current_number)
        current_number += 1
    return f'reach max turn page: {MAX_TURN_PAGE}'


def weibos_page_parser(page_soup: BeautifulSoup) -> iter:
    for weibo_tag in page_soup.select('div[id^="M_"]'):
        weibo = WeiBo(weibo_tag)
        comment_id = get_weibo_id_by_comment_link(weibo.comment_link)
        if comment_id in get_latest_fcl_comment_ids():
            raise ParsedWeiboError(
                f'last parse weibo: comment id is [{comment_id}]'
            )
        if not weibo_preposition_filter(weibo):
            continue
        LOG.info(f'-> [{weibo.username}]\t{weibo.fcl_panel}')
        yield weibo
    seconds_to_sleep = randint(3, 6)
    LOG.info(f'page sleep: {seconds_to_sleep}s')
    sleep(seconds_to_sleep)


def weibo_preposition_filter(weibo: WeiBo) -> bool:
    if weibo.username == Mine().nickname:
        return False
    return True


def weibo_postposition_filter(weibo: WeiBo) -> bool:
    content = weibo.content['text']
    if "应援会" in weibo.username:
        return False
    elif weibo.username in get_fcl_users_name():  # 指定昵称直接添加
        return True
    elif [x for x in get_fcl_users().values() if x in content]:  # 微博内容中有指定昵称
        return True
    # elif not [x for x in parser_content_blacklist if x in content]:  # 排除内容黑名单
    #     weibo_dict_list.append(weibo_dict)
    return False


def get_pretreat_page(url: str) -> BeautifulSoup:
    html = get_html(url, get_weibo_page_headers())  # 打开每页链接
    soup = BeautifulSoup(html, 'lxml')
    soup.style.extract()
    soup.script.extract()
    div_list = soup.select("body > div")
    div_list[0].extract()
    div_list[1].extract()
    div_list[2].extract()
    [x.unwrap() for x in soup.find_all("a", text=re.compile(r"#.+?#"))]  # 移除超话链接
    [x.unwrap() for x in soup.find_all("a", text=re.compile(r"^@.+?"))]  # 移除@链接
    [x.extract() for x in soup.find_all("a", text="收藏")]  # 移除tag - "收藏"
    div_list[-5].extract()
    div_list[-4].extract()
    div_list[-3].extract()
    div_list[-2].extract()
    # LOG.info(soup.prettify())
    return soup


def fcl_weibo(weibo: WeiBo) -> None:
    LOG.info(f'weibo comment link: {weibo.comment_link}')
    LOG.info(f'weibo prettify: {weibo.prettify()}')
    tags = get_fcl_user_tag(weibo.username)
    LOG.info(f'weibo fc tags: {tags}')
    rc_code, l_code = weibo.repost_and_comment(tags), weibo.like()
    LOG.info(f'✔ {weibo.username}\t{rc_code}\t{l_code}')
    sleep(1)


def get_weibo_page_headers() -> dict:
    headers = deepcopy(firefox_request_header)
    headers['Host'] = 'weibo.cn'
    headers['Cookie'] = get_cookie()
    return headers


def get_cookie() -> str:
    def build_pair(cookie):
        return '{}={}'.format(cookie['name'], cookie['value'])

    cookie_pairs = [build_pair(cookie) for cookie in get_cookies()]
    return "; ".join(cookie_pairs)


def get_sub_expiry() -> int:
    def is_sub_cookie(cookie):
        return cookie['name'] == 'SUB'
    sub_cookie = list(filter(is_sub_cookie, get_cookies()))[0]
    return sub_cookie['expiry']


def get_weibo_id_by_comment_link(comment_link: str):
    # https://weibo.cn/comment/HvdFovDeR?uid=5230456780&rl=0#cmtfrm
    return comment_link.split('?')[0].split('/')[-1]


def start() -> None:
    initial_configure()
    waiting_weibos = []
    weibo_urls = get_weibo_page_url_and_number()
    first_page_comment_ids = []
    try:
        while not is_expiry_sub():  # 提前两小时重获取cookies
            current_url = next(weibo_urls)
            page_soup = get_pretreat_page(current_url)
            if (len(first_page_comment_ids) == 0):
                comment_links_tag = page_soup.find_all(
                    'a', text=re.compile('^评论')
                )
                first_page_comment_ids = [
                    get_weibo_id_by_comment_link(tag['href']) for tag in comment_links_tag
                ]
            for weibo in weibos_page_parser(page_soup):
                if weibo_postposition_filter(weibo):
                    waiting_weibos.append(weibo)
    except ParsedWeiboError as err:
        LOG.error(err)
    except StopIteration as err:
        LOG.error(err.value)
    finally:
        LOG.info(f'weibos\'s count to fcl: {len(waiting_weibos)}')
        for weibo in waiting_weibos[::-1]:
            fcl_weibo(weibo)
        LOG.info(f'update latest comment_ids: {first_page_comment_ids}')
        write_latest_fcl_comment_ids(first_page_comment_ids)

    # login_weibo()
    LOG.info('cookies will expire, start brower to refresh...')


if __name__ == '__main__':
    start()
