import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


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
    headers = { 'User-Agent': f'DASC 690 - Summer 2024 ({contactEmail})' }

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
    headers = { 'User-Agent': f'DASC 690 - Summer 2024 ({contactEmail})' }

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