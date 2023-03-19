from wikipediaapi import Wikipedia
import nltk

def getSummaryForTitles(title):
    #Download missing files. Only for the first use
    nltk.download('punkt')

    #Get the summary of a wikipedia page from title
    summary = Wikipedia().page(title=title).summary

    #Split the summary into sentences are return the list
    return nltk.sent_tokenize(summary) 
