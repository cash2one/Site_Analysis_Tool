#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Time-stamp: <2014-01-07 17:20:11 Tuesday by zhangguhua>

# @version 1.0
# @author zhangguhua

 #!/usr/bin/python
  # coding: utf-8

import logging.handlers
from logging import *
import os
import sys
class zgh_logger():
    path = os.path.dirname(os.path.abspath(__file__))
    log_file_name = path + '/../log/mining.log'

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_handle = logging.handlers.TimedRotatingFileHandler(log_file_name, 'H')
    fmt = logging.Formatter("%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s (levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    log_handle.setFormatter(fmt)
    logger.addHandler(log_handle)


    debug = logger.debug
    info = logger.info
    warning = logger.warn
    error = logger.error
    critical = logger.critical
