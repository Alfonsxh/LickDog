"""
@author: Alfons
@contact: alfons_xh@163.com
@file: Run.py
@time: 2019/6/24 下午10:40
@version: v1.0 
"""
import time
import threading

from Dogs import EmailDog, ScheduleDog, WeiboDog


def Run():
    email_thread = threading.Thread(target=EmailDog.Run, name="Email Dog.")
    email_thread.start()

    schedule_thread = threading.Thread(target=ScheduleDog.Run, name="Schedule Dog.")
    schedule_thread.start()

    weibo_thread = threading.Thread(target=WeiboDog.Run, name="Weibo Dog.")
    weibo_thread.start()


if __name__ == '__main__':
    Run()

    time.sleep(3)
    print("Begin!!!")
    ScheduleDog.AddTask(user_id="2204105703", email_to="", poll_count=100, poll_interval=900)
