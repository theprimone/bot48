from sys import maxunicode, path
from os import getcwd

NON_BMP_MAP = dict.fromkeys(range(0x10000, maxunicode + 1), 0xfffd)

COOKIES_JSON = f'{getcwd()}/json/cookies.json'
MINE_JSON = f'{getcwd()}/json/mine.json'
FCL_USERS_JSON = f'{getcwd()}/json/fcl_users.json'
LATEST_FCL_COMMENT_LINK_TXT = f'{getcwd()}/others/latest_fcl_comment_link.txt'

FIREFOX_DIR = f'{getcwd()}/firefoxconf.selenium/'
BROWSER_OBJECT_PATH = f'{getcwd()}/others/browser.data'

WEIBO_LOGIN_URL = "https://passport.weibo.cn/signin/login"
MAX_TURN_PAGE = 20

if __name__ == '__main__':
    print(MINE_JSON)
