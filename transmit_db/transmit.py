# -*- coding: utf-8 -*-
import math
import os
from util import *
_author_ = 'luwt'
_date_ = '2021/9/1 16:30'


class TransmitTableName:
    """
        传输表名，作为传输表的第一步，获取哪些表需要被传输，并且是否可以覆盖等信息

        参数：
        ----
        source_cursor: 源数据库的连接游标，字典类型游标，用来查询源数据库表信息
        target_cursor: 目标数据库的连接游标，字典类型，用来查询目标数据库表信息，和源数据库对比，也为了检测输入的 included_tables 是否正确
        included_tables: 指定要传输的表名，需要是集合类型，如果存在，则只会传输指定的表名，排除掉需要排除的表
        included_pattern: 指定要传输表名的匹配规则，如果 included_tables 也存在，两者求并集
        excluded_tables: 指定要排除的表名
        excluded_pattern: 指定要排除表名的匹配规则，如果 excluded_tables 存在，两者求并集
        override: 是否覆盖表
     """
    def __init__(self, source_cursor, target_cursor, included_tables=None, included_pattern=None,
                 excluded_tables=None, excluded_pattern=None, override=False):
        self.type_error_msg = "类型错误，不是集合类型！"
        self.included_tables = self.check_type_init('included_tables', included_tables)
        self.included_pattern = included_pattern
        self.excluded_tables = self.check_type_init('excluded_tables', excluded_tables)
        self.excluded_pattern = excluded_pattern
        self.show_table_sql = "show tables;"
        self.source_cursor = source_cursor
        self.target_cursor = target_cursor
        self.override = override

    def check_type_init(self, key, value):
        """检查类型，如果值不存在则初始化"""
        if value:
            if not isinstance(value, set):
                msg = key + self.type_error_msg
                log.error(msg)
                raise TypeError(msg)
            else:
                return value
        else:
            return set()

    def get_target_exists_tables(self):
        """获取目标库已存在的表"""
        tables = get_data(self.target_cursor, self.show_table_sql)
        if tables:
            return set(map(lambda x: list(x.values())[0], tables))

    def set_included_excluded_tables(self, table_names):
        """根据输入的匹配模式匹配到的表，和输入的表集合作并集，重新赋值给 included_tables 和 excluded_tables"""
        included_pattern_tables = get_pattern_matches(table_names, self.included_pattern, 'included_pattern')
        self.included_tables = self.included_tables | included_pattern_tables

        excluded_pattern_tables = get_pattern_matches(table_names, self.excluded_pattern, 'excluded_pattern')
        self.excluded_tables = self.excluded_tables | excluded_pattern_tables

    def get_need_transmit_tables(self):
        """获取需要传输的表"""
        tables = get_data(self.source_cursor, self.show_table_sql)
        if not tables:
            msg = "数据库没有表，无法操作! "
            log.error(msg)
            raise RuntimeError(msg)
        # 第一步，获取源库中所有的表名
        table_names = set(map(lambda x: list(x.values())[0], tables))
        # 第二步，计算 included_tables 和 excluded_tables
        self.set_included_excluded_tables(table_names)

        # 第三步，计算需要操作的表，如果 included_tables 不存在，need_load_tables = 源表总表 - excluded_tables
        need_load_tables = table_names - self.excluded_tables
        # 如果 included_tables 存在，need_load_tables = 源表总表 ∩ included_tables - excluded_tables
        if self.included_tables:
            need_load_tables = self.included_tables & need_load_tables

        # 第四步，计算是否有错误表名，即只存在于输入的集合中，不存在于真实的源表集合中
        error_tables = self.included_tables - table_names
        if error_tables:
            log.warning(f"find {len(error_tables)} error_tables: {error_tables}")

        # 第五步，需要考虑假设目标库有表，是否覆盖
        target_exists_tables = self.get_target_exists_tables()
        # 如果目标库存在表，且不需要覆盖，则排除这些表
        if target_exists_tables and not self.override:
            need_load_tables = need_load_tables - target_exists_tables
            log.info(f"将跳过 {len(target_exists_tables)} 个表：{target_exists_tables}")
        if need_load_tables:
            log.info(f"将传输 {len(need_load_tables)} 个表：{need_load_tables}")
        else:
            log.info("没有需要传输的表！")
        return need_load_tables


