#!/usr/bin/sh python
# -*- coding: utf-8 -*-
# @Time : 2020/5/15 10:01
# @Author : qingping.niu
# @File : adb_async.py
# @Desc : 性能监控命令集

import re, subprocess, time, threading
from utils import utils
import traceback
from framework.support import identify

ERROR_TAG = '!occur err!'

def adbExec(args, **kwargs):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that
    would give to subprocess.Popen.
    """

    def runInThread(args, kwargs):
        _serial = kwargs['serial'] if 'serial' in kwargs.keys() else ''
        _prefix = ['adb -s %s' % _serial] if _serial else ['adb']
        _command = ' '.join(_prefix + args)
        callback = kwargs['callback']
        proc = subprocess.Popen((str(_command)), stderr=(subprocess.PIPE), stdout=(subprocess.PIPE), shell=True)
        _out, _err = proc.communicate()
        if proc.returncode == 0:
            out = utils.decode(_out)
            callback(None, out)
        else:
            err = utils.decode(_err)
            callback(err, None)

    thread = threading.Thread(target=runInThread, args=(args, kwargs))
    thread.start()
    return thread


def shell(args, serial='', callback=None):
    return adbExec((['shell', '"'] + args + ['"']), serial=serial, callback=callback)


def shell_sync(args, serial=''):
    return adb_sync(['shell', '"'] + args + ['"'], serial)


def adb_sync(args, serial=''):
    _prefix = ['adb -s %s' % serial] if serial else ['adb']
    _command = ' '.join(_prefix + args)
    s = subprocess.Popen((str(_command)), stderr=(subprocess.PIPE), stdout=(subprocess.PIPE), shell=True)
    _out, _err = s.communicate()
    err = utils.decode(_err)
    out = utils.decode(_out)
    if s.returncode == 0:
        return (None, out)
    print('cmd : ', _command, 'adb err : ', err + out)
    return (
     err, None)


class Adb:
    serial = ''
    cpuHasRun = False

    def __init__(self, serial):
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

    def uid(self, pkg):

        def callback():
            shell_arr = [
             'ps', '|', 'grep', pkg]
            if self.apiLevel() > 25:
                shell_arr = [
                 'ps', '-A', '|', 'grep', pkg]
            err, out = shell_sync(shell_arr, serial=(self.serial))
            if not (err or out):
                self._Adb__uid = -1
                return
            _pid = int(out.split()[1])
            err, out = shell_sync(['cat', '/proc/%s/status' % _pid, '|', 'grep', 'Uid'], serial=(self.serial))
            if not (err or out):
                self._Adb__uid = -1
                return
            self._Adb__uid = int(out.strip().split()[1])

        thread = threading.Thread(target=callback)
        thread.start()
        return self._Adb__uid

    def apiLevel(self):

        def callback(err, out):
            if not (err or out):
                self.printAndThrow(err)
                self._props.update(apiLevel=0)
                return
            self._props.update(apiLevel=(int(out)))

        if not self._props['apiLevel']:
            try:
                t = shell(['getprop', 'ro.build.version.sdk'], serial=(self.serial), callback=callback)
                t.join()
                return self._props['apiLevel']
            except:
                self._props['apiLevel'] = 0

        return self._props['apiLevel']

    def batteryAndTemperature(self):

        def callback(err, out):
            if not (err or out):
                self.printAndThrow(err)
                return
            search_obj = re.search('level:[\\s*](\\d+)[\\s\\S]*temperature:[\\s*](\\d+)', out, re.M | re.I)
            if search_obj:
                self._props['battery'] = int(search_obj.group(1))
                self._props['temperature'] = float(search_obj.group(2)) / 10.0

        try:
            shell(['dumpsys', 'battery'], serial=(self.serial), callback=callback)
            print('battery', self._props['battery'], self._props['temperature'])
            return (
             self._props['battery'], self._props['temperature'])
        except Exception as err:
            try:
                self.printAndThrow(err)
                return (0, 0)
            finally:
                err = None
                del err

    def battery(self, default=None):
        self.batteryAndTemperature()
        return self._props['battery']

    def temperature(self, default=None):
        self.batteryAndTemperature()
        return self._props['temperature']

    def cpu(self, pkg):
        return self._props['cpu']

    def memory(self, pkg):
        return utils.number_format(self.fetch_memory(pkg))

    def total_cpu(self, pkg):
        return self._props['total_cpu']

    def total_memory(self, pkg):
        return utils.number_format(self._props['total_memory'])

    def fetch_memory(self, pkg):

        def callback(err, out):
            #TODO 去掉not,修改为 err is not None
            if err:
                if not out:
                    self.printAndThrow(err)
                    self._props['memory'] = '0'
            else:
                match = re.match('[\\s\\S]*TOTAL\\s+(\\d+)', out, re.M)
                if not match:
                    self._props['memory'] = '0'
                else:
                    self._props['memory'] = match.group(1)

        try:
            shell(['dumpsys', 'meminfo', pkg], serial=(self.serial), callback=callback)
        except Exception as err:
            try:
                self.printAndThrow(err)
            finally:
                err = None
                del err
        return self._props['memory']

    def network(self, pkg, mType='wlan0', mType2='rmnet_data0'):

        def callback(err, out):
            if not (err or out):
                self.printAndThrow(err)
                self._props.update(speed=0, network=0)
                return
            _uid = self.uid(pkg)
            lines = out.split('\n')
            traffic = 0
            app_traffic = 0
            for line in lines:
                items = line.strip().split()
                traffic += int((int(items[5]) + int(items[7])) / 1024)
                if _uid > 0 and str(_uid) in line:
                    app_traffic += int((int(items[5]) + int(items[7])) / 1024)

            if self._Adb__network_start_total <= 0:
                self._Adb__network_start_total = app_traffic
                self._Adb__pre_app_network = app_traffic
            net = app_traffic - self._Adb__network_start_total
            if net < 0:
                net = 0
            speed = traffic - self._Adb__pre_network
            if speed > 20000 or speed < 0:
                speed = 0
            app_speed = app_traffic - self._Adb__pre_app_network
            if app_speed > 10000 or app_speed < 0:
                app_speed = 0
            if app_speed > speed:
                speed = app_speed
            self._props.update(speed=speed, network=net, appSpeed=app_speed)
            self._Adb__pre_network = traffic
            self._Adb__pre_app_network = app_traffic

        try:
            shell(['cat', '/proc/net/xt_qtaguid/stats', '|', 'grep', '0x0'], serial=(self.serial), callback=callback)
            return (
             self._props['speed'], self._props['network'], self._props['appSpeed'])
        except Exception as err:
            try:
                self.printAndThrow(err)
                return (0, 0)
            finally:
                err = None
                del err

    def network_local(self, pkg):
        speed, total, app_speed = self.network(pkg, 'rmnet0', 'rmnet_data0')
        return total

    def network_local_speed(self, default=None):
        return self._props['appSpeed']

    def network_wifi(self, pkg):
        speed, total, app_speed = self.network(pkg, 'wlan0')
        return total

    def network_wifi_speed(self, default=None):
        return self._props['appSpeed']

    def network_all_speed(self, defalut=None):
        return self._props['speed']

    def fps(self, pkg):

        def callback1(out):
            s_index = out.find('Profile data in ms:')
            if s_index < 0:
                self._props.update(fps=0)
                return
            e_index = out.find('View hierarchy:')
            source = out[s_index:e_index]
            source_list = list(filter(lambda it: re.match('\\s*[0-9][\\s\\S]*', it), source.split('\n')))
            if len(source_list) == 0:
                self._props.update(fps=0)
                return
            fps_list = [sum(list(map(lambda item: float(item), it.split()))) for it in source_list]
            result = round(sum(fps_list) / len(fps_list), 2)
            self._props.update(fps=result)

        def callback2(out):
            STR_INDEX = '---PROFILEDATA---'
            content_index_s = utils.last2Index(out, STR_INDEX)
            content = out[content_index_s[0]:content_index_s[1]]
            content_arr = list(filter(lambda it: bool(re.match('\\s*[0-9|a-z|A-Z]', it)), content.split('\n')))
            _first = False
            if not (self._Adb__fps_intended_vsync_index and self._Adb__fps_frame_completed_index):
                _first = True
                content_title = content_arr[0].split(',')
                self._Adb__fps_intended_vsync_index = content_title.index('IntendedVsync')
                self._Adb__fps_frame_completed_index = content_title.index('FrameCompleted')
            content_arr_len = len(content_arr)
            if content_arr_len <= 1:
                self._props.update(fps=0)
                return
            try:
                test_index = content_arr.index(self._Adb__last_line)
            except ValueError:
                test_index = -1

            content_arr_start_index = test_index + 1 if test_index > 1 else 1
            self._Adb__last_line = content_arr[(content_arr_len - 1)]
            if _first:
                self._props.update(fps=0)
                return
            intended_vsync_datas = 0
            frame_completed_datas = 0
            data_len = content_arr_len - content_arr_start_index
            if data_len <= 0:
                self._props.update(fps=0.0)
                return
            for i in range(content_arr_start_index, content_arr_len):
                line_arr = content_arr[i].split(',')
                intended_vsync_datas += int(line_arr[self._Adb__fps_intended_vsync_index])
                frame_completed_datas += int(line_arr[self._Adb__fps_frame_completed_index])

            result = round((frame_completed_datas - intended_vsync_datas) / data_len / 1000000, 2)
            self._props.update(fps=result)

        def callback(err, out):
            if not (err or out):
                self._props.update(fps=0)
                self.printAndThrow(err)
                return
            if out.find('IntendedVsync') > 0:
                callback2(out)
                return
            if out.find('Profile data in ms:') > 0:
                callback1(out)
                return
            self._props.update(fps=0)

        try:
            shell(['dumpsys', 'gfxinfo', pkg, 'framestats'], serial=(self.serial), callback=callback)
            return self._props['fps']
        except Exception as err:
            try:
                self.printAndThrow(err)
                return 0
            finally:
                err = None
                del err

    def curActivity(self, pkg=None):

        def callback(err, out):
            #TODO 此处调整err is not None
            if err:
                out or self.printAndThrow(err)
                print('err command result : ', out)
                self._props.update(activity='unknown')
                return
            else:
                _tmp = re.search('[;|/](\\S+)\\s', out).group(1)
                _prefix = re.search('cmp=(\\S+)/', out).group(1)
                if not _tmp.startswith('.'):
                    _curActivity = _tmp
                else:
                    _curActivity = _prefix + _tmp
            if pkg:
                _curActivity = _curActivity.replace(pkg, '')
                if _prefix == pkg:
                    _curActivity = ';' + _curActivity
            self._props.update(activity=_curActivity)

        try:
            shell(['dumpsys', 'activity', 'activities', '|', 'grep', 'Intent'], serial=(self.serial), callback=callback)
            return self._props['activity']
        except Exception as err:
            try:
                self.printAndThrow(err)
                return ''
            finally:
                err = None
                del err

    def runCPU(self, pkg):

        def runInThread():
            try:
                is_up_8_0 = True if self.apiLevel() > 25 else False
                _cmd = 'adb shell top -O RSS -d 1 ' if is_up_8_0 else 'adb shell top -m 50 -s rss -d 1'
                p = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                tmp_memory_total = 0
                pkg_cpu = 0.0
                while self.cpuHasRun and subprocess.Popen.poll(p) is None:
                    output = utils.decode(p.stdout.readline().strip())
                    # print(output)
                    if is_up_8_0 == False:
                        r = re.search('K\\s+(\\d+)K', output)
                        if r is not None:
                            tmp_memory_total = tmp_memory_total + int(r.group(1))
                            if pkg in output:
                                arr = output.split()
                                if is_up_8_0 == False:
                                    pkg_cpu += float(arr[self._Adb__cpu_index].replace('%', ''))
                                    self._props['cpu'] = '{}%'.format(pkg_cpu)
                        elif 'CPU' in output:
                            self._props['cpu'] = '{}%'.format(pkg_cpu)
                            pkg_cpu = 0.0
                            if is_up_8_0 == False:
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

                        else:
                            if 'User' in output:
                                r = is_up_8_0 or re.search('User\\s(\\d+)%[\\S\\s]*System\\s(\\d+)%', output)
                                if r:
                                    r = list(map(lambda it: int(it), r.groups()))
                                    self._props['total_cpu'] = '{}%'.format(sum(r))
                    else:
                        if 'user' in output:
                            if is_up_8_0 and self._Adb__cpu_count is not None:
                                rr = re.search('(\\d+)%cpu', output)
                                if rr:
                                    self._Adb__cpu_count = int(rr.group(1)) / 100
                                r = re.search('\\s(\\S+)%user[\\s\\S]*\\s(\\S+)%sys', output)
                                if r:
                                    # r = list(map(lambda it: float(it), r.groups()))
                                    # self._props['total_cpu'] = '{}%'.format(sum(r))
                                    r = list(map(lambda it: float(it), r.groups()))
                                    total = sum(r) / self._Adb__cpu_count if self._Adb__cpu_count else sum(r)
                                    self._props['total_cpu'] = '{}%'.format(total)

                        elif 'Mem:' in output and is_up_8_0:
                            r = re.search('(\\d+)k\\sused', output)
                            if r:
                                self._props['total_memory'] = int(r.groups()[0])

                        elif 'CPU' in output:
                            self._props['cpu'] = '{}%'.format(pkg_cpu)
                            pkg_cpu = 0.0
                            if not self._Adb__has_cpu_index:
                                arr = output.split()
                                for i in range(len(arr)):
                                    if 'CPU' in arr[i]:
                                        self._Adb__cpu_index = i
                                        print('self._Adb__cpu_index==%s'%self._Adb__cpu_index)
                                        self._Adb__has_cpu_index = True
                                    if 'RSS' in arr[i]:
                                        self._Adb__memory_index = i-1 if is_up_8_0 else i

                        else:
                            if pkg in output:
                                arr = output.split()
                                pkg_cpu += float(arr[self._Adb__cpu_index].replace('%', ''))
                                self._props['cpu']='{}%'.format(pkg_cpu)
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

    def printError(self, err):

        if identify.DEBUG:
            traceback.print_exc()
        else:
            print(str(err))

    def printAndThrow(self, err):
        self.printError(err)
        if not err:
            return
        msg = str(err)
        if msg.find('No process found for'):
            print(msg)
        _result = bool(re.search('no devices/emulators found|device[\\s\\S]+found|more than one device/emulator|device offline|cannot connect to|device unauthorized', msg))
        if _result:
            self.adbErr = msg
