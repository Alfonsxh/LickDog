"""
@author: Alfons
@contact: alfons_xh@163.com
@file: DbDog.py
@time: 2019/7/2 下午9:31
@version: v1.0 
"""
import os
import datetime
import traceback

from threading import Lock
from sqlite3 import dbapi2 as sqlite
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool

from DogPath import storage_dir_path
from Base.DogLogger import GetLogger

logger = GetLogger("DbDog")  # 日志

sqlite_db_path = os.path.join(storage_dir_path, "dogs.db")  # 数据库文件路径

# 数据库引擎
engine = create_engine('sqlite+pysqlite:///{db}'.format(db=sqlite_db_path),
                       module=sqlite,
                       # echo=True,
                       echo=False,
                       connect_args={'check_same_thread': False},
                       poolclass=SingletonThreadPool)  # 数据库引擎

Base = declarative_base()  # orm基类

SessionCls = sessionmaker(bind=engine)  # 数据库交互会话
session_obj = SessionCls()

sqlite_lock = Lock()


# -------------------------------微博内容表----------------------------------
class Blog(Base):
    __tablename__ = "weibo"

    blog_id = Column(String(256), primary_key=True)  # blog id 唯一标识
    scheme_url = Column(String(4096))  # blog对应的url
    created_time = Column(String(256))  # blog创建时间
    crawl_time = Column(DateTime, default=datetime.datetime.now)  # blog捕获时间
    contents = Column(String(65535))  # blog文字内容
    pictures = Column(JSON())  # blog图片内容


def IsBlogExist(table_name, blog_id):
    """
    特征blog是否存在
    :param table_name: blog所在的表名
    :param blog_id: blog的id
    :return: 存在返回True，不存在返回False
    """
    try:
        Blog.__table__.name = table_name
        blog_info = session_obj.query(Blog).filter_by(blog_id=blog_id).first()
        if blog_info is None:
            logger.debug("blog({blog})在表({table})中不存在！".format(blog=blog_id, table=table_name))
            return False

        return True
    except:
        # logger.warning("表({t})可能不存在！\n{error}".format(t=table_name, error=traceback.format_exc()))
        return False


def InsertBlog(table_name, blog_id, scheme_url, created_time, contents, pictures):
    """
    插入一条blog的内容
    :param table_name: blog所在的表名
    :param blog_id: blog的id
    :param scheme_url: blog对应的url地址
    :param created_time: blog创建的时间
    :param contents: blog的文字内容
    :param pictures: blog中的图片内容
    :return: 成功返回True，失败返回False
    """
    try:
        with sqlite_lock:
            Blog.__table__.name = table_name

            if not IsBlogExist(table_name=table_name, blog_id=blog_id):
                Base.metadata.create_all(bind=engine, tables=[Blog.__table__])
                add_blog = Blog(blog_id=blog_id, scheme_url=scheme_url, created_time=created_time, contents=contents, pictures=pictures)
                session_obj.add(add_blog)
            else:
                blog_obj = session_obj.query(Blog).filter_by(blog_id=blog_id).first()
                blog_obj.scheme_url = scheme_url
                blog_obj.created_time = created_time
                blog_obj.contents = contents
                blog_obj.pictures = pictures

            session_obj.commit()
    except:
        logger.error("添加Blog表({table})时发生错误！\n{error}".format(table=table_name, error=traceback.format_exc()))


# -------------------------------微博图片记录表----------------------------------
class Picture(Base):
    __tablename__ = "picture"

    pic_id = Column(String(128), primary_key=True)  # 图片id，唯一标识
    pic_url = Column(String(4096))  # 图片的url地址
    location_path = Column(String(4096))  # 图片本地路径


def IsPictureExist(pic_id):
    """
    判断picture是否存在
    :param pic_id: 图片id
    :return: 存在返回True，不存在返回False
    """
    try:
        pic_info = session_obj.query(Picture).filter_by(pic_id=pic_id).first()
        if pic_info is None:
            logger.debug("pic({pic_id})在表Picture中不存在！".format(pic_id=pic_id))
            return False

        return True
    except:
        # logger.warning("表({t})可能不存在！\n{error}".format(t="picture", error=traceback.format_exc()))
        return False


