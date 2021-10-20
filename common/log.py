#!/usr/bin/python
"""xquant log"""

import os
import logging
import logging.handlers

logger = logging.getLogger('QuantX')
logger.setLevel(logging.DEBUG)

print_switch = False
log_switch = False

def init(path, logname, server_ip=None, server_port=None):
    global logger
    #logpath = os.path.join(os.getcwd(), "log")
    logpath = os.path.join("log")
    if not os.path.exists(logpath):
        os.mkdir(logpath)

    fullpath = os.path.join(logpath, path)
    if not os.path.exists(fullpath):
        os.mkdir(fullpath)

    filename = os.path.join(fullpath, logname)
    logging.basicConfig(level=logging.NOTSET, filename=filename)

    if server_ip != None:
        extra = {'tags':logname}
        handler = logging.handlers.SysLogHandler(address = (server_ip, int(server_port)))
        f = logging.Formatter('%(tags)s: %(message)s')
        handler.setFormatter(f)
        logger.addHandler(handler)
        logger = logging.LoggerAdapter(logger, extra)

def info(info):
    if print_switch:
        print(info)
    if log_switch:
        logger.info(info)

def warning(info):
    if print_switch:
        print(info)
    if log_switch:
        logger.warning(info)

def error(info):
    if print_switch:
        print(info)
    if log_switch:
        logger.error(info)

def critical(info):
    if print_switch:
        print(info)
    if log_switch:
        logger.critical(info)

def debug(info):
    if print_switch:
        print(info)
    if log_switch:
        logger.debug(info)
