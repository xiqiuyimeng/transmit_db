# -*- coding: utf-8 -*-
import re
from decimal import Decimal
from datetime import timedelta
from datetime import datetime
from .log import logger as log
_author_ = 'luwt'
_date_ = '2021/9/1 16:20'


# 执行策略里，变量必须和convert_type函数的参数名保持一致
need_convert_types = {
    datetime: 'str(value)',
    # decimal 转为字符串形式
    Decimal: 'float(value)',
}


def convert_type(value):
    """将一些特殊类型转换为字符串，避免插入数据库时，参数错误"""
    result = value
    for data_type, deal_strategy in need_convert_types.items():
        if isinstance(value, data_type):
            result = eval(deal_strategy)
            break
    return result


def get_data(cursor, sql):
    cursor.execute(sql)
    return cursor.fetchall()


def get_pattern_matches(table_names, pattern, pattern_name):
    if not pattern:
        return set()
    log.info(f"{pattern_name} pattern is {pattern}")
    result = set(filter(lambda x: re.fullmatch(pattern, x), table_names))
    log.info(f"{pattern_name} match {len(result)} tables: {result}")
    return result


def times(f):
    def count_time(*args, **kw):
        start = datetime.now()
        log.info(f"开始时间为：{start}")
        try:
            f(*args, **kw)
        finally:
            end = datetime.now()
            interval = (end.timestamp() - start.timestamp())
            time_sec = timedelta(seconds=interval)
            log.info(f"结束时间：{end}，耗时{time_sec}")
    return count_time
