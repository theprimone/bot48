# coding=utf-8
import re
import requests
import functools
import threading
from time import sleep
from random import randint
from bs4 import BeautifulSoup
from datetime import timedelta
from copy import deepcopy

from headers import *
from firefox_driver import *
from contant import *
from utils import get_chinese_str, make_dirs, is_path_exists, dump_dict_to_json, loads_json, get_html
from weibo import WeiBo


class RcledWeiboError(ValueError):
    pass


class ReachMaxTurnPageError(ValueError):
    pass


def initial_configure() -> None:
    if not is_path_exists(COOKIES_JSON):
        login_weibo()


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper


def get_weibo_page_url_and_number(initial=1) -> iter:
    current_number = initial
    page_tplt = 'https://weibo.cn/?page={}'
    while current_number <= MAX_TURN_PAGE:
        yield page_tplt.format(current_number), current_number
        current_number += 1
        if current_number > MAX_TURN_PAGE:
            current_number = initial


def weibos_page_parser(current_number: int, page_soup: BeautifulSoup) -> iter:
    for weibo_tag in page_soup.select('div[id^="M_"]'):
        weibo = WeiBo(weibo_tag)
        if weibo.comment_link in get_rcled_comment_links():
            raise RcledWeiboError(
                f'rcled weibo: comment like is {weibo.comment_link}'
            )
        yield weibo
    if current_number >= MAX_TURN_PAGE:
        ReachMaxTurnPageError(
            f'reach max turn page: {MAX_TURN_PAGE}'
        )
    sleep(randint(7, 16))


def weibo_filter(weibo: WeiBo) -> bool:
    content = weibo.content['text']
    if weibo.username == get_my_nickname():
        return False
    elif "应援会" in weibo.username:
        return False
    elif weibo.username in get_users_name():  # 指定昵称直接添加
        return True
    elif [x for x in get_users().values() if x in content]:  # 微博内容中有指定昵称
        return True
    # elif not [x for x in parser_content_blacklist if x in content]:  # 排除内容黑名单
    #     weibo_dict_list.append(weibo_dict)


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
    # print(soup.prettify())
    return soup


def get_rcled_comment_links() -> list:
    with open(RCL_COMMENT_LINKS, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines()]


def rcl_weibo(weibo: WeiBo) -> None:
    print('-------' * 4)
    print("预处理消息\n{}".format(weibo.prettify()))
    print("微博链接", weibo.comment_link)
    print('-------' * 4)
    # 指定微博 或 指定微博内容
    # 可能存在刚转评赞微博出现在下一页，故排除
    super_topic = get_super_topic(weibo.username)
    rc_code, l_code = weibo.repost_and_comment(super_topic), weibo.like()
    print("{}\t{}\t{}".format(weibo.username, rc_code, l_code))
    sleep(1)


def get_super_topic(username: str) -> str:
    topics = []
    if username in get_users_name():
        topics.append(get_users()[username])
    # elif weibo_content:
    #     topics = [x for x in DESTINATION_USERS_DICT.values()
    #               if x in weibo_content]
    return "".join(["#{}#".format(x) for x in topics])


def get_weibo_page_headers() -> dict:
    headers = deepcopy(firefox_request_header)
    headers['Host'] = 'weibo.cn'
    headers['Cookie'] = get_cookie()
    return headers


def get_cookie() -> str:
    def build_pair(cookie):
        return '{}={}'.format(cookie['name'], cookie['value'])

    cookies = loads_json(COOKIES_JSON)
    cookie_pairs = [build_pair(cookie) for cookie in cookies]
    return "; ".join(cookie_pairs)


def get_sub_expiry() -> int:
    def is_sub_cookie(cookie):
        return cookie['name'] == 'SUB'
    cookies = loads_json(COOKIES_JSON)
    sub_cookie = list(filter(is_sub_cookie, cookies))[0]
    return sub_cookie['expiry']


def get_users_name() -> list:
    dict_conf = loads_json(CONF_JSON)
    return [x for x in dict_conf["destination_users"].keys()]


def get_users() -> list:
    return loads_json(CONF_JSON)['destination_users']


def get_my_nickname() -> str:
    return loads_json(CONF_JSON)['nickname']


if __name__ == '__main__':
    initial_configure()
    waiting_weibos = []
    weibo_urls = get_weibo_page_url_and_number()
    try:
        while not is_expiry_sub():  # 提前两小时重获取cookies
            current_url, current_number = next(weibo_urls)
            page_soup = get_pretreat_page(current_url)
            for weibo in weibos_page_parser(current_number, page_soup):
                if weibo_filter(weibo):
                    waiting_weibos.append(weibo)
    except RcledWeiboError as err:
        print(err)
    except ReachMaxTurnPageError as err:
        print(err)
    finally:
        print(waiting_weibos)
        for weibo in waiting_weibos[::-1]:
            rcl_weibo(weibo)
        if len(waiting_weibos) and waiting_weibos[0].comment_link:
            print(f'写入最新 comment_link: {waiting_weibos[0].comment_link}')
            with open(RCL_COMMENT_LINKS, "w", encoding="utf-8") as f:
                f.write(waiting_weibos[0].comment_link + "\n")  # 写入最早操作的链接

    # login_weibo()
    # print('Cookies 即将过期,启动图形化浏览器中...')
    # print('登录成功即可重新获取Cookies')
