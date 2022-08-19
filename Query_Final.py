# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 18:51:15 2022

@author: arick
"""

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import json
from math import log

ps = PorterStemmer()
SW = set(nltk.corpus.stopwords.words('english'))


def textprocess(string):
    """function makes text lowercase, splits into tokens, removes punctuation, 
    changes words to root word (stem), and removes stopwords
    and returns new list of strings"""
    processed_text = []
    try:
        lowerized = string.lower()
        tokenized = word_tokenize(lowerized)
        punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
        for t in tokenized:  
            if t in punc:  
                tokenized.remove(t)      
        for token in tokenized:
            stemmized = ps.stem(token)
            if stemmized not in SW:
                processed_text.append(stemmized)    
        return processed_text
    except:
        return processed_text

def get_crawled():
    try:
        crawled_df = pd.read_csv('pubdf.csv')
        ptitles = crawled_df.Processed_Title.tolist()
        p_titles = []
        for t in ptitles:
            lt = eval(t)
            p_titles.append(lt)     
        
        pabstracts = crawled_df.Processed_Abstracts.tolist()
        p_abstracts = []
        for a in pabstracts:
            la = eval(a)
            p_abstracts.append(la) 
        
        #print(p_abstracts)
        return crawled_df, p_titles, p_abstracts
    except:
        print('no data to index')  
        
def open_dict(filename):       
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
            return data
    except:
        print('could not open file')
        return {}
        
def save_dict(dict_, filename):
    try:
        with open(filename, 'w') as json_file:
            json.dump(dict_, json_file)
    except:
        print('could not save file')
        

def query_rank(userinput):
    """inverted index"""
    df, t_list, a_list = get_crawled()
    docdict = open_dict('idf_dict.txt')
    tfdict = open_dict('tf_dict.txt')
    docdict_a = open_dict('idf_dict_abstracts.txt')
    tfdict_a = open_dict('tf_dict_abstracts.txt')
    
    query = textprocess(userinput)
    N = len(df)
    print('N:',N)
    
    # Get ALL terms
    docs_with_terms = []
    for term in query:
        if term in docdict.keys():
            for doc in docdict[term]:
                docs_with_terms.append(doc)
        if term in docdict_a.keys():
            for doc in docdict_a[term]:
                docs_with_terms.append(doc)
    
    #change to set to eliminate duplicates, then create dictionary with docs as keys
    dwt_set = set(docs_with_terms)
    doc_score_dict = dict.fromkeys(dwt_set)

    #TF-IDF for Titles
    for d in dwt_set:
        title_score = []
        for term in query:
            try:
                loc = docdict[term].index(d)
                tf = tfdict[term][loc]
                dft = len(docdict[term])
                idf = log((N/dft),10)
                tfidf = tf*idf
                if tfidf == None:
                    title_score.append(0)
                else:   
                    title_score.append(tfidf)
            except:
                continue
        doc_score_dict[d] = [sum(title_score)]
    #TF-IDF for Abstracts        
    for d in dwt_set:
        abstract_score = []
        for term in query:
            try:
                loc = docdict_a[term].index(d)
                tf = tfdict_a[term][loc]
                dft = len(docdict_a[term])
                idf = log((N/dft),10)
                tfidf = tf*idf
                if tfidf == None:
                    abstract_score.append(0)
                else:   
                    abstract_score.append(tfidf)
            except:
                continue
        doc_score_dict[d].append(sum(abstract_score))
            
        
    dsd_df = pd.DataFrame.from_dict(doc_score_dict,orient='index',columns=['title_score', 'abstract_score'])
    
    dsd_df = dsd_df.sort_values(['abstract_score', 'title_score'],ascending=False)
    print('dsd_df',dsd_df)
    print('RESULTS:')
    nn = 1
    for index, row in dsd_df.head(10).iterrows():
        print(nn,'.')
        print(df['Title'].iloc[index])
        print(df['Publication'].iloc[index])
        print('*****')
        nn += 1


#query_rank('sleep apnea detection')
            
     
 



