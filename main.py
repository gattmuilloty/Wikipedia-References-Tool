from extractAndParse import *
from exceptions import *

def main():
    wikiPageQuery = input('\nEnter Wikipedia page to query: ')

    userContact = 'mattguilloty@gmail.com'

    df = getWikiReferences(wikiPageQuery, userContact)

    df = fixQuery(df, wikiPageQuery, userContact)

    df = filterReferences(df)

    print('\n' + str(len(df)) + ' bad links found\n')

    for i in range(len(df)):
        print('Reference URL  : ' + df['URL'][i])
        referenceText = getArchiveText(df['URL'][i], 'mattguilloty@gmail.com')
        print('Reference Text : ' + df['reference'][i])
        newReference = remove_sentences_with_words(df['reference'][i], ['Archived', 'Retrieved'])
        cleanedQuery = summarize_text_sumy(newReference).replace('"', '')
        print('Cleaned query  : ' + cleanedQuery)
        print('')
        print('Google Searches found from query:\n')
        searchesFound = googleSearch(cleanedQuery, APIkey = 'AIzaSyCh7g_k2yvQ64SYzybSHaGclZZ7FwIcBKc', CSEid = '224392473af904558')
        searchesFound = [s for s in searchesFound if 'wikipedia' not in s]
        for searchFound in searchesFound:
            response = requests.get(searchFound)

            if response.status_code == 200:

                print(searchFound)
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract the text data
                text_data = soup.get_text()

                text = text_data.replace('\n', '') # Remove line breaks

                print(type(text))

                # Print or process the text data

                if referenceText == 'None':
                    print(cosineSim(df['reference'][i], text))
                else:
                    print(cosineSim(referenceText, text))

        # for found in googleSearch(summarize_text_sumy(df['reference'][i]), 'AIzaSyCh7g_k2yvQ64SYzybSHaGclZZ7FwIcBKc', '224392473af904558'):
        #     print(found)

if __name__ == "__main__":
    main()