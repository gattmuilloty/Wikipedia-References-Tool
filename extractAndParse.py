from similarityMeasures import *
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import chardet
import nltk
import pandas as pd
from spellchecker import SpellChecker
import spacy

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

nltk.download('punkt', quiet = True)
nltk.download('stopwords', quiet = True)


def getWikiReferences(pageName, contactEmail):

    '''
    Return the reference section of a Wikipedia page.

    Args:
        pageName (string): The title of the Wikipedia page.
        contactEmail (string): Contact email used in header for page request.

    Returns:
        pandas.DataFrame: A dataframe containing the reference data of the Wikipedia page.
    '''

    # URL for Wikipedia page
    url = 'https://en.wikipedia.org/wiki/' + pageName
    
    # Set User-Agent
    headers = { 'User-Agent': f'Wikipedia Reference Tool ({contactEmail})' }

    # Make request for page
    response = requests.get(url, headers = headers)

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all of the instances of the References container
    spans = soup.find_all('span', class_ = 'reference-text')

    # Get text for each reference
    texts = [span.get_text() for span in spans]

    # Get links for each reference
    links = [[link.get('href') for link in span.find_all('a')] for span in spans]

    # Initialize data frame
    df = pd.DataFrame(links)

    # Insert reference text to data frame
    df.insert(0, 'reference', texts)

    if df.empty:
        return 'Page does not exist!'

    return(df)

def filterReferences(references):

    '''
    Return filtered reference section that only possesses problem URLs 

    Args:
        references (pandas.DataFrame): Data frame with Wikipedia reference data.

    Returns: 
        pandas.DataFrame: A dataframe containing the filtered reference data of the Wikipedia page.
    '''

    # Description dictionary for HTTP status codes
    statusCodes = {
    100: "Continue", 101: "Switching Protocols", 102: "Processing",
    200: "OK", 201: "Created", 202: "Accepted", 203: "Non-Authoritative Information", 204: "No Content", 205: "Reset Content", 206: "Partial Content", 207: "Multi-Status", 208: "Already Reported", 226: "IM Used",
    300: "Multiple Choices", 301: "Moved Permanently", 302: "Found", 303: "See Other", 304: "Not Modified", 305: "Use Proxy", 307: "Temporary Redirect", 308: "Permanent Redirect", 400: "Bad Request",
    401: "Unauthorized", 402: "Payment Required", 403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed", 406: "Not Acceptable", 407: "Proxy Authentication Required", 408: "Request Timeout", 409: "Conflict",
    410: "Gone", 411: "Length Required", 412: "Precondition Failed", 413: "Payload Too Large", 414: "URI Too Long", 415: "Unsupported Media Type", 416: "Range Not Satisfiable", 417: "Expectation Failed", 418: "I'm a teapot", 421: "Misdirected Request", 
    422: "Unprocessable Entity", 423: "Locked", 424: "Failed Dependency", 425: "Too Early", 426: "Upgrade Required", 428: "Precondition Required", 429: "Too Many Requests", 431: "Request Header Fields Too Large", 439: "Application Inactive", 451: "Unavailable For Legal Reasons", 
    500: "Internal Server Error", 501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout", 505: "HTTP Version Not Supported", 506: "Variant Also Negotiates", 507: "Insufficient Storage", 508: "Loop Detected", 510: "Not Extended", 511: "Network Authentication Required",
    'ERR': 'Error'
    }

    referenceText = []
    urls = []
    indexes = []

    # For each reference found
    for index, row in references.iterrows():
        for i in range(len(row)):
            # Ensure that there is a website being referenced
            if 'http' in str(row.iloc[i]):
                referenceText.append(row.iloc[0])
                urls.append(row.iloc[i])
                indexes.append(index)

    # User-Agent to ensure that HTTP status codes received are typical
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_status_code(url):

        '''
        Return the HTTP status code of a given URL.

        Args:
            url (string): A string of the link to a website.

        Returns:
            int OR string: An integer of the HTTP status code for the given URL, or an "ERR" string if the HTTP status code can not be found.            
        '''

        try:
            response = requests.get(url, headers = headers, timeout = 5)
            return response.status_code
        except requests.exceptions.RequestException as e:
            return 'ERR'
    
    statuses = []
    description = []

    # Add 1 to each index for visual purposes
    indexes = [x + 1 for x in indexes]

    totalURLS = len(urls)

    # For each URL found
    for i in range(len(urls)):
        status = get_status_code(urls[i])

        # Try ERROR status again to attempt to retreive HTTP status code
        if status == 'ERR':
            status = get_status_code(urls[i])

        print('URL ' + str(i + 1).rjust(3) + '/' + str(len(urls)) + ' : ' + str(status) + ' - ' + statusCodes[status])

        statuses.append(status)
        description.append(statusCodes[status])

        # To prevent Status 420 codes  
        time.sleep(1)

    references = pd.DataFrame({
        'reference': referenceText,
        'URL': urls,
        'status': statuses,
        'description': description,
        'index': indexes
    })

    # HTTP status codes that the program should ignore
    codesToIgnore = [200, 201, 202, 206]

    # Filter dataframe to only contain problematic HTTP status codes
    references = references[~references['status'].isin(codesToIgnore)]

    return references, totalURLS


