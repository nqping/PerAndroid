"""
@File : identify.py
@Author: qingping.niu
@Date : 2020/5/23
@Desc :
"""

from hashlib import md5
from os import path
from utils import utils
import pickle, time
CP = path.expanduser('~') + path.sep
DEADLINE = 15552000
VERSION = '1.2.1'
DATE = '2020.3.25-15:57'
DESCRIPTION = 'performance-jimmie-{}-{}'.format(VERSION, DATE).encode('utf-8')
DEBUG = False

def __getMd5():
    _md5 = md5()
    _md5.update(DESCRIPTION)
    return _md5.hexdigest()


def __dumpPickle(ppath):
    _conf = {'key':__getMd5(),
     'start':time.time()}
    _f = open(ppath, 'wb')
    pickle.dump(_conf, _f, protocol=(-1))
    _f.close()


def __loadPickle(ppath):
    if not path.exists(ppath):
        return ''
    _f = open(ppath, 'rb')
    _conf = pickle.load(_f)
    _f.close()
    return _conf


def check(name):
    _cp = CP + name
    _conf = __loadPickle(_cp)
    if not _conf:
        __dumpPickle(_cp)
        _conf = __loadPickle(_cp)
    _md5 = __getMd5()
    if _md5 != _conf['key']:
        __dumpPickle(_cp)
        _conf = __loadPickle(_cp)
    _startTime = float(_conf['start'])
    _experience = time.time() - _startTime
    _remnant = DEADLINE - _experience
    if _remnant <= 0:
        return False
    return utils.time2dh(_remnant)