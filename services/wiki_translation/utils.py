from wikipediaapi import Wikipedia

def getSummaryForTitles(title):
    #Get the summary of a wikipedia page from title
    summary = Wikipedia().page(title=title).summary

    #Split the summary into sentences are return the list
    return summary.split(". ")
