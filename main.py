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

    totalURLsFound = len(df)

    df = filterReferences(df)

    if len(df) == 1:
        print('\n' + str(len(df)) + ' bad link found\n')
    elif len(df) == 0:
        print('\n0 bad links found\n :)\n')
    else:
        print('\n' + str(len(df)) + ' bad links found\n')

    totalBadLinksFound = len(df)

    
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

    for i in range(len(df)):
        print('-----------------------------------------------\n')
        print('Reference URL : ' + df['URL'][i])
        referenceText = getArchiveText(df['URL'][i], 'mattguilloty@gmail.com')

        if referenceText == 'None':
            print('\n----- Archive text was not found. -----\n')
        else:
            print('\n----- Archive text found! -----\n')

        print('Reference Text : ' + df['reference'][i])

        if remove_sentences_with_words(df['reference'][i], ['Archived', 'Retrieved']) == '':
            newReference = referenceText
        else:
            newReference = remove_sentences_with_words(df['reference'][i], ['Archived', 'Retrieved'])
        cleanedQuery = summarize_text_sumy(newReference).replace('"', '')
        print('Cleaned query  : ' + cleanedQuery)
        print('')
        print('Candidate replacement websites found from query:\n')

        print('-----------------------------------------------\n')

        searchesFound = googleSearch(cleanedQuery, APIkey = 'AIzaSyCh7g_k2yvQ64SYzybSHaGclZZ7FwIcBKc', CSEid = '224392473af904558')
        searchesFound = [s for s in searchesFound if 'wikipedia' not in s and 'pdf' not in s]

        for searchFound in searchesFound:
            try:
                response = requests.get(searchFound)
            except Exception as e:
                continue


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

                text = text_data.replace('\n', '')

                if referenceText == 'None':
                    cosSim.append(cosineSim(df['reference'][i], text))
                    print('Cosine Similarity: '.rjust(22), cosineSim(df['reference'][i], text))

                    jaccardInd.append(jaccardIndex(df['reference'][i], text))
                    print('Jaccard Index: '.rjust(22), jaccardIndex(df['reference'][i], text))

                    levenshteinDis.append(levenshteinDist(df['reference'][i], text))
                    print('Levenshtein Distance: '.rjust(22), levenshteinDist(df['reference'][i], text))

                    euclideanDis.append(euclidean_dist(df['reference'][i], text))
                    print('Euclidean Distance: '.rjust(22), euclidean_dist(df['reference'][i], text))
                else:
                    cosSim.append(cosineSim(referenceText, text))
                    print('Cosine Similarity: '.rjust(22), cosineSim(referenceText, text))

                    jaccardInd.append(jaccardIndex(referenceText, text))
                    print('Jaccard Index: '.rjust(22), jaccardIndex(referenceText, text))

                    levenshteinDis.append(levenshteinDist(referenceText, text))
                    print('Levenshtein Distance: '.rjust(22), levenshteinDist(referenceText, text))

                    euclideanDis.append(euclidean_dist(referenceText, text))
                    print('Euclidean Distance: '.rjust(22), euclidean_dist(referenceText, text))

                

                print('\n-----------------------------------------------\n')

    newDf = pd.DataFrame({
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
