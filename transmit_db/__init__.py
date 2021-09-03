# -*- coding: utf-8 -*-
"""
    transmit_db，用来传输数据库的数据。源码地址：https://github.com/xiqiuyimeng/transmit_db.git
    项目的 python 库依赖：
        loguru==0.5.3
        PyMySQL==1.0.2

    调用 transmit 模块的 transmit 方法，即可实现两个数据库之间的数据传输。
    实现原理为：从源数据库查询表结构，在目标数据库中创建表，从源数据库中查询多条数据，在目标数据库中循环插入.

    example:

    # 导入transmit_db
    import transmit_db

    if __name__ == '__main__':
        # 源数据库连接信息
        conn_info_source = {
            'host': 'localhost',
            'user': 'root',
            "pwd": 'admin',
            'db': 'source'
        }
        # 目标数据库连接信息
        conn_info_target = {
            'host': 'localhost',
            'user': 'root',
            "pwd": 'admin',
            'db': 'target'
        }

        # 调用 transmit 方法，默认会传输所有的表结构和数据
        transmit_db.transmit(conn_info_source, conn_info_target)

        # 如果想指定只传输一部分表，可以指定 included_tables 或 included_pattern
        # included_tables 集合类型，可以指定具体表名，这些表将被传输
        # included_pattern 用来指定一个正则匹配模式，符合该模式的表名将被传输
        # 如果以上两个参数同时指定，将会做并集，并传输这些表

        # 如果想排除某些表，可以指定 excluded_tables 或 excluded_pattern
        # excluded_tables 集合类型，可以指定具体表名，这些表将被跳过
        # excluded_pattern 用来指定一个正则匹配模式，符合该模式的表名将被跳过

        # 如果想覆盖目标库中已存在的表，可以指定 override，默认False

        # 如果不想完全传输，可以设置 transmit_type 传输等级，共分三级（默认为 transmit_table_data）：
        #   1. only_show_table_names = 1， 只是展示下表名，不做任何实际的传输工作
        #   2. transmit_table_structure = 2， 将会传输表结构，但不会传输数据
        #   3. transmit_table_data = 3， 将会执行完整的传输，确认表名 -> 传输表结构 -> 传输表数据

        # 如果想保存sql语句，可以设置 save_insert_sql，默认为 False，设置为 True 后，
        # 将在当前目录产生一个新的目录，insert_sql/当前日期，并在其下产生相应的sql文件，以表名命名

        # 如果不想真正执行数据库数据插入操作，可以设置 do_insert，默认为 True，可以设置为 False，
        # 同时设置 save_insert_sql 为 True，这样可以查看生成的sql是否有误，手动执行sql
"""
from .transmit import transmit
from .transmit_type import TransmitType
_author_ = 'luwt'
_date_ = '2021/9/1 16:27'


__all__ = ['transmit', 'TransmitType']
