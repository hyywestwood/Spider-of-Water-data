# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 13:08
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : duilie.py
# @Software: PyCharm
import multiprocessing
import time


class Consumer(multiprocessing.Process):
    def __init__(self, queue):
        super(Consumer, self).__init__(name = 'Consumer')
        self.queue = queue
    def run(self):
        while True:
            count = self.queue.get()
            print ('Consumer get count ', count[0])
            time.sleep(3)

class Producer(multiprocessing.Process):
    def __init__(self, queue, stop_event):
        super(Producer, self).__init__(name = 'Producer')
        self.queue = queue
        self.stop_event = stop_event
    def run(self):
        count = 0
        while not self.stop_event.is_set():
            self.queue.put(str(count)*65536)
            print('producer put count ', count)
            count += 1
            time.sleep(1)
        print ('producer stop loop now')

def main():
    queue = multiprocessing.Queue()

    stop_event = multiprocessing.Event()
    stop_event.clear()
    producer = Producer(queue, stop_event)
    producer.start()

    consumer = Consumer(queue)
    consumer.start()

    time.sleep(10)

    stop_event.set()
    producer.join()
    print('producer terminated')

    time.sleep(3600)

if __name__ == '__main__':
    # main()
    queue = multiprocessing.Queue()

    stop_event = multiprocessing.Event()
    stop_event.clear()
    producer = Producer(queue, stop_event)
    producer.start()

    consumer = Consumer(queue)
    consumer.start()

    time.sleep(10)

    stop_event.set()
    producer.join()
    print('producer terminated')