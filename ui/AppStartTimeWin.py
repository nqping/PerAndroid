#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/4/23 9:49 
# @Author : qingping.niu
# @File : AppStartTimeWin.py 
# @Desc : APP启动时间专项测试主界面

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QFont

class AppStartTimeWin(QWidget):
    def __init__(self,parent=None):
        super(AppStartTimeWin,self).__init__(parent)
        self.setWindowTitle("APP启动时间专项测试")
        self.resize(700, 500)
        self.setUpUI()

    def setUpUI(self):
        #定义布局
        self.hboxlayout = QHBoxLayout() #水平布局

        #定义控件
        packageLabel = QLabel("包名:")
        deviceLabel = QLabel("设备:")
        self.packageComboBox = QComboBox()
        self.packageComboBox.setObjectName("packageComboBox")

        self.deviceComboBox = QComboBox()
        self.deviceComboBox.setObjectName("deviceComboBox")

        self.startBtn = QPushButton("开始")
        self.startBtn.setObjectName("startBtn")

        self.refreshBtn = QPushButton("刷新")
        self.refreshBtn.setObjectName("refreshBtn")

        #样式定义
        font = QFont("Times new Roman",12)
        # font.setPixelSize(15)

        packageLabel.setFont(font)
        packageLabel.setFixedWidth(50)
        deviceLabel.setFont(font)
        deviceLabel.setFixedWidth(50)

        self.deviceComboBox.setFont(font)
        self.deviceComboBox.setFixedHeight(32)
        self.packageComboBox.setFont(font)
        self.packageComboBox.setFixedHeight(32)

        self.startBtn.setFont(font)
        self.startBtn.setFixedWidth(150)
        self.startBtn.setFixedHeight(32)
        self.refreshBtn.setFont(font)
        self.refreshBtn.setFixedWidth(150)
        self.refreshBtn.setFixedHeight(32)

        #事件定义

        #加入布局
        self.hboxlayout.addWidget(deviceLabel)
        self.hboxlayout.addWidget(self.deviceComboBox)
        self.hboxlayout.addWidget(packageLabel)
        self.hboxlayout.addWidget(self.packageComboBox)
        self.hboxlayout.addWidget(self.startBtn)
        self.hboxlayout.addWidget(self.refreshBtn)

        self.setLayout(self.hboxlayout)


        QMetaObject.connectSlotsByName(self)


