from sys import maxunicode

NON_BMP_MAP = dict.fromkeys(range(0x10000, maxunicode + 1), 0xfffd)
# NEEDED DIR
JSON_DIR = "json/"
OTHERS_DIR = "others/"

CONF_JSON = 'json/conf.json'
COOKIES_JSON = 'json/cookies.json'

RCL_COMMENT_LINKS = "others/rcl_comment_links.txt"

MAX_TURN_PAGE = 20
