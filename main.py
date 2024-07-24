from extractAndParse import *
from exceptions import *
from similarityMeasures import *
import chardet

def main():
    wikiPageQuery = input('\nEnter Wikipedia page to query: ')

    userContact = 'mattguilloty@gmail.com'
    # userContact = input('\nEnter contact email for User-Agent: ')

    df = getWikiReferences(wikiPageQuery, userContact)

    df, query = fixQuery(df, wikiPageQuery, userContact)

    df, totalURLsFound = filterReferences(df)

    totalBadLinksFound = len(df)

    def wumbo(df):

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
            searchesFound = googleSearch(cleanedQuery, APIkey = 'AIzaSyCh7g_k2yvQ64SYzybSHaGclZZ7FwIcBKc', CSEid = '224392473af904558')

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
    
    numCandidates = wumbo(df)

    print('*** Wikipedia Page Reference Tool is complete! ***\n')

    print('                      SUMMARY:                    ')
    print('--------------------------------------------------')
    print('Number of Websites Checked: ' + str(totalURLsFound))
    print('Number of Bad Links Found: ' + str(totalBadLinksFound))
    print('Number of Candidate Replacement Sites Found: ' + str(numCandidates))

    print('\nCandidate replacement sites can be found in:')
    print('exports/wikipedia_reference_tool_candidate_URLs_' + query + '.csv\n')


if __name__ == "__main__":
    main()
