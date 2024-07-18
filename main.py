from extractAndParse import *
from exceptions import *
import chardet

def main():
    wikiPageQuery = input('\nEnter Wikipedia page to query: ')

    # userContact = 'mattguilloty@gmail.com'
    userContact = input('\nEnter contact email for User-Agent: ')

    df = getWikiReferences(wikiPageQuery, userContact)

    df = fixQuery(df, wikiPageQuery, userContact)

    df = filterReferences(df)

    if len(df) == 1:
        print('\n' + str(len(df)) + ' bad link found\n')
    elif len(df) == 0:
        print('\n0 bad links found\n :)\n')
    else:
        print('\n' + str(len(df)) + ' bad links found\n')
    


    for i in range(len(df)):
        print('-----------------------------------------------\n')
        print('Reference URL  : ' + df['URL'][i])
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
        print('Cleaned query : ' + cleanedQuery)
        print('')
        print('Google Searches found from query:\n')

        print('-----------------------------------------------\n')

        searchesFound = googleSearch(cleanedQuery, APIkey = 'AIzaSyCh7g_k2yvQ64SYzybSHaGclZZ7FwIcBKc', CSEid = '224392473af904558')
        searchesFound = [s for s in searchesFound if 'wikipedia' or 'pdf' not in s]
        for searchFound in searchesFound:
            response = requests.get(searchFound)

            if response.status_code == 200:
                print(searchFound)

                detected_encoding = chardet.detect(response.content)['encoding']

                if detected_encoding is None:
                    detected_encoding = 'utf-8'

                response = response.content.decode(detected_encoding, errors='replace')

                # Parse the HTML content
                soup = BeautifulSoup(response, 'html.parser')

                # Extract the text data
                text_data = soup.get_text()

                text = text_data.replace('\n', '') # Remove line breaks

                if referenceText == 'None':
                    # print('Reference Archive not found. Similarity measures based on reference text:')
                    # print('Comparison')
                    # print(df['reference'][i])
                    print('Cosine Similarity: ', cosineSim(df['reference'][i], text))
                    print('Jaccard Index: ', jaccard_index(df['reference'][i], text))
                    print('Levenshtein Distance: ', levenshteinDist(df['reference'][i], text))
                    print('Euclidean Distance: ', euclidean_dist(df['reference'][i], text))
                else:
                    # print('Archive text found. Similarity measures based on archive text:')
                    # print('Comparison')
                    # print(referenceText)
                    print('Cosine Similarity: ', cosineSim(referenceText, text))
                    print('Jaccard Index: ', jaccard_index(referenceText, text))
                    print('Levenshtein Distance: ', levenshteinDist(referenceText, text))
                    print('Euclidean Distance: ', euclidean_dist(referenceText, text))

                print('\n-----------------------------------------------\n')
                

if __name__ == "__main__":
    main()
