"""
@author: Alfons
@contact: alfons_xh@163.com
@file: test_DbDog.py
@time: 2019/7/23 下午9:31
@version: v1.0 
"""
from Dogs import DbDog


def Test_ScheduleInsert():
    DbDog.InsertSchedule("123456", "xiaohuihui100@gmail.com", 10, 900)


def Test_ScheduleFetchAll():
    res = DbDog.FetchAllSchedule()
    pass


def Test_ScheduleFetch():
    res = DbDog.FetchSchedule("123456")
    res2 = DbDog.FetchSchedule("234567")
    pass


if __name__ == '__main__':
    Test_ScheduleInsert()

    Test_ScheduleFetchAll()

    Test_ScheduleFetch()
