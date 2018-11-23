import os
import tempfile
import json
from collections import defaultdict,OrderedDict

from gensim import corpora
from gensim import corpora, models, similarities
import pandas
import string 
from zhon.hanzi import punctuation

import fromdb


def gen_documents(t_pat_path):
    
    """从数据源读取数据，并返回一个列表，每一个元素表示一篇文章.
    
    Returns:
        list: tokenizer后的文本.
    """

    db=fromdb.FromDB()
    t_pat_dict,documents=db.read_all_text()
    with open(t_pat_path,'w') as f:
        json.dump(t_pat_dict,f)
    documents=[[w for w in str(doc)] for doc in documents]
    return documents

def create_corpus(documents,dictionary_path,corpus_path):
    """
    去掉停用词和只出现一次的词.
    """
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
    """创建相似度检索模型
    Args:
        dictionary_path ([type]): [字典存放位置]
        corpus_path ([type]): [语料库存放位置]
        index_path ([type]): [保存的检索模型位置]
    """
    dictionary=corpora.Dictionary.load(dictionary_path)
    corpus=corpora.MmCorpus(corpus_path)
    tf_idf=models.TfidfModel(corpus)
    index = similarities.MatrixSimilarity(tf_idf[corpus])
    index.save(index_path)



class Similarity:
    """基于相似度的匹配
    
    Returns:
        list: 每个老师的最终得分，和该老师下每个专利的得分.
    """

    def __init__(self,t_pat_path='data/t_pat_dict.json',dictionary_path='data/teachers.dict'\
	,corpus_path='data/teachers.mm',index_path='data/teachers.index'):
        with open(t_pat_path,'r') as f:
            self.t_pat_dict=json.load(f)
        self.t_pat_num=OrderedDict()
        self.t_pat_num={k:len(self.t_pat_dict[k]) for k in self.t_pat_dict}
        self.dictionary=corpora.Dictionary.load(dictionary_path)
        self.corpus=corpora.MmCorpus(corpus_path)
        self.tf_idf=models.TfidfModel(self.corpus)
        self.index=similarities.MatrixSimilarity.load(index_path)
        self.teachers=list(self.t_pat_num.keys())
        self.pat_nums=self.t_pat_num.values()

    def send_query(self,query,k=10):
        """给定query文本，返回k个与之最匹配的教师和该教师拥有的与之最匹配的专利编号
        
        Args:
            query (str): query文本
            k (int, optional): Defaults to 10. 选择最匹配的k个教师
        
        Returns:
            list: 包含十个最匹配的老师，每个老师用一个列表表示他的编号和最匹配专利编号
        """

        query=[item for item in query]
        vec_bow = self.dictionary.doc2bow(query)
        vec_tfidf = self.tf_idf[vec_bow]
        sims=self.index[vec_tfidf]
        sim_len=len(sims)
        new_sim_sum=[]
        new_sim=defaultdict(lambda :[])

        # 累计每个教师专利的得分
        i=0
        while i<sim_len:
            for j,num in enumerate(self.pat_nums):
                sum_tmp=0
                for _ in range(int(num)):
                    new_sim[self.teachers[j]].append(sims[i])
                    sum_tmp+=sims[i]
                    i+=1
                new_sim_sum.append(sum_tmp)

        # 按匹配得分排序
        new_sim_sum=[(t,score) for t,score in zip(self.teachers,new_sim_sum)]
        new_sim_sum = sorted(new_sim_sum, key=lambda item: -item[1])
        new_sim_sum_k=new_sim_sum[:10]

        # 返回得分最高的教师和该教师得分最高的专利
        results=[]
        for t in new_sim_sum_k:
            pats=self.t_pat_dict[t[0]]# 专利编号
            results.append([t[0],str(max(zip(pats,new_sim[t[0]]),key=lambda item: item[1])[0])])

        print(results)
        return results
	

def main():
    dictionary_path='data/teachers.dict'
    corpus_path='data/teachers.mm'
    index_path='data/teachers.index'
    t_pat_path='data/t_pat_dict.json'

    documents=gen_documents(t_pat_path)
    create_corpus(documents,dictionary_path,corpus_path)
    create_index(dictionary_path,corpus_path,index_path)


    s=Similarity(t_pat_path,dictionary_path,corpus_path,index_path)
    s.send_query('人工智能')


if __name__ == '__main__':
    main()
