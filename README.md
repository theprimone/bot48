# weibot

一个自动转评赞的微博 bot

## 准备工作

* Windows 10
* Python 3.7
* 火狐浏览器
* Gecko （火狐浏览器驱动）

浏览器驱动可到 Selenium 官网[下载](https://www.seleniumhq.org/download/)，安装后需要将驱动添加到系统环境变量 Path 中。

由于使用了 [Pipenv](https://docs.pipenv.org/en/latest/) 包管理工具，上述环境就绪后使用 `pipenv install` 安装相关依赖即可使用。

## 快速上手

配置 `json/conf.json` 中的相关参数。特别的，会根据 `destination_users` 中的 key 自动转评赞该用户微博，并根据 value 带上超级话题 tag 。

随后启动 `start.py` 即可。
