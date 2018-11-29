import json
import sys
sys.path.append("..\match_gz")
from collections import OrderedDict

from fromdb import FromDB
from tf_idf_model import Similarity


def json_result(input_file):
    """从文件中读取query文本,进行匹配后返回匹配的id.
    
    Arguments:
        input_file {str} -- query文本一个一行
    """                     

    s=Similarity()
    with open(input_file,'r',encoding="utf-8") as fr:
        for line in fr:
            line=line.rstrip()
            teachers_patents=s.send_query(line)
            # print(line,len(line),teachers_patents)
            yield teachers_patents

def id_result(teachers_patents):
    """解析返回的json格式, 返回10个教师id,10个与上面教师相关的专利id和10个和教师无关的专利id
    
    Arguments:
        teachers_patents {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    teachers_patents=json.loads(teachers_patents,object_pairs_hook=OrderedDict)
    teachers=teachers_patents['teacher_results']
    pats=teachers_patents['pat_results']
    
    teachers_vals=teachers.values()
    teacher_ids=[item['t'] for item in teachers_vals]
    teacher_pat_ids=[item['p'] for item in teachers_vals]
    pat_ids=pats.values()
    # print((teacher_ids,teacher_pat_ids),pat_ids)
    return (teacher_ids,teacher_pat_ids),pat_ids

def text_result(teachers,pats):
    """查询数据库，得到相应字段的文本 
        teacher:5个字段
        | 教师id | 专利id | 教师姓名 | 专利标题 | 专利摘要 |

        [948, 911, '王靖岱', '一种烯烃聚合的多区循环反应装置和反应方法', '本发明公开了一种烯烃聚合的多...']

        pat:3个字段
        | 专利id | 专利id | 专利摘要 |

        [46627, '基于机器学习的预取能效优化自适应装置及方法', '本发明公开了一...]
    Arguments:
        teachers {[type]} -- [description]
        pats {[type]} -- [description]
    
    Returns:
        [type] -- shape=(10,10)
    """

    db=FromDB()
    pats=pats
    teacher_ids_text=[]
    pat_ids_text=[]
    for t_id,p_id in zip(teachers[0],teachers[1]):
        df_t_p=db.read_text("SELECT a.idteacher,b.id,a.teacher_name,b.title,b.abs\
            from final a ,t_zheda b WHERE a.idteacher={} AND b.id={} and a.idzd=b.id;".format(t_id,p_id))
        teacher_ids_text.append(df_t_p.values.tolist())
    
    for p_id in pats:
        df_p=db.read_text("SELECT a.id,a.title,a.abs FROM t_zheda a WHERE a.id={};".format(p_id))
        pat_ids_text.append(df_p.values.tolist())
    # print(pat_ids_text[1][0])
    return teacher_ids_text,pat_ids_text

def text2excel():
    pass

def main():
    input_file=r'C:\code\projects\match_gz\test\query.txt'
    for q in json_result(input_file):
        # print(q)
        # print(id_result(q))
        teachers,pats=id_result(q)
        text_result(teachers,pats)

if __name__=="__main__":
    main()