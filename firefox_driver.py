# coding=utf-8
import json
import pickle
from time import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from win32api import ShellExecute
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from socket import socket, AF_INET, SOCK_STREAM
from my_firefox import *
from utils import is_path_exists, loads_json, dump_dict_to_json, Mine
from constants import MINE_JSON, COOKIES_JSON, WEIBO_LOGIN_URL, FIREFOX_DIR, BROWSER_OBJECT_PATH
# import sys
# sys.path.append('.')


def driver_initial():
    """
    初始化浏览器对象并序列化
    :return:
    """
    profile_dir = FIREFOX_DIR  # firefox.exe -ProfileManager -no-remote
    profile = FirefoxProfile(profile_dir)
    port = socket.socket(AF_INET, SOCK_STREAM)
    try:
        # setdefaulttimeout(1) 导致启动浏览器异常 设为较大时间 如 10 无异常
        port.settimeout(2)
        port.connect(('127.0.0.1', 4444))
        port.close()
        print('4444端口已占用，geckodriver已启动')
        return True
    except Exception as e:
        print('Error :', e)
        print('4444端口未占用，geckodriver未启动')
        ShellExecute(0, 'open', 'geckodriver', '', '', 1)
        # ShellExecute(hwnd, op, file, params, dir, bShow)
        # 其参数含义如下所示。
        # hwnd：父窗口的句柄，如果没有父窗口，则为0。
        # op：要进行的操作，为“open”、“print”或者为空。
        # file：要运行的程序，或者打开的脚本。
        # params：要向程序传递的参数，如果打开的为文件，则为空。
        # dir：程序初始化的目录。
        # bShow：是否显示窗口。
        driver = webdriver.remote.webdriver.WebDriver(
            command_executor="http://127.0.0.1:4444",
            browser_profile=profile,
            desired_capabilities=DesiredCapabilities.FIREFOX
        )
        # driver.get('about:blank')
        put_browser(driver)
        return False


def is_expiry_sub():
    sub_expriy = get_sub_expriy()
    print("Cookies 过期时间 {}".format(datetime.fromtimestamp(sub_expriy)))
    return sub_expriy <= int(time() + 2 * 60 * 60)


def get_sub_expriy():
    weibo_cookies = loads_json(COOKIES_JSON)
    _sub_cookie = list(
        filter(lambda cookie: cookie['name'] == 'SUB', weibo_cookies))[0]
    sub_expriy = _sub_cookie['expiry']
    return sub_expriy


def login_weibo():
    """
    微博登录
    :return:
    """
    is_exists_cookies_json = is_path_exists(COOKIES_JSON)
    if is_exists_cookies_json:
        print("cookies json 已存在")
        is_expiry = is_expiry_sub()
        if is_expiry:
            print("Cookies 即将过期 重新获取")
            print("帐号密码登录")
            driver_initial()
            driver = get_browser()
            try:
                print('准备登陆Weibo.cn网站...')
                driver.get(WEIBO_LOGIN_URL)
                # WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "loginAction"))) 该句相较于下句不起作用
                WebDriverWait(driver, 10).until(
                    ec.visibility_of_element_located((By.ID, "loginAction")))
                elem_user = driver.find_element_by_id("loginName")
                elem_user.send_keys(Mine().username)  # 用户名
                elem_pwd = driver.find_element_by_id("loginPassword")
                elem_pwd.send_keys(Mine().password)  # 密码

                elem_sub = driver.find_element_by_id("loginAction")
                elem_sub.click()
                # 点击登陆，登录多次或异地登录可能会有验证码
                WebDriverWait(driver, 20).until(ec.url_contains('m.weibo.cn'))

                sina_cookies = driver.get_cookies()  # 包含多个 cookie 的字典列表
                # for cookie in sina_cookies:
                #     cookie['table'] = 'weibo_cookies'
                # with open(COOKIES_JSON, 'w', encoding="utf-8") as f:  # 保存Cookies
                #     f.write(json.dumps(sina_cookies, indent=4))
                dump_dict_to_json(sina_cookies, COOKIES_JSON)
                print('<登陆成功>')
                driver.close()
            except Exception as e:
                print("Error: <登录失败> {}".format(e))
        else:
            print("Cookies 登录")
            weibo_cookies = loads_json(COOKIES_JSON)
            driver_initial()
            driver = get_browser()
            driver.delete_all_cookies()
            driver.get("https://m.weibo.cn/")
            for wc in weibo_cookies:
                wc.pop('domain')
                driver.add_cookie(wc)
            driver.get("https://m.weibo.cn/")


def put_browser(driver):
    """
    浏览器对象序列化方法
    :param driver:
    :return:
    """
    params = {}
    params["session_id"] = driver.session_id
    params["server_url"] = driver.command_executor._url
    with open(BROWSER_OBJECT_PATH, 'wb') as f:
        pickle.dump(params, f)


def get_browser():
    """
    浏览器对象反序列化方法
    :return:
    """
    with open(BROWSER_OBJECT_PATH, 'rb') as f:
        params = pickle.load(f)
    driver = myWebDriver(
        service_url=params["server_url"], session_id=params["session_id"])
    return driver


if __name__ == "__main__":
    login_weibo()
