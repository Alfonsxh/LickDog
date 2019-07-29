"""
@author: Alfons
@contact: alfons_xh@163.com
@file: WeiboDog.py
@time: 2019/6/24 下午10:41
@version: v1.0 
"""
import os
import time
import datetime
import requests
import traceback

from collections import namedtuple

from Base.DogQueue import DogQueue
from Base.DogLogger import GetLogger
from Dogs import DbDog, EmailDog
from DogPath import storage_dir_path

logger = GetLogger("WeiboDog")

WeiboTaskCls = namedtuple("WeiboTask", "user_id email_to")
email_task_queue = DogQueue()  # weibo观测任务队列


def __GetContainerId(user_id):
    """
    通过weibo_id获取到微博内容的id
    :param user_id: weibo_id，唯一标识
    :return: 成功返回containerid，失败返回None
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "mweibo-pwa": "1",
        "pragma": "no-cache",
        "referer": "https://m.weibo.cn/u/{user_id}".format(user_id=user_id),
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "x-requested-with": "XMLHttpRequest"
    }

    params = {
        "type": "uid",
        "value": user_id
    }

    try:
        response = requests.get(url="https://m.weibo.cn/api/container/getIndex",
                                headers=headers,
                                params=params)

        info_body = response.json()

        assert isinstance(info_body, dict), "个人信息返回结果的类型({t} != dict)错误！".format(t=type(info_body))

        # 获得tabs列表，微博的container_id在列表中，关键字为tabKey -> weibo
        tabs_list = info_body.get("data", dict()).get("tabsInfo", dict()).get("tabs", list())
        for tab in tabs_list:
            if tab.get("tabKey") == "weibo":
                return tab.get("containerid")
    except:
        logger.error("[__GetContainerId] 获取用户微博container_id失败！{error}".format(error=traceback.format_exc()))
        return None


def __GetNewWeibo(user_id, container_id):
    """
    获取新的微博
    :param user_id: 用户id
    :param container_id: 微博的container_id
    :return: 成功最新的微博信息，失败返回None
    """

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "mweibo-pwa": "1",
        "pragma": "no-cache",
        "referer": "https://m.weibo.cn/u/{user_id}".format(user_id=user_id),
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "x-requested-with": "XMLHttpRequest"

    }

    params = {
        "type": "uid",
        "value": user_id,
        "containerid": container_id
    }

    try:
        response = requests.get(url="https://m.weibo.cn/api/container/getIndex",
                                headers=headers,
                                params=params)

        weibo_body = response.json()

        assert isinstance(weibo_body, dict), "微博body返回类型({t} != dict)错误！".format(t=type(weibo_body))

        return weibo_body.get("data", dict()).get("cards", None)
    except:
        logger.error("[__GetNewWeibo]获取目标的最新微博发生错误！{error}".format(error=traceback.format_exc()))
        return None


def __Parser(user_id, email_to, weibo_info: list):
    """
    处理单挑blog信息
    :param user_id: 用户id
    :param email_to: 目标weibo回复的email地址
    :param weibo_info: weibo信息
    :return:
    """
    assert isinstance(weibo_info, list), "返回的结果的类型({t})非list类型！内容为 -> {w}".format(t=type(weibo_info), w=weibo_info)

    for single_weibo in weibo_info:
        if not isinstance(single_weibo, dict):
            logger.warning("内容({t})非dict类型！跳过此条！".format(t=single_weibo))
            continue

        weibo_blog = single_weibo.get("mblog", dict())

        blog_id = weibo_blog.get("id")
        if DbDog.IsBlogExist(table_name=user_id, blog_id=blog_id):
            logger.debug("blog内容({blog})已经存在，跳过此条！".format(blog=(user_id, blog_id)))
            continue

        user_name = weibo_blog.get("user", dict()).get("screen_name", user_id)
        blog_text = weibo_blog.get("text", "")
        blog_url = single_weibo.get("scheme", "")
        blog_create_time = weibo_blog.get("created_at", "")
        blog_pic_id_list, blog_pic_path_list = __ParserPicture(weibo_blog.get("pics", list()))

        DbDog.InsertBlog(table_name=user_id,
                         blog_id=blog_id,
                         contents=blog_text,
                         scheme_url=blog_url,
                         created_time=blog_create_time,
                         pictures=blog_pic_id_list)

        EmailDog.AddTask(to=email_to,
                         subject="New blog from {target} {time}".format(target=user_name, time=blog_create_time),
                         contents="正文:\n{content}\n\n微博链接:\n{url}".format(content=blog_text, url=blog_url),
                         image=blog_pic_path_list)


def __ParserPicture(pic_list):
    """
    处理图片数据
    :param pic_list: 待处理的图片数据列表
    :return: 处理过的图片id列表
    """
    pic_id_list = list()
    pic_path_list = list()
    for pic in pic_list:
        pic_id = pic.get("pid")
        pic_url = pic.get("large", dict()).get("url", "")

        # 图片下载
        pic_location_path = __DownloadPicture(pic_url=pic_url,
                                              pic_path=os.path.join(storage_dir_path, "Picture", pic_id + pic_url[pic_url.rfind('.'):]))

        # 图片入库
        DbDog.InsertPicture(pic_id=pic_id, pic_url=pic_url, location_path=pic_location_path)
        pic_id_list.append(pic_id)
        pic_path_list.append(pic_location_path)

    return pic_id_list, [p for p in pic_path_list if p is not None]


def __DownloadPicture(pic_url, pic_path):
    """
    根据对应的url下载图片并保存
    :param pic_url: 图片地址
    :param pic_path: 图片本地保存路径
    :return: 下载成功 返回图片本地保存路径，失败返回None
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    try:
        content = requests.get(url=pic_url, headers=headers).content

        os.makedirs(os.path.dirname(pic_path), exist_ok=True)
        with open(pic_path, "wb") as f:
            f.write(content)

        return pic_path
    except:
        logger.error("下载图片({url})发生了错误！\n{error}".format(url=pic_url, error=traceback.format_exc()))
        return None


# ----------------------------外部接口--------------------------------
def AddTask(user_id, email_to):
    """
    添加weibo爬取任务
    :param user_id: 待爬取的weibo用户id
    :param email_to: 爬取后email对象的地址
    :return: 成功返回True，失败返回False
    """
    email_task_queue.put(WeiboTaskCls(user_id=user_id, email_to=email_to))


def Run():
    """
    开始执行
    """
    user_info = None
    while True:
        try:
            user_info = email_task_queue.get()

            assert isinstance(user_info, WeiboTaskCls), "添加的任务类型({t})错误！".format(t=type(user_info))

            logger.info("开始执行任务({user})!".format(user=user_info))
            __Parser(user_id=user_info.user_id,
                     email_to=user_info.email_to,
                     weibo_info=__GetNewWeibo(user_id=user_info.user_id, container_id=__GetContainerId(user_id=user_info.user_id)))
        except:
            logger.error("执行Weibo爬取任务(user_info={user_info})发生错误！\n{error}".format(user_info=user_info,
                                                                                   error=traceback.format_exc()))
            time.sleep(1)
