#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/4/23 9:47 
# @Author : qingping.niu
# @File : Main.py 
# @Desc : 程序执行总入口

import sys,qdarkstyle
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.PerfToolsMainWin import PerfToolsMainWin

if __name__== "__main__":
    app = QApplication(sys.argv) #qdarkstyle.load_stylesheet_pyqt5()
    app.setWindowIcon(QIcon("./images/main48.ico"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = PerfToolsMainWin()
    mainMindow.show()
    sys.exit(app.exec_())



