import re
import requests
from bs4.element import Tag
from bs4 import BeautifulSoup
from copy import deepcopy

from constants import NON_BMP_MAP, COOKIES_JSON
from utils import replace_link_to_https, get_html, loads_json
from headers import firefox_request_header


prettify_tplt = """
ღ {username} ღ
{content[text]}
{pics_count}
{fcl_panel}
{repost_reason}
""".strip()


class WeiBo(object):
    def __init__(self, weibo: Tag):
        self.__weibo = weibo
        self.username = self.get_username()
        self.comment_link = self.get_comment_link()
        self.like_link = self.get_like_link()
        self.content = self.get_content()
        self.repost_reason = self.get_repost_reason()
        self.fcl_panel = self.get_fcl_panel()
        self.pics_count = self.get_pics_count()
        # self.raw_pics_link = = self.get_row_pics_link()

    def get_username(self):
        return self.__weibo.select('[class=nk]')[0].string

    def get_comment_link(self):
        # 转发也有此链接,取后一个,在转发理由之后
        comment_link = self.__weibo.select('a[href*="comment"]')[-1]['href']
        return replace_link_to_https(comment_link)

    def get_like_link(self):
        like_link = self.__weibo.select('a[href*="attitude"]')
        if like_link:
            like_link = like_link[0]["href"]
            return replace_link_to_https(like_link)
        else:
            return 'null'

    def get_content(self):
        content = self.__weibo.select('span[class=ctt]')[-1]
        content_a_tags = content.select("a")
        inner_links = []
        for a in content_a_tags:
            inner_links.append((a.get_text(), a["href"]))
        # print("inner_links -->", inner_links)
        text = content.get_text().translate(NON_BMP_MAP)
        if text and text[0] == ':':
            text = text[1:]  # 去除冒号
        return {
            'inner_links': inner_links,
            'text': text,
        }

    def get_row_pics_link(self):
        pass

    def get_repost_reason(self):
        div_list = self.__weibo.select('div')
        # "转发理由：" tag
        repost_reason_tag = div_list[-1].select('span[class=cmt]')
        repost_reason = ""
        if repost_reason_tag and "转发理由" in repost_reason_tag[0].string:
            repost_reason = div_list[-1].get_text("|", strip=True)
            repost_reason = "".join(repost_reason.split("|")[1:-4])
        # print("repost_reason -->", repost_reason)
        return repost_reason.translate(NON_BMP_MAP)

    def get_fcl_panel(self):
        div_list = self.__weibo.select('div')
        fcl_panel = [x.get_text() for x in div_list[-1].select("*")[-4:]]
        # print("fcl_panel -->", fcl_panel)
        return " ".join(fcl_panel).translate(NON_BMP_MAP)

    def get_pics_count(self):
        div_list = self.__weibo.select('div')
        pics_count = ""
        # group_pics_link = ""
        if len(div_list) == 2:
            group_pics_link_list = div_list[0].find_all(
                "a", text=re.compile(r"组图"))
            if group_pics_link_list:
                pics_count = group_pics_link_list[0].get_text()
                # group_pics_link = group_pics_link_list[0]["href"]
        # print("pics_count -->", pics_count)
        return pics_count

    def to_dict(self):
        return {
            'username': self.username,
            'comment_link': self.comment_link,
            'like_link': self.like_link,
            'content': self.content,
            'repost_reason': self.repost_reason,
            'fcl_panel': self.fcl_panel,
            'pics_count': self.pics_count,
        }

    def prettify(self):
        return re.sub(r'\n{2,}', '\n', prettify_tplt.format(**self.to_dict()))

    def __str__(self):
        return f'Weibo object (name: {self.username})'

    __repr__ = __str__

    def repost_and_comment(self, comment) -> int:
        print('comment_link', self.comment_link)
        comment_page = get_html(self.comment_link, get_headers_with_cookie())
        comment_page_soup = BeautifulSoup(comment_page, 'lxml')
        form_tag = comment_page_soup.find('form')
        form = {
            'srcuid': form_tag.select('input[name=srcuid]')[0]['value'],
            'id': form_tag.select('input[name=id]')[0]['value'],
            'rl': form_tag.select('input[name=rl]')[0]['value'],
            'content': comment,
            'rt': '评论并转发'
        }
        repost_and_comment_url = 'https://weibo.cn' + form_tag['action']
        repost_and_comment_result = requests.post(
            repost_and_comment_url,
            headers=get_repost_and_comment_headers(self.comment_link, comment),
            data=form
        )
        repost_and_comment_result.encoding = 'utf-8'
        # print(repost_and_comment_result.text)
        return repost_and_comment_result.status_code

    def like(self) -> int:
        # print('like_link', self.like_link)
        # print(not self.like_link)
        if self.like_link == 'null':
            return
        return requests.get(self.like_link, headers=get_like_headers(self.comment_link)).status_code


def get_headers_with_cookie() -> dict:
    weibo_requests_header = deepcopy(firefox_request_header)
    weibo_requests_header['Host'] = 'weibo.cn'
    cookies_dict = loads_json(COOKIES_JSON)
    weibo_requests_header['Cookie'] = "; ".join(
        ["{}={}".format(cookie["name"], cookie["value"]) for cookie in cookies_dict])
    return weibo_requests_header


def get_repost_and_comment_headers(comment_link: str, comment: str) -> dict:
    reposet_and_comment_headers = get_like_headers(comment_link)
    reposet_and_comment_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    reposet_and_comment_headers['Content-Length'] = str(
        get_comment_length(comment))
    return reposet_and_comment_headers


def get_like_headers(comment_link: str) -> dict:
    like_headers = get_headers_with_cookie()
    like_headers['Referer'] = comment_link.split('#')[0]
    return like_headers


def get_comment_length(comment: str):
    # "" : 93
    # "a" : 94
    # "啊" : 102
    length = 93
    for c in comment:
        if '\u4e00' <= c <= '\u9fa5':
            length += 3
        else:
            length += 1
    return length
