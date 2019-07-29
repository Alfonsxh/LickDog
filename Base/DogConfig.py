"""
@author: Alfons
@contact: alfons_xh@163.com
@file: DogConfig.py
@time: 2019/7/3 下午10:10
@version: v1.0 
"""
import os
import traceback
import configparser

from DogPath import base_dir_path
from Base.DogLogger import GetLogger

config_path = os.path.join(base_dir_path, "config.ini")  # 配置文件路径
logger = GetLogger()  # 日志实例


class DogConfig:
    def __init__(self):

        # email相关配置
        self.mail_user = None
        self.mail_password = None
        self.mail_host = None

        # weibo相关配置
        self.weibo_poll_time = None

        # 初始化开始
        self.Init()

    def Init(self):
        """
        配置文件初始化
        :return:
        """
        assert os.path.isfile(config_path), "日志文件({f})不存在，请确认！".format(f=config_path)

        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(config_path)

            # 初始化不同节区的配置
            self.__InitMailConfig(parser=config_parser)
            self.__InitWeiboConfig(parser=config_parser)
        except:
            logger.error("配置文件初始化失败！\n{error}".format(error=traceback.format_exc()))
            raise

    def __InitMailConfig(self, parser: configparser.ConfigParser):
        """
        读取mail相关配置
        :param parser: 配置文件parser
        :return:
        """
        self.mail_user = parser.get("MAIL", "user")
        self.mail_password = parser.get("MAIL", "password")
        self.mail_host = parser.get("MAIL", "host")

    def __InitWeiboConfig(self, parser: configparser.ConfigParser):
        """
        读取weibo相关配置
        :param parser: 配置文件parser
        :return:
        """
        self.weibo_poll_time = parser.getint("WEIBO", "poll_time") * 60

    def __repr__(self):
        return "\n".join(["self.{k} -> {v}".format(k=key, v=value) for key, value in self.__dict__.items()])


dog_config = DogConfig()
