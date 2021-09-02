# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
from transmit_main import main
_author_ = 'luwt'
_date_ = '2021/9/2 18:05'


if __name__ == '__main__':
    conn_info_local = {
        'host': 'localhost',
        'user': 'root',
        "pwd": 'admin',
        'db': 'test'
    }
    conn_info_local_test = {
        'host': 'localhost',
        'user': 'root',
        "pwd": 'admin',
        'db': 'test2'
    }
    main(conn_info_local, conn_info_local_test, included_tables={"user"})



