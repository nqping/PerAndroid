#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/5/14 15:52 
# @Author : qingping.niu
# @File : utils.py 
# @Desc : 工具集


def decode(bytes):
    try:
        return str(bytes.decode('UTF-8')).strip()
    except:
        return str(bytes.decode('GBK')).strip()


def listFind(_list, item):
    try:
        return _list.index(item)
    except:
        return -1

def time2hms(timeOffset):
    m = int(timeOffset / 60)
    if m < 1:
        return '{}秒'.format(int(timeOffset))
    s = round(timeOffset % 60, 2)
    h = int(m / 60)
    if h < 1:
        return '{}分钟{}秒'.format(m, s)
    m = m % 60
    return '{}小时{}分钟{}秒'.format(h, m, s)
