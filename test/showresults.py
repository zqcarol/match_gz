import json
import sys
sys.path.append("..\match_gz")
import linecache
from xlutils.copy import copy as xl_copy
from collections import OrderedDict
import xlwt,xlrd
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

    return teacher_ids_text,pat_ids_text

def text2excel():
    input_file='test\query.txt'
    # print(linecache.getline(input_file, 1))
    query=open(input_file,'r',encoding='utf-8').readlines()
    count=len(query)  #读取文本行数（输入关键字个数）

    workbook = xlwt.Workbook(encoding = 'utf-8')
    xlsheet1 = workbook.add_sheet("teachers",cell_overwrite_ok=True)
    xlsheet2 = workbook.add_sheet("patents",cell_overwrite_ok=True)

    for idx,q in enumerate(json_result(input_file)):
        print(query[idx])
        # print(id_result(q))
        teachers,pats=id_result(q)
        teachers,patents=text_result(teachers,pats)
        # print(teachers)
        # print(teachers[0][0][0])

        

        style = xlwt.XFStyle()  # 初始化样式
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER # 垂直对齐
        alignment.vert = xlwt.Alignment.VERT_CENTER # 水平对齐
        alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT # 自动换行
        style.alignment = alignment
        font = xlwt.Font()
        # font.height = 12 * 20  #12号字体
        font.name = "SimSun"    #宋体
        style.font = font

        xlsheet1.write_merge(0, 0, 0, 6, '说明：')
        xlsheet2.write_merge(0, 0, 0, 4, '说明：')
  
        xlsheet1.write_merge(11*idx+2, 11*idx+11, 0, 0, query[idx].rstrip(),style)
        xlsheet2.write_merge(11*idx+2, 11*idx+11, 0, 0, query[idx].rstrip(),style)

        teachers_head=['query文本','教师id','专利id','教师姓名','专利标题','专利摘要','是否匹配']
        content1=teachers
        # print(content[0][0][1])
        #写excel表头
        headlen1 = len(teachers_head)
        for i in range(headlen1):
            xlsheet1.write(1,i,teachers_head[i],style)
        #写入表内容
        contentRow1 = len(content1) #列表元素个数  = 待写入内容行数   
        for row in range(contentRow1):
            for col in range(headlen1-2):
                xlsheet1.write(11*idx+row+2,col+1,content1[row][0][col],style)
                for i in range(4,headlen1-1):
                    xlsheet1.col(i).width = 256*80
                for k in range(4):
                    xlsheet1.col(k).width = 256*12
                for j in range(2,contentRow1+2):
                    tall_style = xlwt.easyxf('font:height 270')
                    xlsheet1.row(j).set_style(tall_style)
        

        patents_head=['query文本','专利id','专利标题','专利摘要','是否匹配']
        content2=patents 
        #写excel表头
        headlen2 = len(patents_head)
        for i in range(headlen2):
            xlsheet2.write(1,i,patents_head[i],style)
        #写入表内容
        contentRow2 = len(content2) #列表元素个数  = 待写入内容行数
        for row in range(contentRow2):
            for col in range(headlen2-2):
                xlsheet2.write(11*idx+row+2,col+1,content2[row][0][col],style)
                for i in range(2,headlen2-1):
                    xlsheet2.col(i).width = 256*80
                for k in range(2):
                    xlsheet2.col(k).width = 256*12
                for j in range(2,contentRow2+2):
                    tall_style = xlwt.easyxf('font:height 270')
                    xlsheet2.row(j).set_style(tall_style)
    workbook.save(r'F:\\projects\\match_gz\\test\\querytxt2.xls')


       

if __name__=="__main__":
    # main()
    text2excel()