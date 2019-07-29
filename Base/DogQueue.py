"""
@author: Alfons
@contact: alfons_xh@163.com
@file: DogQueue.py
@time: 2019/7/21 下午12:42
@version: v1.0 
"""
from collections import deque
from queue import Queue


class DogQueue(Queue):

    # Initialize the queue representation
    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        return len(self.queue)

    # Put a new item in the queue
    def _put(self, item):
        self.queue.append(item)

    # Get an item from the queue
    def _get(self):
        return self.queue.popleft()

    def __contains__(self, item):
        return item in self.queue