def InsertPicture(pic_id, pic_url, location_path):
    """
    插入新的图片数据
    :param pic_id: 图片id
    :param pic_url: 图片原始地址
    :param location_path: 图片本地保存地址
    :return:
    """
    try:
        with sqlite_lock:
            if not IsPictureExist(pic_id=pic_id):
                Base.metadata.create_all(bind=engine, tables=[Picture.__table__])
                add_pic = Picture(pic_id=pic_id, pic_url=pic_url, location_path=location_path)
                session_obj.add(add_pic)
            else:
                pic_obj = session_obj.query(Picture).filter_by(pic_id=pic_id).first()
                pic_obj.pic_url = pic_url
                pic_obj.location_path = location_path

            session_obj.commit()
    except:
        logger.error("添加Picture表时发生错误！\n{error}".format(error=traceback.format_exc()))


# ------------------------------任务调度信息------------------------------------
class Schedule(Base):
    __tablename__ = "schedule"

    schedule_id = Column(String(128), primary_key=True)  # 调度id，唯一标识
    email_to = Column(String(256), primary_key=True)  # 目标weibo获取后传递的对象的email地址
    poll_count = Column(Integer)  # 轮询次数
    poll_interval = Column(Integer)  # 单次轮询时间

    def __eq__(self, other):
        return self.schedule_id == other.schedule_id \
               and self.email_to == other.email_to \
               and self.poll_count == other.poll_count \
               and self.poll_interval == other.poll_interval


def IsScheduleExist(schedule_id, email_to):
    """
    调度任务是否存在
    :param schedule_id: 调度任务id
    :param email_to: email接收地址
    :return: 存在返回True，不存在返回Fasle
    """
    try:
        schedule_info = FetchSchedule(schedule_id=schedule_id, email_to=email_to)
        if not schedule_info:
            logger.debug("pic({schedule_id})在表Schedule中不存在！".format(schedule_id=schedule_id))
            return False

        return True
    except:
        # logger.warning("表({t})可能不存在！\n{error}".format(t="schedule", error=traceback.format_exc()))
        return False


def FetchSchedule(schedule_id, email_to=None):
    """
    查询调度任务信息
    :param schedule_id: 调度任务id
    :param email_to: email接收地址
    :return: 调度任务信息列表，异常返回空list
    """
    try:
        if email_to is None:
            return session_obj.query(Schedule).filter_by(schedule_id=schedule_id).all()
        else:
            return session_obj.query(Schedule).filter_by(schedule_id=schedule_id, email_to=email_to).all()
    except:
        # logger.warning("在schedule表中查询({schedule_id})发生错误!\n{error}".format(schedule_id=schedule_id, error=traceback.format_exc()))
        return list()


def FetchAllSchedule():
    """
    查询所有调度任务信息
    :return: 成功返回所有调度任务信息，失败返回空list
    """
    try:
        return session_obj.query(Schedule).all()
    except:
        # logger.warning("查询所有调度任务信息发生错误!\n{error}".format(error=traceback.format_exc()))
        return list()


def InsertSchedule(schedule_id, email_to, poll_count, poll_interval):
    """
    更新调度任务信息
    :param schedule_id: 调度任务id
    :param email_to: email接收地址
    :param poll_count: 轮询次数
    :param poll_interval: 单次轮询时长
    :return:
    """
    try:
        with sqlite_lock:
            if not IsScheduleExist(schedule_id=schedule_id, email_to=email_to):
                Base.metadata.create_all(bind=engine, tables=[Schedule.__table__])
                add_schedule = Schedule(schedule_id=schedule_id, email_to=email_to, poll_count=poll_count, poll_interval=poll_interval)
                session_obj.add(add_schedule)
            else:
                schedule_obj = session_obj.query(Schedule).filter_by(schedule_id=schedule_id, email_to=email_to).first()
                schedule_obj.poll_count = poll_count
                schedule_obj.poll_interval = poll_interval

            session_obj.commit()
    except:
        logger.error("添加Schedule表时发生错误！\n{error}".format(error=traceback.format_exc()))

# Base.metadata.create_all(engine)
