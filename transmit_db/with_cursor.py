# -*- coding: utf-8 -*-
import pymysql
from transmit_db.log import logger as log
_author_ = 'luwt'
_date_ = '2020/7/29 10:58'


class DictConn:

    def __init__(self, host, user, pwd, db, port=3306, charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.charset = charset
        self.db = db
        self.conn = self.get_mysql_conn()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self.conn

    def get_mysql_conn(self):
        """打开数据库连接（ip/数据库用户名/登录密码/数据库名/编码）"""
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                passwd=self.pwd,
                db=self.db,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            log.debug("获取数据库连接成功")
            return conn
        except Exception as e:
            log.error("获取数据连接失败", e)
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
            log.error(f"exception type:{exc_type}")
            log.error(f"exception value:{exc_val}")
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
        log.debug("成功关闭数据库连接")


class DictCursor(DictConn):

    def __enter__(self):
        return super().__enter__().cursor()

