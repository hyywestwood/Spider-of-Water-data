# -*- coding: utf-8 -*-
# @Time    : 2019/4/2 11:00
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : douban_movie_1.py
# @Software: PyCharm
import requests
import json


def douban():
    movie_list = []
    url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=热门&sort=recommend&page_limit=20&page_start=0'

    r = requests.get(url, verify=False)
    content = r.text
    result = json.loads(content)
    tvs = result['subjects']
    for i in range(0, len(tvs)):
        tv = {}
        tv['rate'] = tvs[i]['rate']
        tv['cover'] = tvs[i]['cover']
        tv['url'] = tvs[i]['url']
        tv['title'] = tvs[i]['title']
        movie_list.append(tv)
    return movie_list


if __name__=="__main__":
    result=douban()
    for i in result:
        print (i)