import requests
from os import path, makedirs
from json import dump, loads


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
        json_str = loads(sf.read())
    return json_str


def replace_link_to_https(link):
    if not link.startswith('https'):
        link = link.replace('http', 'https')
    return link


def get_html(url, headers, encode='utf-8'):
    r = requests.get(url, headers=headers)
    r.encoding = encode
    print('get', url, r.status_code)
    return r.text


if __name__ == "__main__":
    with open("json/user.json", "r", encoding="utf-8") as f:
        a = f.readlines()
    print(len(a))
