# -*- coding: utf-8 -*-
import scrapy


class DoubanbookSpider(scrapy.Spider):
    name = 'doubanbook'
    allowed_domains = ['book.douban.com']
    start_urls = ['http://book.douban.com/']

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl doubanbook'.split())