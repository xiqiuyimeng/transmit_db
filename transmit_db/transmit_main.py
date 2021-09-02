# -*- coding: utf-8 -*-
from with_cursor import DictConn
from transmit_type import TransmitType
from transmit import *
_author_ = 'luwt'
_date_ = '2021/9/1 16:42'


@times
def main(source_conn_info, target_conn_info, included_tables=None, included_pattern=None,
         excluded_tables=None, excluded_pattern=None, override=False,
         transmit_type=TransmitType.transmit_table_data, save_insert_sql=False):
    """
    传输数据库的主方法，传入源数据库和目标数据库信息即可完成两个数据库之间的数据传输，
    可以设置指定的表进行传输，同样可以设置排除指定表，同时支持使用正则匹配模式进行指定，
    可以设置传输等级，TransmitType，实现不同的需求.
        为了尽可能的保证效率和数据准确性，
        采用一次导出多条数据，并单条导入的策略，这样可以在某一条数据失败时，不影响其他数据的正常导入
            例如：select * from table limit 0, 1000;
            循环插入：insert into table (id, name) values (1, 'jane');
    :param source_conn_info: 源数据库连接信息，例如：
        source_conn_info = {
            'host': 'localhost',
            'user': 'root',
            "pwd": 'admin',
            'db': 'test'
        }
        值得注意的是，需要指定库名，否则无法直接使用 `show tables;` 查询库下所有的表
    :param target_conn_info: 目标数据库连接信息，同 source_conn_info
    :param included_tables: 指定希望传输的表名集合，数据类型为set，此参数将和 included_pattern 所匹配到的表进行合并，
        以此获取用户所希望传输的表集合
    :param included_pattern: 指定希望传输的表名的正则匹配模式，为了方便指定表名，使用正则进行匹配，
        匹配到的表将与 included_tables 进行合并，以此获取用户所希望传输的表集合
    :param excluded_tables: 指定排除的表，数据类型为set，此参数和 excluded_pattern 所匹配到的表进行合并，
        以此获取用户不希望传输的表集合
    :param excluded_pattern: 指定不希望传输的表名的正则匹配模式，为了方便指定表名，使用正则进行匹配，
        匹配到的表将与 excluded_tables 进行合并，以此获取用户所不希望传输的表集合
    :param override: 是否覆盖，默认 False，如果目标库中已存在当前传输的表，根据此参数判定是否删除原表重新创建
    :param transmit_type: 传输等级，共三级：
        1. only_show_table_names = 1， 只是展示下表名，不做任何实际的传输工作
        2. transmit_table_structure = 2， 将会传输表结构，但不会传输数据
        3. transmit_table_data = 3， 将会执行完整的传输，确认表名 -> 传输表结构 -> 传输表数据
    :param save_insert_sql: 是否保存insert sql语句，默认False，如果设置为True，
        将在当前目录产生一个新的目录，insert_sql/当前日期，并在其下产生相应的sql文件，以表名命名
    """
    if not (check_db(source_conn_info) and check_db(target_conn_info)):
        raise RuntimeError("连接信息中，db不可为空")
    with DictConn(**source_conn_info) as source_conn, DictConn(**target_conn_info) as target_conn:
        transmit_tables = TransmitTableName(source_conn.cursor(),
                                            target_conn.cursor(),
                                            included_tables=included_tables,
                                            included_pattern=included_pattern,
                                            excluded_tables=excluded_tables,
                                            excluded_pattern=excluded_pattern,
                                            override=override)
        need_transmit_tables = transmit_tables.get_need_transmit_tables()
        # 如果 TransmitType 大于只展示表名的等级，且有需要传输的表则继续
        if transmit_type.value > TransmitType.only_show_table_names.value and need_transmit_tables:
            for table in need_transmit_tables:
                # 表结构
                table_structure = TransmitTableStructure(source_conn.cursor(), target_conn.cursor(), table)
                table_structure.main()
                # 如果 TransmitType 大于传输表结构的等级，那么继续传输数据
                if transmit_type.value > TransmitType.transmit_table_structure.value:
                    table_data = TransmitTableData(source_conn.cursor(), target_conn,
                                                   table, save_insert_sql=save_insert_sql)
                    table_data.main()


def check_db(conn_info):
    if conn_info and conn_info.get('db'):
        return True
    return False
