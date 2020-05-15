#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/4/23 9:52 
# @Author : qingping.niu
# @File : PerfToolsMainWin.py 
# @Desc : 程序主界面

import sys,qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import *

from ui.AppStartTimeWin import AppStartTimeWin
from ui.performanceGui import PerformnaceAppUi

class PerfToolsMainWin(QMainWindow):
    def __init__(self,parent=None):
        super(PerfToolsMainWin,self).__init__(parent)
        self.performnameApp = PerformnaceAppUi()
        self.layout = QHBoxLayout() #水平布局
        self.setWindowTitle("Android性能测试工具集")
        # self.appstarttimeWin = AppStartTimeWin()
        # self.setCentralWidget(self.appstarttimeWin)
        self.resize(600,200)

        self.setCentralWidget(self.performnameApp)

        #菜单
        menuBar = self.menuBar()
        self.menu = menuBar.addMenu("导航")


        self.performnaceTestAction = QAction("性能监控测试")
        self.appStartTiemAction = QAction("App启动专项测试")
        self.monkeyTestAction = QAction("Monkey专项测试")
        self.fpsTestAction = QAction("GUI过度渲染")
        self.batteryTestAction = QAction("电量测试")
        self.exitAction = QAction("退出")

        self.menu.addAction(self.performnaceTestAction)
        self.menu.addAction(self.appStartTiemAction)
        self.menu.addAction(self.monkeyTestAction)
        self.menu.addAction(self.fpsTestAction)
        self.menu.addAction(self.batteryTestAction)
        self.menu.addAction(self.exitAction)

        #事件
        self.exitAction.triggered.connect(qApp.quit)

        #工具栏
        self.toolBar = self.addToolBar("退出")
        self.toolBar.addAction(self.performnaceTestAction)
        self.toolBar.addSeparator()  # 分隔线
        self.toolBar.addAction(self.appStartTiemAction)
        self.toolBar.addAction(self.exitAction)

        #状态栏信息
        self.appStartTiemAction.setStatusTip("App启动专项测试")
        self.monkeyTestAction.setStatusTip("Monkey专项测试")
        self.batteryTestAction.setStatusTip("电量测试")
        self.performnaceTestAction.setStatusTip("性能监控测试")
        self.exitAction.setStatusTip("退出")

        self.statusBar()


        QMetaObject.connectSlotsByName(self)




