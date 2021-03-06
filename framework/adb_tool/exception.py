#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/5/15 16:36 
# @Author : qingping.niu
# @File : exception.py
# @Desc : 处理异常

class AdbError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)