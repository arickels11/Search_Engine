# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 13:09:12 2022

@author: arick
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 15:17:47 2022

@author: arick
"""

from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import json

ps = PorterStemmer()
SW = set(nltk.corpus.stopwords.words('english'))

def textprocess(string):
    """This makes text lowercase, splits into tokens, removes punctuation, 
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
    
    
def get_authors(url, headers):
    auths = []
    page = requests.get(url, headers=headers)
    authsoup = BeautifulSoup(page.text, "html.parser") 
    authors = authsoup.find_all("a", class_="link person")
    try:
        for auth in authors:
            auths.append(auth.string)
        return auths
    except:
        return []
    #time.sleep(1)

def get_a_links(url, headers):
    authlinks = []
    page = requests.get(url, headers=headers)
    authsoup = BeautifulSoup(page.text, "html.parser") 
    authors = authsoup.find_all("a", class_="link person")
    try:
        for auth in authors:
            authlinks.append(auth.get('href'))
        return authlinks
    except:
        return []
    #time.sleep(1)
    
     
      
def get_abstract(url, headers):
    page = requests.get(url, headers=headers)
    abssoup = BeautifulSoup(page.text, "html.parser") 
    abstract = abssoup.find("div", class_="textblock")
    try:
        return textprocess(abstract.text)
    except:
        return []
    #time.sleep(1)
    
def append_q(pubtitles, publications, pubyears, headers):
    new_titles = pubtitles
    new_pubs = publications
    new_dates = pubyears
    
    new_auths = []
    new_a_links = [] 
    new_abstracts = []
    new_p_titles = []
      
    for l in publications:
        new_auths.append(get_authors(l, headers))
        new_a_links.append(get_a_links(l, headers))
        new_abstracts.append(get_abstract(l, headers))        
        
        # added tokenized author names to end of abstract for search engine
        for a in new_auths[-1]:
            b = textprocess(a)
            for bb in b:
                new_abstracts[-1].append(bb)
        
    for nt in new_titles:
        new_p_titles.append(textprocess(nt))
    return new_titles, new_pubs, new_dates, new_auths, new_a_links, new_abstracts, new_p_titles

def get_crawled_df():
    """retrieve crawled dictionary so we don't recrawl previously crawled items"""
    
    crawled_df = pd.DataFrame(columns=['Title', 'Publication', 'Cov_Authors',
                                       'Cov_Authors_links','Pub_Dates',
                                       'Processed_Abstracts', 'Processed_Title',
                                       'Cov_Authors_Links'])
    crawled_df = crawled_df.set_index('Title')
    crawled_titles = []
    
    try:
        crawled_df = pd.read_csv('pubdf.csv')
        crawled_df = crawled_df.set_index('Title')
        titles = crawled_df.index.tolist()       
        for t in titles:
            crawled_titles.append(t)  
        
    except:
        print('no dataframe yet')
    
    return crawled_df, crawled_titles


           
def vertcrawl(maxpagenum):
    """Crawls Titles, Pubication Links, and Publication Year for each publication.
    Opens up dictionary of previously crawled items/titles, only crawls new items
    and appends them to the dictionary, then saves updated dictionary.
    
    *** Titles, publication links, and years crawled in this function because
    they are retrieved from the main page, whereas separated independence functions
    for authors, author links, and abstracts are crawled within the publication page"""
    
    crawled_df, crawled_titles  = get_crawled_df()
    headers = {'user-agent' : 'Alexandra Rickels/Coventry University'}
    url = "https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-electronics-and-maths/publications/"
    
    # FIRST PAGE OF PUBLICATIONS
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    
    #Titles
    for t in range(len(crawled_titles)):
        crawled_titles[t] = crawled_titles[t].lower()
        
    tindex = 0
    all_titles = []
    title_index = []
    titles = soup.find_all("h3", class_="title")
    for t in titles:
        if t.text.lower() not in crawled_titles:
            if t.text.lower() not in all_titles:
                all_titles.append(t.text)
                title_index.append(tindex)
        tindex += 1
    #time.sleep(1)
     
    # Publicaton Links             
    all_publinks = []
    pubsite = "https://pureportal.coventry.ac.uk/en/publications/"
    all_publinks_pp = soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['link'])
    pindex = 0
    for l in all_publinks_pp:
        if l.get('href').startswith(pubsite):
            if pindex in title_index:
                all_publinks.append(l.get('href'))
            pindex += 1
    #time.sleep(1)
    #Publication Dates      
    all_dates = []
    date_index = []
    dates = soup.find_all("span", class_="date")
    dindex = 0
    for d in dates:
        yr = d.text[-4:]
        if dindex in title_index:
            all_dates.append(yr)
            date_index.append(dindex)
        dindex += 1
    #time.sleep(1)
        
    
    #LOOP THROUGH REST OF PAGES
    pagenum = 1
    maxpage = maxpagenum
    while pagenum != maxpage:
          site = f"https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-electronics-and-maths/publications/?page={pagenum}"
          page = requests.get(site, headers=headers)
          soup = BeautifulSoup(page.text, "html.parser")
          
          # Titles
          titles = soup.find_all("h3", class_="title")
          for t in titles:
              if t.text.lower() not in crawled_titles:
                  all_titles.append(t.text)
                  title_index.append(tindex)
              tindex += 1
          #time.sleep(1)

          # Publication Links
          all_publinks_pp = soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['link'])
          for l in all_publinks_pp:
              if l.get('href').startswith(pubsite):
                  if pindex in title_index:
                      all_publinks.append(l.get('href'))
                  pindex += 1
          #time.sleep(1)
          
          # Publication Years
          dates = soup.find_all("span", class_="date")
          if len(dates) > 50:
              print('too many dates on page',pagenum)
          errcount = 0
          for d in dates:
              yr = d.text[-4:]
              #index location and count of extra dates
              errorindex = {255: 2}
              if dindex in errorindex and errcount != errorindex[dindex]:
                  errcount += 1
                  print('ignored at index', dindex)                                            
              elif dindex in title_index:
                  all_dates.append(yr)
                  date_index.append(dindex)
                  dindex += 1
                  errcount = 0
              else:
                  dindex += 1
          print('pagenum',pagenum,'completed') 
          #time.sleep(1)
          pagenum += 1

    tt,pp,dd,aa,al,ab,pt = append_q(all_titles,all_publinks,all_dates, headers)
    dict_to_add = {'Title': tt,
               'Publication': pp,      
               'Cov_Authors': aa,
               'Cov_Authors_Links': al,
               'Pub_Dates': dd,
               'Processed_Abstracts':ab,
               'Processed_Title':pt} 
    
    newly_crawled = pd.DataFrame(dict_to_add)
    newly_crawled = newly_crawled.set_index('Title')
    #removes pubs which don't have an author that is linked in Coventry CEM staff
    newdf = newly_crawled[newly_crawled.astype(str)['Cov_Authors'] != '[]'] 
    crawled_df_updated = pd.concat([crawled_df, newdf], join='outer', sort=False)
    crawled_df_updated.to_csv('pubdf.csv')
    
    print('new publications crawled:',len(newdf),'total publications in db:',len(crawled_df_updated))
      

