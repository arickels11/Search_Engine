# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:54:00 2022

@author: arick
"""

import pandas as pd
import nltk
from nltk.stem import PorterStemmer
from math import log
from tkinter import Label, Entry, Tk, IntVar, Radiobutton, Button
import webbrowser
from Crawler_Final import textprocess, get_crawled_df, open_dict


ps = PorterStemmer()
SW = set(nltk.corpus.stopwords.words('english'))


def query_rank():
    """calculates tfidf for each word in the query and sorts results on highest values"""
    userinput = u_input.get()
    cat = v0.get()
    df, t_list = get_crawled_df()
    docdict = open_dict('idf_dict.txt')
    tfdict = open_dict('tf_dict.txt')
    docdict_a = open_dict('idf_dict_abstracts.txt')
    tfdict_a = open_dict('tf_dict_abstracts.txt')
    
    query = textprocess(userinput)
    print(query)
    N = len(df)
    
    # Get ALL terms (from titles and abstracts)
    docs_with_terms = []
    for term in query:
        if term in docdict.keys():
            for doc in docdict[term]:
                docs_with_terms.append(doc)
        if term in docdict_a.keys():
            for doc in docdict_a[term]:
                docs_with_terms.append(doc)
    print('docs with terms', docs_with_terms)
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
        #Years
        doc_score_dict[d].append(df.iloc[d]['Pub_Dates'])
    
    
    # if relevance was clicked, sort on tfidf of abstract then title
    # if newest was clicked, sort on year
    dsd_df = pd.DataFrame.from_dict(doc_score_dict,orient='index',columns=['title_score', 'abstract_score', 'Year'])   
    if cat == 1:
        dsd_df = dsd_df.sort_values(['title_score','abstract_score'],ascending=False)
    if cat == 2:
        dsd_df = dsd_df.sort_values(['Year'],ascending=False)
    print(dsd_df)

    nn = 1
    output = []
    titleoutput = []
    yroutput = []
    authoutput = []
    df = df.reset_index()
    for index, row in dsd_df.head(10).iterrows():
        titleoutput.append(df['Title'].iloc[index])
        output.append(df['Publication'].iloc[index])
        yroutput.append(df['Pub_Dates'].iloc[index])
        authoutput.append(df['Cov_Authors'].iloc[index])
        nn += 1
        
    # to clear output on tkinter window when there are < 10 results
    while len(output) < 10:
        output.append('')
        titleoutput.append('')
        authoutput.append('')
        yroutput.append('')
    return output, titleoutput, yroutput, authoutput
        

def callback(url):
   webbrowser.open_new_tab(url)
   
           
def display():
    outlist, titlelist, yrlist, authlist = query_rank()
    i = 0
    for oo in outlist:
        #Title
        title = titlelist[outlist.index(oo)]
        lbl = Label(window, text=title, fg="blue", width=200, anchor='w', cursor="hand2", font=("Times", 14, "underline", "bold"))
        lbl.bind("<Button-1>", lambda e,url=oo: callback(url))
        lbl.grid(row=i,column=0)
        lbl.place(x=100, y=200+(i*25))
        
        #Authors, Year
        yr = yrlist[outlist.index(oo)]
        auths = authlist[outlist.index(oo)]
        lbl = Label(window, text=('Coventry Author(s):' + auths + ' Published in: ' + str(yr)), width=200, anchor='w', font=("Times", 12, "italic"))
        lbl.grid(row=i+1,column=0)
        lbl.place(x=100, y=225+(i*25))
        i += 3
    
# UI - tkinter

window=Tk()
window.geometry("1800x1500+20+40")
window.title('Vertical Search Engine')

labl=Label(window, text="Coventry University - School of Computing, Electronics and Maths Publications",
          fg='red', font=("Helvetica", 16))
labl.place(x=100, y=10)
u_input=Entry(window, text="Enter search here", bg='white',fg='black', bd=10,width=50)
u_input.place(x=100, y=50)
labl=Label(window, text="Sort By:")
labl.place(x=100, y=100)

#button to choose to rank based on relevance (tfidf) or newest first
v0=IntVar()
v0.set(1)
r1=Radiobutton(window, text="Relevance", variable=v0,value=1)
r2=Radiobutton(window, text="Newest", variable=v0,value=2)
r1.place(x=200,y=100)
r2.place(x=300, y=100)

btn=Button(window, text="Search", fg='blue',command=display)
btn.place(x=100, y=140)

label_output = Label(text='SEARCH RESULTS:')
label_output.place(x=100, y=180)
window.mainloop()


