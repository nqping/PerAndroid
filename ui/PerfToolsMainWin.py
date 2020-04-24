#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/4/23 9:52 
# @Author : qingping.niu
# @File : PerfToolsMainWin.py 
# @Desc : 程序主界面

import sys,qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import *

from ui.AppStartTimeWin import AppStartTimeWin

class PerfToolsMainWin(QMainWindow):
    def __init__(self,parent=None):
        super(PerfToolsMainWin,self).__init__(parent)
        self.layout = QHBoxLayout() #水平布局
        self.appstarttimeWin = AppStartTimeWin()
        self.setWindowTitle("Android性能测试工具集")
        self.setCentralWidget(self.appstarttimeWin)

        #菜单
        menuBar = self.menuBar()
        self.menu = menuBar.addMenu("操作")
        self.appStartTiemAction = QAction("App启动专项测试")
        self.monkeyTestAction = QAction("Monkey专项测试")
        self.batteryTestAction = QAction("电量测试")
        self.exitAction = QAction("退出")


        #事件
        self.exitAction.triggered.connect(qApp.quit)



        #工具栏
        self.toolBar = self.addToolBar("退出")
        self.toolBar.addAction(self.exitAction)

        self.toolBar.addAction(self.batteryTestAction)


        #状态栏信息
        self.appStartTiemAction.setStatusTip("App启动专项测试")
        self.monkeyTestAction.setStatusTip("Monkey专项测试")
        self.batteryTestAction.setStatusTip("电量测试")

        self.statusBar()






        QMetaObject.connectSlotsByName(self)




