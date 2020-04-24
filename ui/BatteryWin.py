#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/4/24 10:23 
# @Author : qingping.niu
# @File : BatteryWin.py
# @Desc : 电量测试主界面

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class BatteryWin(QWidget):
    def __init__(self,parent=None):
        super(BatteryWin,self).__init__(parent)
        self.resize(700, 400)
        self.setUpUI()

    def setUpUI(self):
        pass
