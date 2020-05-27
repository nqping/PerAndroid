#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/5/15 10:01
# @Author : qingping.niu
# @File : performanceGui.py
# @Desc : 性能监控测试

import time, sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from framework.adb_tool.adb_async import Adb
from framework.adb_tool.exception import *
from tablib import Dataset
from framework.support import identify
from utils import utils

remnant = identify.check('.pc')
adb = Adb.create()
CPU = 'cpu(%)'
FPS = 'fps(ms)'
MEMORY = '内存(k)'
NETWORK = '流量(k)'
BATTERY = '电量(%)'
TEMPERATURE = '温度(℃)'
TOTAL_MEMORY = '总内存(k)'
TOTAL_CPU = '总CPU(%)'
NETWORK_ALL = '网速(k/s)'
NAMES = {CPU: 'cpu',
 FPS: 'fps',
 MEMORY: 'memory',
 NETWORK: 'network',
 BATTERY: 'battery',
 TEMPERATURE: 'temperature',
 TOTAL_MEMORY: 'total_memory',
 TOTAL_CPU: 'total_cpu',
 NETWORK_ALL: 'network_all_speed'}
F_NAMES = {'cpu':CPU,
 'fps':FPS,
 'memory':MEMORY,
 'network_wifi':'应用总流量(k)',
 'network_local':'应用总流量(k)',
 'network_wifi_speed':'应用网速(k/s)',
 'network_local_speed':'应用网速(k/s)',
 'network_all_speed':NETWORK_ALL,
 'battery':BATTERY,
 'temperature':TEMPERATURE,
 'timestamp':'时间(h:m:s)',
 'curActivity':'当前页面',
 'total_memory':TOTAL_MEMORY,
 'total_cpu':TOTAL_CPU}
COUNT = 10

def trap_exc_during_debug(*args):
    print(args)

sys.excepthook = trap_exc_during_debug

def clearLayout(layout):
    while layout.count() > 0:
        item = layout.takeAt(0)
        if not item:
            continue
        if isinstance(item, QLayout):
            clearLayout(item)
        w = item.widget()
        if w:
            w.close()

