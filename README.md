# Search_Engine
This project includes a web crawler, indexer, query function, and user interface using tkinter. 
<br />
<br /> -The web crawler can be run on command or set up in Windows to run every day, week, month, etc.
<br /> -Initial crawl (using Beautiful Soup) is indexed, where information (terms) are stored in two python dictionaries: term frequency (TF) and inverse document frequency (IDF)
<br /> -Additional crawls update index to include new terms or updated values in the tf and idf dictionaries
<br /> -Indexed data (dictionaries) are saved as JSON file
<br /> -Search engine UI receives input from the user(tkinter interface)
<br /> -Query function runs to determine most relevant docs based on TF-IDF score ranking
<br /> -Returns top 10 most relevant documents to user, including links
