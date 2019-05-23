import logging
import logging.config
from os import path
from concurrent_log_handler import ConcurrentRotatingFileHandler


def pwd(*args):
    """
    返回当前项目（或文件？）绝对路径
    :param args:
    :return:
    """
    return path.join(path.dirname(__file__), *args)


# 定义三种日志输出格式
STANDARD_FORMAT = "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]"

SIMPLE_FORMAT = "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s"

ID_SIMPLE_FORMAT = "[%(levelname)s][%(asctime)s] %(message)s"

# logfile_dir = os.path.dirname(os.path.abspath(__file__))  # log文件的目录
# 如果不存在定义的日志目录就创建一个
# if not os.path.isdir(logfile_dir):
#     os.mkdir(logfile_dir)

LOG_FILE_PATH = pwd("log", "weibot.log")

LOGGING_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": STANDARD_FORMAT
        },
        "simple": {
            "format": SIMPLE_FORMAT
        },
    },
    "filters": {},
    "handlers": {
        # 打印到终端的日志
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",  # 打印到屏幕
            "formatter": "simple"
        },
        # 写入到文件的日志,收集info及以上的日志
        "default": {
            "level": "INFO",
            # "class": "logging.handlers.RotatingFileHandler",  # 保存到文件
            "class": "logging.handlers.ConcurrentRotatingFileHandler",  # 保存到文件
            "formatter": "standard",
            "filename": LOG_FILE_PATH,  # 日志文件
            "maxBytes": 1024 * 1024 * 2,  # 日志大小 5M
            "backupCount": 5,
            "encoding": "utf-8",  # 日志文件的编码
        },
    },
    "loggers": {
        "weibot": {
            "handlers": ["default", "console"],
            "level": "DEBUG",
            "propagate": True,  # 向上（更高level的logger）传递
        },
    },
}


class Logger(object):
    def __init__(self, logger_name='weibot'):
        logging.config.dictConfig(LOGGING_DICT)  # 导入配置
        logger = logging.getLogger(logger_name)
        self.info = logger.info
        self.warning = logger.warning
        self.error = logger.error


if __name__ == "__main__":
    logger = Logger()
    logger.info('hello world.')
