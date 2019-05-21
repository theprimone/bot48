import requests
from os import path, makedirs
from json import dump, loads
from constants import MINE_JSON, FCL_USERS_JSON, LATEST_FCL_COMMENT_LINK_TXT, COOKIES_JSON


def is_path_exists(path_name):  # 文件 文件夹都行
    return path.exists(path_name)


def make_dirs(dirs):
    """
    创建目录
    :param dirs: 目录路径，可迭代创建
    :return:
    """
    if not is_path_exists(dirs):
        makedirs(dirs)
        print('创建目录:', dirs)

# def check_needed_path(file_path):
#     """
#     确保文件存在
#     :param file_path:
#     :return:
#     """
#     if not path.exists(file_path):
#         open(file_path, 'w', encoding='utf-8').close()
#         print('新建文件', file_path)


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    return '\u4e00' <= uchar <= '\u9fa5'


def get_chinese_str(str):
    """
    得到汉字字符串
    :param str:
    :return:
    """
    chinese_str = ''
    for i in str:
        if is_chinese(i):
            chinese_str = chinese_str + i
    return chinese_str


def dump_dict_to_json(dict_, path_):
    with open(path_, 'w', encoding='utf-8') as jf:  # 保存中文字符时 encoding 和 ensure_ascii 需要同时设置
        dump(dict_, jf, ensure_ascii=False, indent=4)


def loads_json(path_):
    with open(path_, 'r', encoding="utf-8") as sf:
        return loads(sf.read())


def replace_link_to_https(link):
    if not link.startswith('https'):
        link = link.replace('http', 'https')
    return link


def get_html(url, headers, encode='utf-8'):
    r = requests.get(url, headers=headers)
    r.encoding = encode
    print('▶ get', url, r.status_code)
    return r.text


class Mine(object):
    def __init__(self):
        mine = loads_json(MINE_JSON)
        self.username = mine['username']
        self.password = mine['password']
        self.nickname = mine['nickname']

    def __str__(self):
        return f'Mine object (username: {self.username})'

    __repr__ = __str__


def get_fcl_users() -> dict:
    return loads_json(FCL_USERS_JSON)


def get_fcl_users_name() -> list:
    return [x for x in loads_json(FCL_USERS_JSON).keys()]


def get_fcl_user_tag(username: str) -> str:
    topics = []
    if username in get_fcl_users():
        topics.append(get_fcl_users()[username])
    return "".join(["#{}[超话]#".format(x) for x in topics])


def get_latest_fcl_comment_ids() -> list:
    with open(LATEST_FCL_COMMENT_LINK_TXT, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def write_latest_fcl_comment_ids(comment_ids: list) -> str:
    with open(LATEST_FCL_COMMENT_LINK_TXT, "w", encoding="utf-8") as f:
        f.writelines([f'{id}\n' for id in comment_ids])


def get_cookies() -> list:
    return loads_json(COOKIES_JSON)


if __name__ == "__main__":
    print(get_latest_fcl_comment_ids())
    print('===')
