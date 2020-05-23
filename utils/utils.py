#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/5/14 15:52 
# @Author : qingping.niu
# @File : utils.py 
# @Desc : 工具集


import re

def last2Index(source, prefix):
    """
    to get last two indexs from string with prefix
    :param prefix: str
    :return: (lastStart,lastEnd)
    """
    tmp_list = []
    for m in re.finditer(prefix, source):
        tmp_list.append(m.start())

    tmp_len = len(tmp_list)
    if tmp_len == 1:
        return (
         tmp_list[0] + len(prefix), len(source))
    if tmp_len == 0:
        return (
         0, len(source))
    return (
     tmp_list[(tmp_len - 2)] + len(prefix), tmp_list[(tmp_len - 1)])


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


def time2dh(timeOffset):
    h = timeOffset / 3600
    if h < 1:
        return round(h, 1)
    d = int(h / 24)
    h = round(h % 24, 1)
    if h >= 24:
        h -= 24
        d += 1
    if d < 1:
        return '{}小时'.format(h)
    return '{}天{}小时'.format(d, h)


def kbFormat(_source):
    source = float(_source)
    tmp = source / 1024
    if tmp < 1:
        return str(round(source, 3)) + 'K'
    source = tmp / 1024
    if source < 1:
        return str(round(tmp, 3)) + 'M'
    return str(round(source, 3)) + 'G'


def decode(bytes):
    try:
        return str(bytes.decode('UTF-8')).strip()
    except:
        return str(bytes.decode('GBK')).strip()


def number_format(num):
    text = str(num)
    size = len(text)
    count = int(size / 3.01)
    for i in range(0, count):
        text = text[:size - (i + 1) * 3] + ',' + text[size - (i + 1) * 3:]

    return text
