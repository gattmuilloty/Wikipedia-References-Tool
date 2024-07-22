from extractAndParse import getWikiReferences
import pandas as pd
from spellchecker import SpellChecker
import spacy
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

nltk.download('punkt', quiet = True)
nltk.download('stopwords', quiet = True)


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

def summarize_text_sumy(text):
    '''
    Summarize the input text using Sumy.

    Args:
    text (str): The input text to summarize.
    sentence_count (int): The number of sentences to return as the summary.

    Returns:
    str: The summarized text.
    '''
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 2)
    return " ".join(str(sentence) for sentence in summary)

import re
from nltk.tokenize import sent_tokenize

# Ensure you have the necessary nltk data for sentence tokenization
import nltk
nltk.download('punkt', quiet=True)

def remove_sentences_with_words(text, exclude_words):
    """
    Remove sentences containing specific words from the input text.

    Parameters:
    text (str): The input text.
    exclude_words (list): A list of words. Sentences containing any of these words will be removed.

    Returns:
    str: The text with specified sentences removed.
    """
    sentences = sent_tokenize(text)
    filtered_sentences = [
        sentence for sentence in sentences
        if not any(re.search(r'\b' + word + r'\b', sentence, re.IGNORECASE) for word in exclude_words)
    ]
    return " ".join(filtered_sentences)
