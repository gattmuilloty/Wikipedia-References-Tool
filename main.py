from extractAndParse import *
from exceptions import *

def main():
    wikiPageQuery = input('\nEnter Wikipedia page to query: ')

    userContact = 'mattguilloty@gmail.com'

    df = getWikiReferences(wikiPageQuery, userContact)

    df = fixQuery(df, wikiPageQuery, userContact)

    df = filterReferences(df)

    print(df)

if __name__ == "__main__":
    main()