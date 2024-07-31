# How to run Wikipedia Reference Tool

This program was built using [Python 3.11](https://www.python.org/downloads/). If you encounter any issues running the program, it is recommended to use this version to ensure compatibility.

You will also need all the libraries from the following command:

```bash
pip install requests, beautifulsoup4, pandas, chardet, nltk, sumy, pyspellchecker, spacy, scikit-learn, levenshtein, scipy
```

Finally, you will need the following:

- [Custom Search JSON API](https://developers.google.com/custom-search/v1/overview)
- [Custom Search Engine Identifier](https://programmablesearchengine.google.com/controlpanel/all)

Once you have everything required, run the program by entering the following command in the directory:

```bash
python .\main.py
```

You will then be prompted to enter a Wikipedia article to fix:



You will then be prompted to:
1. Enter your email (for [User Agent](https://developer.mozilla.org/en-US/docs/Glossary/User_agent))
2. Enter your [Search API](https://developers.google.com/custom-search/v1/overview) 
3. Enter your [CSE ID](https://programmablesearchengine.google.com/controlpanel/all)
4. Enter the name of the page you would like to fix

The program will search Wikipedia to see if the article exists and grab the data from the reference section. After, it will begin checking the HTTP status codes for each reference URL. Below is an example output of getting to this point:

![](images/ss1.jpg)

Once all the reference URLs have been checked, the program will begin searching for candidate replacement links per site: 

![](images/ss2.jpg?)

Once the program has searched for all candidate links, the summary will appear at the end:

![](images/ss3.jpg)

In the `exports` folder, a CSV file with the name: 
`wikipedia_reference_tool_candidate_URLs_` + **`ARTICLE_NAME`** will populate. The file looks like:

![](images/ss4.jpg)

The dataframe from the file has the following attributes:

| Atribute | Description |
|----------|----------|
| `reference_number`    | The reference number that has a broken link |
| `reference`    | The text description of the reference   |
| `URL`    | The broken link from the reference   |
| `status`    | The HTTP status code returned from the URL   |
| `description`    | The text description of the HTTP status code   |
| `candidate_replacement_url`    | A potential replacement URL  |
| `cosine_similarity`    | The Cosine Similarity between the archive text/reference description and the text of the candidate site   |
| `jaccard_index`   | The Jaccard Index between the archive text/reference description and the text of the candidate site   |
| `levenshtein_distance`    | The Levenshtein Distance between the archive text/reference description and the text of the candidate site   |
| `euclidean_distance`   | The Euclidean Distance between the archive text/reference description and the text of the candidate site  |

If you are running the program multiple times, it may be better to make changes in `main.py` so you don't have to input your email, API Key, and CSE ID every time:

![](images/ss5.jpg)