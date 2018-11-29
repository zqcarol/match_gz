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
from collections import OrderedDict,defaultdict

class FromDB:
    def __init__(self,host='localhost', port=3306,user='root', passwd='root', db='analysis'):
        self.mysql_cn= MySQLdb.connect(host=host, port=port,user=user, passwd=passwd, db=db)

    def read_all_text(self):
        """将每个教师有关属性的信息
        ['teacher_id','学科','研究方向','研究成果','pat_id','pat1','pat2'...]
        ['teacher_id','pat_ids','pat1','pat2'...]
        Returns:
            dict: 教师和专利之间对应的字典orderdict
            list: 教师所有专利,按照教师的顺序排列.
        """
        df_t_p = pd.read_sql('SELECT a.idteacher,a.idzd,b.abs from final a ,t_zheda b WHERE a.idzd=b.id ORDER BY idteacher;', con=self.mysql_cn)
        # df_teacher=pd.read_sql('select * from t_zheda;', con=self.mysql_cn)   
        self.mysql_cn.close()
        pat_orderby_t=df_t_p['abs'].tolist()
        t_pats=df_t_p[['idteacher','idzd']].values.tolist()
        t_pat_dict=OrderedDict()
        
        for t_pat in t_pats:
            if t_pat[0] not in t_pat_dict:
                t_pat_dict[t_pat[0]]=[t_pat[1]]
            else:
                t_pat_dict[t_pat[0]].append(t_pat[1])

        # print(t_pat_dict,pat_orderby_t)
        return t_pat_dict,pat_orderby_t

# db=FromDB()
# db.read_all_text()

