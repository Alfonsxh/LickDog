"""
@author: Alfons
@contact: alfons_xh@163.com
@file: DogLogger.py
@time: 2019/7/3 下午10:13
@version: v1.0 
"""
import os
import logging

from DogPath import storage_dir_path

# 日志保存目录
logger_folder = os.path.join(storage_dir_path, "logs")
os.makedirs(logger_folder, exist_ok=True)


def GetLogger(name="LickDog"):
    """
    获取日志实例
    :param name: 日志名称
    :return: 日志实例
    """
    logger_name = name if name.endswith(".log") else name + ".log"

    logger = logging.getLogger(name=name)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt="%(asctime)s - %(filename)s[%(lineno)d] - %(funcName)s - %(levelname)s: %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # 文件日志句柄
    file_handler = logging.FileHandler(filename=os.path.join(logger_folder, logger_name))
    file_handler.setFormatter(fmt=fmt)
    file_handler.setLevel(logging.DEBUG)

    # 终端输出日志句柄
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt=fmt)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
