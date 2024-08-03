from extractAndParse import *

def main():
    
    userContact = input('\nEnter contact email for User-Agent: ')
    APIkey = input('\nPlease enter Google Custom Search API key: ')
    CSEid = input('\nPlease enter Custom Search Engine ID: ')
    
    wikiPageQuery = input('\nEnter Wikipedia page to query: ')

    df = getWikiReferences(wikiPageQuery, userContact)

    df, query = fixQuery(df, wikiPageQuery, userContact)

    df, totalURLsFound = filterReferences(df)

    totalBadLinksFound = len(df)
    
    numCandidates = wikipediaReferenceTool(df, query, APIkey, CSEid)

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