def getArchiveText(url, contactEmail):

    '''
    Return a URL's latest archived text.

    Args:
        url (string): The link to a website.
        contactEmail (string): Contact email used in header for page request.

    Returns:
        string: Text from archive or 'None" if archive couldn't be found.

    '''

    # API endpoint
    apiURL = f'http://archive.org/wayback/available?url={url}'

    # Set User-Agent
    headers = { 'User-Agent': f'Wikipedia Reference Tool ({contactEmail})' }

    # Make request for archived site
    content = requests.get(apiURL, headers = headers).json()

    # If an archived snapshot exists
    if content['archived_snapshots']:

        # Get the closest/latest snapshot
        closest = content['archived_snapshots']['closest']

        # If the closest/latest snapshot is available
        if closest['available']:

            # Get the URL for the last snapshot
            closestURL = closest['url']

            # Make request
            content = requests.get(closestURL, headers = headers)

            # Parse HTML
            soup = BeautifulSoup(content.text, 'html.parser')

            # Get text data
            text = soup.get_text()

            # Remove line breaks
            text = text.replace('\n', '')

            return text
        
        else:
            return 'None'
    else:
        return 'None'
    

def googleSearch(query, APIkey, CSEid, numResults = 10):

    '''
    Return search results (links) from query.

    Args:
        query (string): Query for Google search.
        APIkey (string): API key connected to Custom Search API.
        CSEid (string): Programmable Search Engine ID. 
        numResults (int): Max number of search results to return. 

    Returns:
        list: A list of links returned from the query.
    '''

    # API endpoint
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        'key': APIkey,
        'cx': CSEid,
        'q': query,
        'num': numResults
    }

    try:
        # Make request to endpoint
        response = requests.get(url, params = params)

        searchResults = response.json()

        # Get links of results
        links = [item['link'] for item in searchResults.get('items', [])]

    except Exception as e:
        links = []

    return links

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

import nltk
nltk.download('punkt', quiet=True)

def removeSentences(text, exclude_words):
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



def wikipediaReferenceTool(df, query, APIkey, CSEid):

    if len(df) == 1:
        print('\n' + str(len(df)) + ' bad link found\n')
    elif len(df) == 0:
        print('\n0 bad links found\n :)\n')
    else:
        print('\n' + str(len(df)) + ' bad links found\n')

    df = df.reset_index(drop=True)

    urlsToFix = []
    candidateURLs = []
    cosSim = []
    jaccardInd =[]
    levenshteinDis = []
    euclideanDis = []
    referenceTexts = []
    statuses = []
    descriptions = []
    indexes = []
    numCandidates = 0

    # For each reference URL
    for i in range(len(df)):
        print('-----------------------------------------------\n')
        print('Reference URL : ' + df['URL'][i])

        # Get the text from the URL's archive (if available)
        referenceText = getArchiveText(df['URL'][i], 'mattguilloty@gmail.com')

        if referenceText == 'None':
            print('\n----- Archive text was not found. -----\n')
        else:
            print('\n----- Archive text found! -----\n')

        print('Reference Text : ' + df['reference'][i])

        # If the cleaned query returns nothing
        if removeSentences(df['reference'][i], ['Archived', 'Retrieved']) == '':
            newReference = referenceText
        else:
            newReference = removeSentences(df['reference'][i], ['Archived', 'Retrieved'])

        # Remove quotation marks from query
        cleanedQuery = summarize_text_sumy(newReference).replace('"', '')

        print('Cleaned query  : ' + cleanedQuery)
        print('')
        print('Candidate replacement websites found from query:\n')

        print('-----------------------------------------------\n')

        # Make Google searches based on cleaned query
        searchesFound = googleSearch(cleanedQuery, APIkey, CSEid)

        # Remove candidates that reference Wikipedia or are in PDF format
        searchesFound = [s for s in searchesFound if 'wikipedia' not in s and 'pdf' not in s]

        # For each candidate replacement URL found
        for searchFound in searchesFound:
            try:
                response = requests.get(searchFound)
            except Exception as e:
                continue

            # If the candidate URL works
            if response.status_code == 200:
                print(searchFound + '\n')

                urlsToFix.append(df['URL'][i])
                candidateURLs.append(searchFound)
                referenceTexts.append(df['reference'][i])
                statuses.append(df['status'][i])
                descriptions.append(df['description'][i])
                indexes.append(df['index'][i])
                numCandidates += 1

                detected_encoding = chardet.detect(response.content)['encoding']

                if detected_encoding is None:
                    detected_encoding = 'utf-8'

                response = response.content.decode(detected_encoding, errors='replace')

                soup = BeautifulSoup(response, 'html.parser')

                text_data = soup.get_text()

                # Remove line breaks in string
                text = text_data.replace('\n', '')

                if referenceText == 'None':
                    referenceText = df['reference'][i]

                cosSim.append(cosineSim(referenceText, text))
                print('Cosine Similarity: '.rjust(22), cosineSim(referenceText, text))

                jaccardInd.append(jaccardIndex(referenceText, text))
                print('Jaccard Index: '.rjust(22), jaccardIndex(referenceText, text))

                levenshteinDis.append(levenshteinDist(referenceText, text))
                print('Levenshtein Distance: '.rjust(22), levenshteinDist(referenceText, text))

                euclideanDis.append(euclidean_dist(referenceText, text))
                print('Euclidean Distance: '.rjust(22), euclidean_dist(referenceText, text))

                print('\n-----------------------------------------------\n')

    pd.DataFrame({
        'reference_number': indexes,
        'reference': referenceTexts,
        'URL': urlsToFix,
        'status': statuses,
        'description': descriptions,
        'candidate_replacement_url': candidateURLs,
        'cosine_similarity': cosSim,
        'jaccard_index': jaccardInd,
        'levenshtein_distance': levenshteinDis,
        'euclidean_distance': euclideanDis
    }).to_csv('exports/wikipedia_reference_tool_candidate_URLs_' + query + '.csv', index = False)

    return numCandidates

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