#Indexer

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
        
def get_crawled_index():
    """retrieve crawled dictionary so we don't recrawl previously crawled items"""

    p_titles = []
    p_abstracts = []
    
    try:
        crawled_df = pd.read_csv('pubdf.csv')
        
        ptitles = crawled_df.Processed_Title.tolist()
        for t in ptitles:
            lt = eval(t)
            p_titles.append(lt)     
        
        pabstracts = crawled_df.Processed_Abstracts.tolist()
        for a in pabstracts:
            la = eval(a)
            p_abstracts.append(la) 
    except:
        print('no dataframe yet')
    
    return crawled_df, p_titles, p_abstracts



def inverted_index():
    """inverted index and tf's for titles and abstracts"""
    df, t_list, a_list = get_crawled_index()
    
    #TITLE DICTIONARY
    # open current index and TF dictionaries
    docdict = open_dict('idf_dict.txt')
    tfdict = open_dict('tf_dict.txt')
    
    # identify what terms are already indexed
    prev_indexed = []
    for dd in docdict.values():
        for ddd in dd:
            if ddd not in prev_indexed:
                prev_indexed.append(ddd)
 
    # add new terms (if not already in index dict)
    wd_idf = docdict
    wd_tf = tfdict
    for t in t_list:
        for w in t:
            if w not in wd_idf.keys():
                wd_idf[w] = []
                wd_tf[w] = []
    
    # then loop through titles, if new, append Index dict value
    # with doc (doc index)
    # and TF dict value with term frequency (count)
    docid = 0
    for t in t_list:
        if docid not in prev_indexed:
            w_in_t = []
            for w in t:                          
                if w not in w_in_t:
                    wd_idf[w].append(docid)
                    wd_tf[w].append(1)
                else:              
                    wd_tf[w][-1] = wd_tf[w][-1] + 1
                w_in_t.append(w)
        docid += 1
    
    # save new index and TF dicts as JSONs
    save_dict(wd_idf, 'idf_dict.txt')
    save_dict(wd_tf, 'tf_dict.txt')
        
        
    #ABSTRACT DICTIONARY   
    docdict_a = open_dict('idf_dict_abstracts.txt')
    tfdict_a = open_dict('tf_dict_abstracts.txt')
    prev_indexed_a = []
    for dd in docdict_a.values():
        for ddd in dd:
            if ddd not in prev_indexed_a:
                prev_indexed_a.append(ddd)
        
    #first gather all the words and add as keys to dict
    wd_idf_a = docdict_a
    wd_tf_a = tfdict_a
    for a in a_list:
        for w in a:
            if w not in wd_idf_a.keys():
                wd_idf_a[w] = []
                wd_tf_a[w] = []
    
    #then loop through titles and append with word counts
    docid = 0  
    for a in a_list:
        if docid not in prev_indexed_a:
            w_in_a = []
            for w in a:                          
                if w not in w_in_a:
                    wd_idf_a[w].append(docid)
                    wd_tf_a[w].append(1)
                else:              
                    wd_tf_a[w][-1] = wd_tf_a[w][-1] + 1
                w_in_a.append(w)
        docid += 1
        
    save_dict(wd_idf_a, 'idf_dict_abstracts.txt')
    save_dict(wd_tf_a, 'tf_dict_abstracts.txt')





        


