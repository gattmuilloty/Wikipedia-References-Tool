# Library requirements
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def getWikiReferences(pageName, contactEmail):

    '''
    Return the reference section of a Wikipedia page.

    Args:
        pageName (string): The title of the Wikipedia page.
        contactEmail (string): Contact email used in header for page request.

    Returns:
        pandas.DataFrame: A dataframe containing the reference data of the Wikipedia page.
    '''

    url = 'https://en.wikipedia.org/wiki/' + pageName # URL for Wikipedia page
    
    headers = { 'User-Agent': f'DASC 690 - Summer 2024 ({contactEmail})' } # Set User-Agent

    response = requests.get(url, headers = headers) # Make request for page

    soup = BeautifulSoup(response.text, 'html.parser') # Parse HTML

    spans = soup.find_all('span', class_ = 'reference-text') # Find all of the instances of the References container

    texts = [span.get_text() for span in spans] # Get text for each reference

    links = [[link.get('href') for link in span.find_all('a')] for span in spans] # Get links for each reference

    df = pd.DataFrame(links) # Initialize data frame

    df.insert(0, 'reference', texts) # Insert reference text to data frame

    if df.empty:
        return 'Page does not exist!'

    return(df)


def getArchiveText(url, contactEmail):

    '''
    Return a URL's latest archived text.

    Args:
        url (string): The link to a website.
        contactEmail (string): Contact email used in header for page request.

    Returns:
        string: Text from archive or 'None" if archive couldn't be found.

    '''

    apiURL = f'http://archive.org/wayback/available?url={url}' # API endpoint

    headers = { 'User-Agent': f'DASC 690 - Summer 2024 ({contactEmail})' } # Set User-Agent

    content = requests.get(apiURL, headers = headers).json() # Make request for archived site

    if content['archived_snapshots']: # If an archived snapshot exists

        closest = content['archived_snapshots']['closest'] # Get the closest/latest snapshot

        if closest['available']: # If the closest/latest snapshot is available

            closestURL = closest['url'] # Get the URL for the last snapshot

            content = requests.get(closestURL, headers = headers) # Make request

            soup = BeautifulSoup(content.text, 'html.parser') # Parse HTML

            text = soup.get_text() # Get text data

            text = text.replace('\n', '') # Remove line breaks

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

    url = "https://www.googleapis.com/customsearch/v1" # API endpoint

    params = {
        'key': APIkey,
        'cx': CSEid,
        'q': query,
        'num': numResults
    }

    response = requests.get(url, params = params) # Make request to endpoint

    searchResults = response.json()

    links = [item['link'] for item in searchResults.get('items', [])] # Get links of results

    return links


def filterReferences(references):

    '''
    Return filtered reference section that only possesses problem URLs 

    Args:
        references (pandas.DataFrame): Data frame with Wikipedia reference data.

    Returns: 
        pandas.DataFrame: A dataframe containing the filtered reference data of the Wikipedia page.
    '''

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

    for index, row in references.iterrows():
        for i in range(len(row)):
            if 'http' in str(row.iloc[i]):
                referenceText.append(row.iloc[0])
                urls.append(row.iloc[i])

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_status_code(url):
        try:
            response = requests.get(url, headers = headers, timeout = 5)
            return response.status_code
        except requests.exceptions.RequestException as e:
            return 'ERR'
    
    statuses = []
    description = []

    for i in range(len(urls)):
        status = get_status_code(urls[i])

        print('URL ' + str(i + 1).rjust(3) + '/' + str(len(urls)) + ' : ' + str(status) + ' - ' + statusCodes[status])

        statuses.append(status)
        description.append(statusCodes[status])

        time.sleep(1)

    references = pd.DataFrame({
        'reference': referenceText,
        'URL': urls,
        'status': statuses,
        'description': description
    })

    codesToIgnore = [200, 201, 202, 206]

    references = references[~references['status'].isin(codesToIgnore)].reset_index(drop=True)

    return(references)


def cosineSim(text1, text2):
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0][1]