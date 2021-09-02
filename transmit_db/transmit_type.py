# -*- coding: utf-8 -*-
from enum import Enum
_author_ = 'luwt'
_date_ = '2021/9/1 16:54'


class TransmitType(Enum):
    # 只展示表名不做任何实际的传输
    only_show_table_names = 1
    # 传输表结构，但不传输表数据
    transmit_table_structure = 2
    # 传输表结构和数据
    transmit_table_data = 3
