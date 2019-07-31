"""
@author: Alfons
@contact: alfons_xh@163.com
@file: Run.py
@time: 2019/6/24 下午10:40
@version: v1.0
"""
import os
import sys

sys.path.append(os.path.dirname(__file__))
print(sys.path)

import time
import threading
import argparse

from Dogs import EmailDog, ScheduleDog, WeiboDog


def Run():
    email_thread = threading.Thread(target=EmailDog.Run, name="Email Dog.")
    email_thread.start()

    schedule_thread = threading.Thread(target=ScheduleDog.Run, name="Schedule Dog.")
    schedule_thread.start()

    weibo_thread = threading.Thread(target=WeiboDog.Run, name="Weibo Dog.")
    weibo_thread.start()


def ArgsParser():
    parser = argparse.ArgumentParser(description='This is a LickDog.')

    parser.add_argument("-u", action="store", dest="user_id", required=True, help="Input the target weibo id.")
    parser.add_argument("-e", action="store", dest="email_to", required=True, help="Input the result email to.")
    parser.add_argument("-n", action="store", dest="poll_count", type=int, default=100, help="Poll number.")
    parser.add_argument("-t", action="store", dest="poll_interval", type=int, default=900, help="Poll interval(second).")

    return parser.parse_args()


if __name__ == '__main__':
    args = ArgsParser()

    Run()

    time.sleep(3)

    print("Begin!!!")
    ScheduleDog.AddTask(user_id=args.user_id, email_to=args.email_to, poll_count=args.poll_count, poll_interval=args.poll_interval)