class Worker(QObject):
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """
    __module__ = __name__
    __qualname__ = 'Worker'
    sigStep = pyqtSignal(list)
    sigAdbErr = pyqtSignal(str)
    sigInit = pyqtSignal()

    def __init__(self, id):
        super().__init__()
        self._Worker__id = id
        self._Worker__abort = False
        self._Worker__data = None
        self._thread = None

    @pyqtSlot()
    def work(self):
        """
        Pretend this worker method does work that takes a long time. During this time, the thread's
        event loop is blocked, except if the application's processEvents() is called: this gives every
        thread (incl. main) a chance to process events, which in this sample means processing signals
        received from GUI (such as abort).
        """
        items, pkg, serial = self._Worker__data
        adb.serial = serial
        print('数据初始化中...')
        if adb.cpuHasRun:
            adb.cpuHasRun = False
            time.sleep(1)
        adb.runCPU(pkg)
        for step in range(1000000):
            _start_time = time.time()
            try:
                arr = [getattr(adb, it)(pkg) for it in items]
                if step > 1:
                    self.sigStep.emit(arr)
                elif step == 1:
                    print('checking...')
                    self.sigInit.emit()
                if adb.adbErr:
                    self.sigAdbErr.emit(str(adb.adbErr))
                    adb.adbErr = ''
            except AdbError as err:
                try:
                    self.sigAdbErr.emit(str(err))
                finally:
                    err = None
                    del err

            app.processEvents()
            if self._Worker__abort:
                break
            _offset = time.time() - _start_time
            if _offset < 1:
                time.sleep(1 - _offset)
            if self._Worker__abort:
                break

    def abort(self):
        self._Worker__abort = True

    def setData(self, data):
        self._Worker__data = data


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self._options = {}
        self._count = 0
        self._size = 0
        self._netType = '_wifi'
        self._message_box_count = 0
        self._lastTotal = 0
        self._export = None
        self._items = []
        self._last_adb_err_time = 0
        _helpAction = QPushButton('帮助')
        _helpAction.clicked.connect(self.onHelpClick)
        _helpAction.setFlat(True)
        _helpAction.setAutoFillBackground(True)
        _palette = QPalette()
        _palette.setColor(QPalette.ButtonText, QColor('#1E90FF'))
        _palette.setColor(QPalette.Button, QColor('#DCDCDC'))
        _helpAction.setPalette(_palette)
        _aboutAction = QPushButton('关于')
        _aboutAction.clicked.connect(self.onAboutClick)
        _aboutAction.setFlat(True)
        _aboutAction.setAutoFillBackground(True)
        _palette = QPalette()
        _palette.setColor(QPalette.ButtonText, QColor('#1E90FF'))
        _palette.setColor(QPalette.Button, QColor('#DCDCDC'))
        _aboutAction.setPalette(_palette)
        self.toolbar = self.addToolBar('help')
        self.toolbar.addWidget(_helpAction)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(_aboutAction)
        _widget = QWidget()
        self.layout = QVBoxLayout(_widget)
        self.setCentralWidget(_widget)
        self.resize(600, 200)
        self.setWindowTitle('性能监控')
        self.setOptionLayout()

    def setOptionLayout(self):
        self._titleLayout = QVBoxLayout()
        self.newCheckBtn(CPU, NETWORK)
        self.newCheckBtn(FPS, BATTERY)
        self.newCheckBtn(MEMORY, TEMPERATURE)
        self.newCheckBtn(TOTAL_MEMORY, TOTAL_CPU)
        self.newInput()
        _hLayout = QHBoxLayout()
        _checkbox = QCheckBox('导出Excel文件', self)
        _checkbox.stateChanged.connect(self.onExportChanged)
        _hLayout.addWidget(_checkbox)
        self._titleLayout.addLayout(_hLayout)
        btn = QPushButton('开始')
        btn.clicked.connect(self.onStart)
        self._titleLayout.addWidget(btn)
        self.layout.addLayout(self._titleLayout)

    def check(self):
        print('Checking...')
        if not remnant:
            QMessageBox.warning(self, '警告:软件到期!', '请关注微信公众号 "测试一般不一般" ，\n进行软件更新，谢谢~')
            self.close()
            sys.exit(1)
        print('OK...')

    def onHelpClick(self):
        QMessageBox.information(self, '帮助', '请关注微信公众号: "测试一般不一般" ,\n查看性能监控工具使用测试说明~')

    def onAboutClick(self):
        QMessageBox.information(self, '关于', '版本号 : {}\n日期 : {}'.format(identify.VERSION, identify.DATE))

    def onNetworkChanged(self, state):
        if state == Qt.Checked:
            self._netType = '_local'
        else:
            self._netType = '_wifi'

    def onExportChanged(self, state):
        self._export = state

    def newInput(self):
        layout = QHBoxLayout()
        self._App__pkg_edit = QLineEdit()
        self._App__pkg_edit.setPlaceholderText('包名')
        self._App__pkg_edit.setText('com.tct.launcher')
        self._App__serial_edit = QLineEdit()
        self._App__serial_edit.setPlaceholderText('设备号(单设备,可不输)')
        layout.addWidget(self._App__pkg_edit)
        layout.addWidget(self._App__serial_edit)
        self._titleLayout.addLayout(layout)

    def newCheckBtn(self, name1, name2):
        layout = QHBoxLayout()
        btn = QPushButton(name1)
        btn.setCheckable(True)
        btn.clicked[bool].connect(self.onNetworkCheck)
        layout.addWidget(btn)
        btn2 = QPushButton(name2)
        btn2.setCheckable(True)
        btn2.clicked[bool].connect(self.onNetworkCheck)
        layout.addWidget(btn2)
        self._titleLayout.addLayout(layout)

    def onStart(self):
        items = [k if k != 'network' else k + self._netType for k, v in self._options.items() if v]
        _it = 'network' + self._netType
        self._networkIndex = utils.listFind(items, _it) + 1
        self._fpsIndex = utils.listFind(items, 'fps') + 1
        if self._networkIndex > 0:
            items.append(_it + '_speed')
            items.append('network_all_speed')
        items.insert(0, 'timestamp')
        items.append('curActivity')
        self._curIndex = len(items) - 1
        if len(items) <= 1:
            QMessageBox.warning(self, '警告!', '一项指标都没选!')
            return
        pkg = self._App__pkg_edit.text()
        if not pkg:
            QMessageBox.warning(self, '错误!', '包名没有传入!')
            return
        serial = self._App__serial_edit.text()
        data = (items, pkg, serial)
        clearLayout(self._titleLayout)
        self._size = len(items)
        _windowSize = 130 * self._size
        _windowSize = _windowSize if _windowSize > 500 else 500
        self.resize(_windowSize, 500)
        self.setWorkerLayout(items)
        self.startThreads(data)

    def onReset(self):
        self.onClearModels()
        self.abortWorkers()
        adb.cpuHasRun = False
        clearLayout(self.layout)
        self.resize(600, 200)
        self.setOptionLayout()

    def onNetworkCheck(self, pressed):
        source = self.sender()
        name = NAMES[source.text()]
        self._options[name] = pressed

    def setWorkerLayout(self, items):
        self._titleLine = [F_NAMES[it] for it in items]
        _hLayout = QHBoxLayout()
        if self._export:
            self.exportBtn = QPushButton('导出')
            self.exportBtn.setEnabled(False)
            self.exportBtn.clicked.connect(self.onExport)
            _hLayout.addWidget(self.exportBtn)
        self.clearBtn = QPushButton('清空')
        self.clearBtn.clicked.connect(self.onClearModels)
        _hLayout.addWidget(self.clearBtn)
        self.exitBtn = QPushButton('停止')
        self.exitBtn.clicked.connect(self.abortWorkers)
        _hLayout.addWidget(self.exitBtn)
        self.resetBtn = QPushButton('重置')
        self.resetBtn.clicked.connect(self.onReset)
        self.resetBtn.setEnabled(False)
        _hLayout.addWidget(self.resetBtn)
        _timeLayout = QHBoxLayout()
        self._start_time = time.time()
        self._startLabel = QLabel('开始 :' + time.strftime('%H:%M:%S', time.localtime()))
        self._totalLabel = QLabel('总耗时 :')
        self.startTotalLabel = QLabel('初始流量 :')
        self.endTotalLabel = QLabel('总流量 :')
        _timeLayout.addWidget(self._startLabel)
        _timeLayout.addWidget(self._totalLabel)
        _timeLayout.addWidget(self.startTotalLabel)
        _timeLayout.addWidget(self.endTotalLabel)
        groupBox = QGroupBox('性能')
        self._treeView = QTreeView()
        self._treeView.setRootIsDecorated(True)
        self._treeView.setAutoScroll(True)
        self._treeView.setAlternatingRowColors(True)
        tree_layout = QHBoxLayout()
        tree_layout.addWidget(self._treeView)
        groupBox.setLayout(tree_layout)
        self._model = QStandardItemModel(0, self._size, self)
        for index in range(self._size):
            self._model.setHeaderData(index, Qt.Horizontal, F_NAMES[items[index]])

        self._treeView.setModel(self._model)
        self.layout.addLayout(_hLayout)
        self.layout.addLayout(_timeLayout)
        self.layout.addWidget(groupBox)
        if self._networkIndex > 0:
            self.startTotalLabel.setText('初始流量 :0k')

    def onClearModels(self):
        if self._count == 0:
            return
        self._model.removeRows(0, self._count)
        self._count = 0

    def onExport(self):
        try:
            data = Dataset(*self._items, **{'headers': self._titleLine})
            fileName = time.strftime('%m-%d-%H_%M_%S', time.localtime()) + '-performance.xls'
            with open(fileName, 'wb') as (f):
                f.write(data.export('xls'))
                QMessageBox.information(self, '导出成功!', 'Excel文件名为' + fileName)
        except Exception as err:
            try:
                QMessageBox.warning(self, '导出异常!', str(err))
            finally:
                err = None
                del err

    def addModel(self, items):
        if self._count > 100:
            self.onClearModels()
        else:
            if self._networkIndex > 0:
                self._lastTotal = items[self._networkIndex]
                items[self._networkIndex] = utils.number_format(items[self._networkIndex])
            self._model.insertRow(self._count)
            for index in range(self._size):
                self._model.setData(self._model.index(self._count, index), items[index])

            if self._fpsIndex > 0:
                if float(items[self._fpsIndex] > 16.66):
                    self._model.item(self._count, self._fpsIndex).setForeground(QBrush(QColor(255, 0, 0)))
            if not items[self._curIndex].startswith(';'):
                self._model.item(self._count, self._curIndex).setForeground(QBrush(QColor(255, 0, 0)))
                items[self._curIndex] += '(out)'
            else:
                items[self._curIndex] = items[self._curIndex].replace(';', '')
                self._model.setData(self._model.index(self._count, self._curIndex), items[self._curIndex])
        self._items.append(items)
        self._count += 1
        self._treeView.scrollToBottom()

    def startThreads(self, data):
        worker = Worker(1)
        worker.setData(data)
        thread = QThread()
        worker.moveToThread(thread)
        worker.sigStep.connect(self.onWorkerStep)
        worker.sigInit.connect(self.onInitCompleted)
        worker.sigAdbErr.connect(self.onAdbErr)
        thread.started.connect(worker.work)
        thread.start()
        self.thread = thread
        self.worker = worker

    def onInitCompleted(self):
        print('数据初始化结束!!!')

    @pyqtSlot(list)
    def onWorkerStep(self, items: list):
        self.addModel(items)

    def abortWorkers(self):
        if self._export:
            self.exportBtn.setEnabled(True)
        self.clearBtn.setEnabled(False)
        self.exitBtn.setEnabled(False)
        self.resetBtn.setEnabled(True)
        adb.cpuHasRun = False
        total = time.time() - self._start_time
        self._totalLabel.setText('总耗时 : %s' % utils.time2hms(int(total)))
        if self._networkIndex > 0:
            self.endTotalLabel.setText('总流量 : {}'.format(utils.kbFormat(self._lastTotal)))
        self.worker.abort()
        self.thread.quit()

    def onAdbErr(self, err):
        if self._message_box_count > 0:
            return
        self._message_box_count += 1
        reply = QMessageBox.question(self, 'adb连接错误!', err, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self._message_box_count -= 1


if __name__ == '__main__':
    app = QApplication([])
    form = App()
    form.show()
    if not identify.DEBUG:
        form.check()
    sys.exit(app.exec_())