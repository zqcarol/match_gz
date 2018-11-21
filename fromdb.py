"""
TODO:
读取数据库
使用pandas连接数据库
关联两张表,
将处理好的结果存入数据库
"""

import pandas as pd
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


class FromDB:
    def __init__(self,host='localhost', port=3306,user='root', passwd='', db='analysis'):
        self.mysql_cn= MySQLdb.connect(host=host, port=port,user=user, passwd=passwd, db=db)

    def read_all_text(self):
        df_patent = pd.read_sql('select app_no,abs from t_zheda;', con=self.mysql_cn)
        # df_teacher=pd.read_sql('select * from t_zheda;', con=self.mysql_cn)   
        self.mysql_cn.close()
        df_patent=df_patent['abs'].fillna('').tolist()
        return df_patent
        # print(df_patent)

db=FromDB()
db.read_all_text()