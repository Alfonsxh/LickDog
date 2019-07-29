"""
@author: Alfons
@contact: alfons_xh@163.com
@file: ScheduleDog.py
@time: 2019/7/21 下午3:36
@version: v1.0 
"""
import time
import threading
import traceback

from collections import namedtuple

from Base.DogLogger import GetLogger
from Dogs import DbDog, WeiboDog

logger = GetLogger("Schedule")

ScheduleTaskCls = namedtuple("ScheduleTask", "user_id email_to")  # 调度任务结构体
schedule_task_list = list()  # 记录当前正在处理的调度任务


def __Init():
    """
    初始化调度任务
    :return:
    """
    all_schedule = DbDog.FetchAllSchedule()

    for schedule in all_schedule:
        user_id = schedule.schedule_id
        email_to = schedule.email_to
        poll_count = schedule.poll_count
        poll_interval = schedule.poll_interval

        if poll_count == 0:
            logger.info("调度任务({task})可轮询的次数为0！".format(task=user_id))
            continue

        AddTask(user_id=user_id, email_to=email_to, poll_count=poll_count, poll_interval=poll_interval)


def __AddTaskThread(user_id, email_to, poll_count, poll_interval):
    """
    调度任务线程
    :param user_id: 目标用户id
    :param email_to: 目标weibo回复的email地址
    :param poll_count: 轮询次数
    :param poll_interval: 单次轮询间隔
    :return:
    """
    try:
        # 记录任务
        global schedule_task_list

        task_obj = ScheduleTaskCls(user_id=user_id, email_to=email_to)
        schedule_task_list.append(task_obj)

        # 根据次数，向WeiboDog中添加任务
        for i in range(poll_count):
            logger.info("添加任务({task}, 共{total}次轮询, 此为第{i}次。 )。".format(task=user_id, total=poll_count, i=i + 1))

            WeiboDog.AddTask(user_id=user_id, email_to=email_to)
            DbDog.InsertSchedule(schedule_id=user_id, email_to=email_to, poll_count=poll_count - i - 1, poll_interval=poll_interval)  # 更新数据库中调度任务的轮询次数

            # 轮询时间间隔
            time.sleep(poll_interval)

        # 删除任务并退出
        schedule_task_list.remove(task_obj) if task_obj in schedule_task_list else ...
    except:
        logger.error("调度任务执行过程中发生了错误！\n{error}".format(error=traceback.format_exc()))


def AddTask(user_id, email_to, poll_count, poll_interval):
    """
    添加调度任务
    :param user_id: 目标用户id
    :param email_to: 目标weibo回复的email地址
    :param poll_count: 轮询次数
    :param poll_interval: 单次轮询间隔
    :return:
    """
    if ScheduleTaskCls(user_id=user_id, email_to=email_to) in schedule_task_list:
        logger.warning("目标调度任务({task})已经存在，请稍后再试！".format(task=(user_id, poll_count, poll_interval)))
        return

    # 更新数据库
    DbDog.InsertSchedule(schedule_id=user_id, email_to=email_to, poll_count=poll_count, poll_interval=poll_interval)

    # 启动线程开始轮询的添加任务
    t = threading.Thread(target=__AddTaskThread, args=(user_id, email_to, poll_count, poll_interval), name="schedule thread {id}-{email}".format(id=user_id, email=email_to))
    t.start()


def Run():
    __Init()
