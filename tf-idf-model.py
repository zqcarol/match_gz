import os
import tempfile
from gensim import corpora
from collections import defaultdict
from gensim import corpora, models, similarities

import pandas

import string #导入string这个模块
from zhon.hanzi import punctuation

def gen_documents(input_file):
    pd=pandas.read_excel(input_file)
    teacher_names=pd['姓名']
    teachers=teacher_names.tolist()

    except_patents=pd[['学科','研究方向','研究成果','研究领域']]
    except_patents=except_patents.values.tolist()
    except_pats=[]
    id_belong_1=[]
    for idx,pat in enumerate(except_patents):
        id_belong_1+=[idx]*len(pat)
        except_pats.extend(pat)
    except_pats
    patents=pd['专利成果'].fillna('').tolist()
    single_pats=[]
    id_belong_2=[]
    for idx,pats in enumerate(patents):
        for pat in str(pats).split('\n'):
    #         print(pat.split(' ')[2])
            try:
                pat=pat.split(' ')[2]
                if pat:
                    id_belong_2.append(idx)
                    single_pats.append(pat)
            except:
                continue  
    single_pats
    documents=except_pats+single_pats
    ids=id_belong_1+id_belong_2
    ids_dict={i:ids[i] for i in range(len(ids))}
    documents=[[w for w in str(doc)] for doc in documents]
    return documents,ids_dict,teachers

def create_corpus(documents,dictionary_path,corpus_path):
    chars = string.ascii_letters + string.digits+string.punctuation+punctuation
    chars=[item for item in chars]
    stoplist=chars+['\n']
    texts=[[word for word in document if word not in stoplist] for document in documents]
    #去掉只出现一次的词
    frequency=defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] +=1
    texts=[[token for token in text if frequency[token]>1] for text in texts]
    # print(texts)
    dictionary=corpora.Dictionary(texts)
    dictionary.save(dictionary_path)
    #new_vec=dictionary.token2id
    corpus=[dictionary.doc2bow(text) for text in texts]#将文档转换为向量
    corpora.MmCorpus.serialize(corpus_path,corpus)
    return dictionary,corpus

def create_index(dictionary_path,corpus_path,index_path):
    dictionary=corpora.Dictionary.load(dictionary_path)
    corpus=corpora.MmCorpus(corpus_path)
    tf_idf=models.TfidfModel(corpus)
    corpus_tfidf=tf_idf[corpus]
    vec=[vectors for vectors in corpus_tfidf]
    index = similarities.MatrixSimilarity(tf_idf[corpus])
    index.save(index_path)


def similarity(query,ids_dict,dictionary_path,corpus_path,index_path):
    dictionary=corpora.Dictionary.load(dictionary_path)
    corpus=corpora.MmCorpus(corpus_path)
    tf_idf=models.TfidfModel(corpus)

    vec_bow = dictionary.doc2bow(query)
    vec_tfidf = tf_idf[vec_bow] 

    index=similarities.MatrixSimilarity.load(index_path)
    sims=index[vec_tfidf]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    teacher_score=defaultdict(lambda :0)
    for doc in sims:
        teacher_score[ids_dict[doc[0]]]+=doc[1]
    print(teacher_score)

class Similarity:
    def __init__(self,ids_dict,dictionary_path,corpus_path,index_path):
        self.ids_dict=ids_dict
        self.dictionary=corpora.Dictionary.load(dictionary_path)
        self.corpus=corpora.MmCorpus(corpus_path)
        self.tf_idf=models.TfidfModel(self.corpus)
        self.index=similarities.MatrixSimilarity.load(index_path)

    def send_query(self,query):
        vec_bow = self.dictionary.doc2bow(query)
        vec_tfidf = self.tf_idf[vec_bow] # convert the query to LSI space 
        sims=self.index[vec_tfidf]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        teacher_score=defaultdict(lambda :[])
        for doc in sims:
            teacher_score[self.ids_dict[doc[0]]].append(doc)
        # print(teacher_score)
        score={k:sum([item[1] for item in teacher_score[k]]) for k in teacher_score}
        return score,teacher_score


def demo(query):
    input_file="datasets/浙大教授样例.xlsx"
    dictionary_path='datasets/teachers.dict'
    corpus_path='datasets/teachers.mm'
    index_path='datasets/teachers.index'
    documents,ids_dict,teachers=gen_documents(input_file)

    create_corpus(documents,dictionary_path,corpus_path)

    create_index(dictionary_path,corpus_path,index_path)
    # query = ['数','据','挖','掘']
    query=[item for item in "人工智能"]
    # similarity(query,ids_dict,dictionary_path,corpus_path,index_path)

    q=Similarity(ids_dict,dictionary_path,corpus_path,index_path)
    q.send_query(query)

def main():
    input_file="datasets/浙大教授样例.xlsx"
    dictionary_path='datasets/teachers.dict'
    corpus_path='datasets/teachers.mm'
    index_path='datasets/teachers.index'
    documents,ids_dict,teachers=gen_documents(input_file)

    create_corpus(documents,dictionary_path,corpus_path)

    create_index(dictionary_path,corpus_path,index_path)
    # query = ['数','据','挖','掘']
    query=[item for item in "大数据分析"]
    # similarity(query,ids_dict,dictionary_path,corpus_path,index_path)

    q=Similarity(ids_dict,dictionary_path,corpus_path,index_path)
    results,pat_sort=q.send_query(query)
    # print(results)
    for teacher_id in results:
        print(teachers[teacher_id],results[teacher_id],pat_sort[teacher_id])




if __name__ == '__main__':
    main()