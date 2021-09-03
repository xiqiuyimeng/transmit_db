### transmit_db
用来进行数据库数据传输的脚本工具，实现两个数据库之间的数据传输
1. 项目由python语言编写，项目依赖：
   ```bash 
   python3
   loguru==0.5.3
   PyMySQL==1.0.2
   ```
   可以使用 `pip install -r requirements`安装依赖，也可以手动安装上述依赖
2. 实现原理：从源数据库查询表结构，在目标数据库中创建表，从源数据库中查询多条数据，在目标数据库中循环插入
3. 安装到本地类库：
   1. setup: 在 setup.py 同级目录下执行，`python setup.py install`
   2. wheel: 在 setup.py 同级目录下执行，`python setup.py bdist_wheel && pip install dist/*.whl`
   3. 下载whl安装，或`pip install transmitDB`
4. 使用方法：
   ```python
   # 导入 transmit_db
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
   
   # console output >>>
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.util: count_time: 46 - 开始时间为：2021-09-03 15:33:31.511569
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.transmit_func: get_need_transmit_tables: 91 - 将传输 1 个表：{'user'}
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.transmit_func: main: 125 - 导入表 user 结构开始
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.transmit_func: main: 128 - 导入表 user 结构成功
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.transmit_func: main: 216 - 表 user的总条数1，全部执行
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.transmit_func: to_target: 175 - 表 user 1 执行成功
   # 2021-09-03 15:33:31 | INFO     | MainThread   | transmit_db.util: count_time: 53 - 结束时间：2021-09-03 15:33:31.610132，耗时0:00:00.098563
   
   # 同样的可以在 log 目录下查看日志信息，日志文件中记录的将更加详细。
   ```
5. 核心参数说明：
   - included_tables: 集合类型，可以指定具体表名，这些表将被传输
   - included_pattern: 用来指定一个正则匹配模式，符合该模式的表名将被传输，如果 included_tables 也指定，两者会做并集，传输这些表
   - excluded_tables: 集合类型，可以指定具体表名，这些表将被跳过
   - excluded_pattern: 用来指定一个正则匹配模式，符合该模式的表名将被跳过，如果 excluded_tables 也指定，两者做并集，跳过这些表
   - override: 是否覆盖目标库中已存在的表，默认False
   - transmit_type: 传输等级
     - only_show_table_names = 1， 只是展示下表名，不做任何实际的传输工作
     - transmit_table_structure = 2， 将会传输表结构，但不会传输数据
     - transmit_table_data = 3， 将会执行完整的传输，确认表名 -> 传输表结构 -> 传输表数据
   - save_insert_sql: 是否保存 insert sql 语句，默认为 False。如果设置为 True，将在当前目录产生一个新的目录，insert_sql/当前日期，并在其下产生相应的sql文件，以表名命名
   - do_insert: 如果不想真正执行数据库数据插入操作，可以修改此选项，默认为 True。可以同时设置 save_insert_sql=True 和 do_insert=False，这样可以查看生成的sql是否有误，手动执行sql
