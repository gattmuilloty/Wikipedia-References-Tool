from extractAndParse import *
from exceptions import *

def main():
    wikiPageQuery = input('\nEnter Wikipedia page to query: ')

    userContact = 'mattguilloty@gmail.com'
    # userContact = input('\nEnter contact email for User-Agent: ')

    df = getWikiReferences(wikiPageQuery, userContact)

    df, query = fixQuery(df, wikiPageQuery, userContact)

    df, totalURLsFound = filterReferences(df)

    totalBadLinksFound = len(df)
    
    numCandidates = wikipediaReferenceTool(df, query)

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
