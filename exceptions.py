from extractAndParse import getWikiReferences
import pandas as pd
from spellchecker import SpellChecker
import spacy


def fixQuery(df, query, userContact):

    '''
    Make attempts to query Wikipedia pages that exist

    Args:
        df (pandas.DataFrame OR string): Returned value from original query.
        query (string): Query for a Wikipedia page that does not exist.
        userContact (string): Contact email used in header for page request.

    Returns:
        pandas.DataFrame: A dataframe containing the reference data of the Wikipedia page.
    '''

    nlp = spacy.load("en_core_web_sm")

    while not isinstance(df, pd.DataFrame):
        if SpellChecker().candidates(query) is not None:
            print('\nError. Wikipedia page does not exist! Did you mean:')
            print(str(SpellChecker().candidates(query)) + '?\n')

        else:
            print('\nWikipedia page could not be found. Please try again.\n')

        query = input('Enter Wikipedia page to query: ')
        df = getWikiReferences(query, userContact)

    query = query.replace(' ', '_')
    
    print('\nWikipedia Page Found!')
    print('URL: https://en.wikipedia.org/wiki/' + query + '\n')

    return(df, query)
