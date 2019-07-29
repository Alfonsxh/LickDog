"""
@author: Alfons
@contact: alfons_xh@163.com
@file: EmailDog.py
@time: 2019/6/24 下午10:41
@version: v1.0
"""
import time
import yagmail
import traceback

from collections import namedtuple

from Base.DogLogger import GetLogger
from Base.DogQueue import DogQueue
from Base.DogConfig import dog_config as config

EmailInfo = namedtuple("Email", "to subject contents image")  # Email结构提

logger = GetLogger("EmailDog")

email_task_queue = DogQueue()  # email任务队列

mail_sender = yagmail.SMTP(user=config.mail_user, password=config.mail_password, host=config.mail_host)  # 初始化邮件发送实例


def __SendEmail(to, subject="New Message to Lick Dog", contents="", image=None, try_number=3):
    """
    向舔狗的email发送消息
    :param to: 目标email地址
    :param subject: 标题，必须
    :param contents: 文字内容
    :param image: 图片内容
    :param try_number: 尝试重新发送的次数
    :return:
    """
    for i in range(try_number):
        try:
            content_list = list()
            if isinstance(image, str):
                content_list.append(image)
            elif isinstance(image, list):
                content_list.extend(image)

            content_list.insert(0, contents)

            mail_sender.send(to=to, subject=subject, contents=content_list)

            logger.info("email({sub}) to ({e}) 发送成功！".format(sub=subject, e=to))
            break
        except:
            logger.error("email({sub}) to ({e}) 第{i}次发送失败！\n{error}".format(sub=subject, e=to, i=i + 1, error=traceback.format_exc()))
            time.sleep(3)
            continue


# ----------------------------外部接口--------------------------------
def AddTask(to, subject, contents, image):
    """
    添加email任务
    :param to: 目标email地址
    :param subject: 标题，必须
    :param contents: 文字内容
    :param image: 图片内容
    :return: 成功返回True，失败返回False
    """
    try:
        global email_task_queue
        email_task_queue.put(EmailInfo(to=to, subject=subject, contents=contents, image=image))

        return True
    except:
        logger.error("Email添加任务({to}, {subject}, {contents}, {image})时发生错误！\n{error}".format(to=to,
                                                                                             subject=subject,
                                                                                             contents=contents,
                                                                                             image=image,
                                                                                             error=traceback.format_exc()))
        return False


def Run():
    """
    email开始工作
    :return:
    """
    task = None
    while True:
        try:
            task = email_task_queue.get()

            if not isinstance(task, EmailInfo):
                logger.warning("任务类型({t})不匹配！内容为 -> {content}".format(t=type(task), content=task))
                continue

            __SendEmail(to=task.to,
                        subject=task.subject,
                        contents=task.contents,
                        image=task.image)
        except:
            logger.error("任务({t})执行失败！发送email发生错误！\n{error}".format(t=task, error=traceback.format_exc()))
        finally:
            time.sleep(1)
