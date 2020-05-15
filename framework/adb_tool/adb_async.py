#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/5/14 15:29 
# @Author : qingping.niu
# @File : adb_async.py 
# @Desc : Android性能专项测试核心函数

import traceback
import re,subprocess,time,threading
import logging
from utils import utils

logger = logging.getLogger('adb_async')


def adbExce(args,**kwargs):

    def runInThread(args,kwargs):
        _serial = kwargs['serial'] if 'serial' in kwargs.keys() else ''
        _prefix = ['adb -s %s' % _serial] if _serial else ['adb']
        _command = ' '.join(_prefix + args)
        callback = kwargs['callback']
        proc = subprocess.Popen(str(_command),stderr=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
        _out,_err = proc.communicate()
        if proc.returncode == 0:
            out = utils.decode(_out)
            callback(None,out)
        else:
            err = utils.decode(_err)
            callback(err,None)

    thread = threading.Thread(target=runInThread,args=(args,kwargs))
    thread.start()
    return thread

def adb_sync(args,serial=''):
    _prefix = ['adb -s %s' % serial] if serial else ['adb']
    _command = ' '.join(_prefix + args)
    s = subprocess.Popen(str(_command), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    _out, _err = s.communicate()
    err = utils.decode(_err)
    out = utils.decode(_out)
    if s.returncode == 0:
        return (None,out)
    logger.info('cmd: %s adb err: %s' %(_command,(err+out)))
    # print('cmd: {} adb err: {}'.format(str(_command),(err+out)))
    return (err,None)


def shell(args,serial='',callback=None):
    return adbExce((['shell','"'] + args + ['"']),serial=serial,callback=callback)

def shell_sync(args, serial=''):
    return adb_sync(['shell', '"'] + args + ['"'], serial)

class Adb(object):
    serial = ''
    cpuHasRun = False

    def __init__(self,serial):
        self.serial = serial
        self.adbErr = ''
        self._Adb__network_s_index = ''
        self._Adb__network_e_index = ''
        self._Adb__network_start_total = -1
        self._Adb__pre_network = 0
        self._Adb__pre_app_network = 0
        self._Adb__pre_upload = 0
        self._Adb__pre_download = 0
        self._Adb__pid = -1
        self._Adb__uid = -1
        self._Adb__last_line = ''
        self._Adb__cpu_index = -1
        self._Adb__memory_index = -1
        self._Adb__has_cpu_index = False
        self._Adb__fps_intended_vsync_index = ''
        self._Adb__fps_frame_completed_index = ''
        self._Adb__cpu_count = ''
        self._props = dict(pid=(-1),
                           serial='',
                           uid='',
                           activity='',
                           apiLevel=0,
                           battery=0,
                           temperature=0.0,
                           cpu=0,
                           memory=0,
                           speed=0,
                           appSpeed=0,
                           network=0,
                           fps=0,
                           total_memory=0,
                           total_cpu=0)

    @staticmethod
    def create(serial=''):
        return Adb(serial)

    def timestamp(self, default=None):
        r = time.strftime('%H:%M:%S', time.localtime())
        return r

    def apiLevel(self):
        '''获取api版本'''
        def callback(err,out):
            if not(err or out):
                self.printAndThrow(err)
                self._props.update(apiLevel=0)
                return
            self._props.update(apiLevel=int(out))

        if not self._props['apiLevel']:
            try:
                t = shell(['getprop', 'ro.build.version.sdk'], serial=(self.serial), callback=callback)
                t.join()
                return self._props['apiLevel']
            except:
                self._props['apiLevel']=0
        return self._props['apiLevel']

    def uid(self,pkg):
        '''通过包名获取uid,先拿pid,再用pid去获取uid'''
        def callback():
            shell_arr = ['ps', '|', 'grep', pkg]
            if self.apiLevel() > 25:
                shell_arr=['ps', '-A', '|', 'grep', pkg]
            err,out = shell_sync(shell_arr,serial=self.serial)
            if not(err or out):
                self._Adb_uid = -1
                return
            _pid = int(out.split()[1])
            err, out = shell_sync(['cat', '/proc/%s/status' % _pid, '|', 'grep', 'Uid'], serial=self.serial)
            if not(err or out):
                self._Adb_uid = -1
                return
            self._Adb_uid = int(out.strip().split()[1])
        thread = threading.Thread(target=callback)
        thread.start()
        return self._Adb_uid


    def printError(self,err):
        if logging.DEBUG:
            traceback.print_exc()
        else:
            logger.error(err)

    def printAndThrow(self,err):
        self.printError(err)
        if not err:
            return
        msg = str(err)
        if msg.find('No process found for'):
            logger.error(msg)
        _result = bool(re.search('no devices/emulators found|device[\\s\\S]+found|more than one device/emulator|device offline|cannot connect to|device unauthorized'),msg)
        if _result:
            self.adbErr = msg

    def runCPU(self, pkg):

        def runInThread():
            try:
                _pkg_len = len(pkg)
                _len = _pkg_len if _pkg_len <= 15 else 15
                _pkg = pkg[0:_len]
                is_up_8_0 = True if self.apiLevel() > 25 else False
                _cmd = 'adb shell top -O RSS -d 1 ' if is_up_8_0 else 'adb shell top -m 50 -s rss -d 1'
                p = subprocess.Popen(_cmd, stdout=(subprocess.PIPE))
                tmp_memory_total = 0
                pkg_cpu = 0.0
                while self.cpuHasRun and subprocess.Popen.poll(p) is None:
                    output = utils.decode(p.stdout.readline().strip())
                    if not is_up_8_0:
                        r = re.search('K\\s+(\\d+)K', output)
                        if r:
                            tmp_memory_total = tmp_memory_total + int(r.group(1))
                        elif 'CPU' in output:
                            self._props['cpu'] = '{}%'.format(pkg_cpu)
                            pkg_cpu = 0.0
                            if not is_up_8_0:
                                self._props['total_memory'] = tmp_memory_total
                                tmp_memory_total = 0
                            if not self._Adb__has_cpu_index:
                                arr = output.split()
                                for i in range(len(arr)):
                                    if 'CPU' in arr[i]:
                                        self._Adb__cpu_index = i
                                        self._Adb__has_cpu_index = True
                                    if 'RSS' in arr[i]:
                                        self._Adb__memory_index = i - 1 if is_up_8_0 else i

                            elif _pkg in output:
                                arr = output.split()
                                if is_up_8_0:
                                    _cpu = float(
                                        arr[self._Adb__cpu_index]) / self._Adb__cpu_count if self._Adb__cpu_count else \
                                    arr[self._Adb__cpu_index]
                                    pkg_cpu += _cpu
                        else:
                            pkg_cpu += float(arr[self._Adb__cpu_index].replace('%', ''))
                    elif 'user' in output:
                        if is_up_8_0 and not self._Adb__cpu_count:
                            rr = re.search('(\\d+)%cpu', output)
                            if rr:
                                self._Adb__cpu_count = int(rr.group(1)) / 100
                            r = re.search('\\s(\\S+)%user[\\s\\S]*\\s(\\S+)%sys', output)
                            if r:
                                r = list(map(lambda it: float(it), r.groups()))
                                total = sum(r) / self._Adb__cpu_count if self._Adb__cpu_count else sum(r)
                                self._props['total_cpu'] = '{}%'.format(total)
                    elif 'Mem:' in output and is_up_8_0:
                        r = re.search('(\\d+)k\\sused', output)
                        if r:
                            self._props['total_memory'] = int(r.groups()[0])
                    else:
                        if 'User' in output:
                            r = is_up_8_0 or re.search('User\\s(\\d+)%[\\S\\s]*System\\s(\\d+)%', output)
                            if r:
                                r = list(map(lambda it: int(it), r.groups()))
                                self._props['total_cpu'] = '{}%'.format(sum(r))

                self.cpuHasRun = False
                p.stdout.close()
                p.kill()
            except Exception as e:
                try:
                    self.cpuHasRun = False
                finally:
                    e = None
                    del e

        thread = threading.Thread(target=runInThread)
        self.cpuHasRun = True
        thread.start()
        return thread