# -*- coding: utf-8 -*-
import sys
import os
from loguru import logger
from datetime import datetime
_author_ = 'luwt'
_date_ = '2021/8/27 11:11'


# 移除原本的控制台输出样式
logger.remove()
log_format = (
    '<g>{time:YYYY-MM-DD HH:mm:ss}</g> '
    '| <level>{level: <8}</level> '
    '| <e>{thread.name: <12}</e> '
    '| <cyan>{name}</cyan>: <cyan>{function}</cyan>: <cyan>{line}</cyan> '
    '- <level>{message}</level>'
)

# 定义新的控制台输出样式
logger.add(sys.stderr, format=log_format, level="INFO")


log_dir = f'log/{datetime.now().strftime("%Y-%m-%d")}'
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

log_filename = f"{log_dir}/transmit.log"
error_log_filename = f"{log_dir}/transmit-error.log"
# 定义日志文件输出样式
logger.add(
    log_filename,
    format=log_format,
    level="DEBUG",
    rotation="100mb",
)
# 定义错误日志文件输出样式
logger.add(
    error_log_filename,
    format=log_format,
    level="ERROR",
    rotation="10mb"
)
