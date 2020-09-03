# -*- coding: utf-8 -*-
# @Time    : 2020/9/2 22:26
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : settings.py
# @Software: PyCharm
import configparser

config = configparser.ConfigParser()
config.read("./config.cfg")
conf_email = config['email_setting']

a = conf_email['receiver1'].split(',')

# """
# The DEFAULT section which provides default values for all other sections"""
# print("\n- DEFAULT Section")
# ## default 是所有section的默认设置，备胎...
# for key in config['bitbucket.org']: print(key)
# print("> Get default value : forwardx11 = %s\n"%config['bitbucket.org']['forwardx11'])
#
# ## 读取不同数据类型的配置参数
# print("\n- Support datatypes")
# forwardx11 = config['bitbucket.org'].getboolean('forwardx11')
# int_port = config.getint('topsecret.server.com', 'port')
# float_port = config.getfloat('topsecret.server.com', 'port')
# print("> Get int port = %d type : %s"%(int_port, type(int_port)))
# print("> Get float port = %f type : %s"%(float_port, type(float_port)))

