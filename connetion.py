from datetime import datetime

import pymysql


try:
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='marykay_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    print('True')
except Exception as e:
    print('False')
    print(e)