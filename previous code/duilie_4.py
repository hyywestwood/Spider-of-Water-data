# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 16:19
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : duilie_4.py
# @Software: PyCharm
import multiprocessing
import time


class Consumer(multiprocessing.Process):
    def __init__(self, lock):
        super(Consumer, self).__init__(name = 'Consumer')
        self.lock = lock
    def run(self):
        print ('consumer wait the lock')
        time.sleep(1)
        self.lock.acquire()
        print ('consumer get the lock')
        time.sleep(1)
        self.lock.release()

class Producer(multiprocessing.Process):
    def __init__(self, lock):
        super(Producer, self).__init__(name = 'Producer')
        self.lock = lock
    def run(self):
        self.lock.acquire()
        print ('producer get the lock')
        time.sleep(100)
        self.lock.release()

def main():
    lock = multiprocessing.Lock()

    producer = Producer(lock)
    producer.start()

    consumer = Consumer(lock)
    consumer.start()

    time.sleep(3)

    producer.terminate()
    producer.join()
    print ('producer terminated')

    time.sleep(3600)

if __name__ == '__main__':
    main()