class TransmitTableStructure:
    """
        传输表结构，查询源数据库创建表语句，并且在目标库中执行，创建表结构
        参数：
        ----
        source_cursor: 源数据库的连接游标，字典类型，用来查询源数据库表结构信息
        target_cursor: 目标数据库连接游标，用来执行创建表sql语句
        table: 表名
    """
    def __init__(self, source_cursor, target_cursor, table):
        self.create_table_sql = f"show create table {table};"
        self.drop_sql = f"drop table if exists {table};"
        self.source_cursor = source_cursor
        self.target_cursor = target_cursor
        self.table = table

    def load_data(self):
        """读取源表创建语句，去除自增的信息"""
        sql_data = get_data(self.source_cursor, self.create_table_sql)
        source_create_table_sql = sql_data[0].get("Create Table")
        # 去除自增信息
        return re.sub("AUTO_INCREMENT=\\w+ ", "", source_create_table_sql)

    def to_target(self):
        self.target_cursor.execute(self.drop_sql)
        self.target_cursor.execute(self.load_data())

    def main(self):
        log.info(f"导入表 {self.table} 结构开始")
        self.load_data()
        self.to_target()
        log.info(f"导入表 {self.table} 结构成功")


class TransmitTableData:
    """
        传输表数据，查询源表数据，生成插入sql，插入目标库表，为了尽可能的保证效率和数据准确性，
        采用一次导出多条数据，并单条导入的策略，这样可以在某一条数据失败时，不影响其他数据的正常导入
                例如：select * from table limit 0, 1000;
                循环插入：insert into table (id, name) values (1, 'jane');
        参数：
        ----
        source_cursor: 源数据库连接游标，字典类型，用以查询源数据库表数据，生成insert sql
        target_conn: 目标数据库连接，用以执行insert sql来导入数据
        table: 表名
        save_insert_sql: 是否保存 insert sql 语句，默认False，不保存，如需要保存，设置为True，
            将在当前目录产生一个新的目录，insert_sql/当前日期，并在其下产生相应的sql文件，以表名命名
    """
    def __init__(self, source_cursor, target_conn, table, save_insert_sql=False):
        # 每一次执行的数量
        self.limit = 10000
        self.source_cursor = source_cursor
        self.target_conn = target_conn
        self.table = table
        self.save_insert_sql = save_insert_sql

    def load_data(self, offset=0, num=1):
        """从源数据库表读取数据，可设置offset来分批查询，以免数据量过大，产生io传输问题"""
        sql = f'select * from {self.table} limit {offset}, {self.limit};'
        log.debug(f"表 {self.table} {num} 查询sql：{sql}")
        return get_data(self.source_cursor, sql)

    def to_target(self, data, num=1):
        if not data:
            return
        insert_sql_list = self.get_insert_sql_list(data)
        target_cursor = self.target_conn.cursor()
        # 循环执行 insert sql
        for i, insert_sql in enumerate(insert_sql_list, start=1):
            try:
                target_cursor.execute(insert_sql)
            except Exception as e:
                log.info(f"表 {self.table} {num}.{i} 执行失败，跳过")
                log.error(f"表 {self.table} {num}.{i} 执行失败，insert sql is ==> {insert_sql}\n出错信息：{e}")
        log.info(f"表 {self.table} {num} 执行成功")
        # 即使有一些插入失败，也应该提交，保证其他数据可以插入
        self.target_conn.commit()

    def get_insert_sql_list(self, data):
        """拼接insert sql，需要处理一些特殊格式"""
        cols = tuple(map(lambda k: k, data[0].keys()))
        col_str = str(cols).replace("'", '')
        sql_list = list()
        for row in data:
            value = str(tuple(map(lambda v: convert_type(v), row.values())))
            insert_sql = f'insert into {self.table} {col_str} values {value.replace("None", "null")};\n'
            sql_list.append(insert_sql)
        # 调用保存sql方法
        if self.save_insert_sql:
            self.save_sql(sql_list)
        return sql_list

    def save_sql(self, sql_list):
        """保存sql"""
        sql_file = self.get_sql_file()
        with open(sql_file, 'w+', encoding='utf-8') as f:
            f.writelines(sql_list)

    def get_sql_file(self):
        """获取sql文件，如果没有就在当前目录下创建"""
        file_name = f'{self.table}.sql'
        sql_file_dir = f'insert_sql/{datetime.now().strftime("%Y-%m-%d")}'
        if not os.path.isdir(sql_file_dir):
            os.makedirs(sql_file_dir)
        sql_file = os.path.join(sql_file_dir, file_name)
        return sql_file

    def main(self):
        # 统计行数
        count_sql = f'select count(*) from {self.table};'
        row_count = get_data(self.source_cursor, count_sql)[0].get('count(*)')
        if row_count == 0:
            return
        elif row_count <= self.limit:
            # 直接导入
            log.info(f"表 {self.table}的总条数{row_count}，全部执行")
            data = self.load_data()
            self.to_target(data)
        else:
            # 分批导入
            exe_count = math.ceil(row_count / self.limit)
            log.info(f"表 {self.table}的总条数:{row_count}，分{exe_count}批执行")
            offset = 0
            num = 1
            while row_count > 0:
                data = self.load_data(offset, num)
                self.to_target(data, num)
                offset += self.limit
                row_count -= self.limit
                num += 1

