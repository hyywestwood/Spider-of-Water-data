# -*- coding: utf-8 -*-
# @Time    : 2019/4/22 14:57
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : lea_1.py
# @Software: PyCharm
import urllib.request


def download(url, num_retries = 2):
    print('Downloading:',url)
    headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    request = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(request).read()
    except urllib.request.URLError as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, num_retries-1)
    return html


if __name__ == '__main__':
    html = download('http://httpstat.us/500')