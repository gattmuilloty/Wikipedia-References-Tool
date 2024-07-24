from sklearn.feature_extraction.text import CountVectorizer # For cosine similarity and euclidean distance
from sklearn.metrics.pairwise import cosine_similarity # For cosine similarity
import Levenshtein # For levenshtein distance
from scipy.spatial import distance # For euclidean Distance


def cosineSim(text1, text2):

    '''
    Return the cosine similarity between two strings.

    Args:
        text1 (string): The first piece of text for comparison.
        text2 (string): The second piece of text for comparison.

    Returns:
        numpy.float64: A float ranging from 0 to 1 determining the cosine similarity between the two strings.
    '''

    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()

    return cosine_similarity(vectors)[0][1]


def jaccardIndex(text1, text2):

    '''
    Return the Jaccard index between two strings.

    Args:
        text1 (string): The first piece of text for comparison.
        text2 (string): The second piece of text for comparison.

    Returns:
        float: A float ranging from 0 to 1 determining the Jaccard index between the two strings.
    '''

    set1 = set(text1.split())
    set2 = set(text2.split())

    return len(set1.intersection(set2)) / len(set1.union(set2))


def levenshteinDist(text1, text2):

    '''
    Return the Levenshtein distance between two strings.

    Args:
        text1 (string): The first piece of text for comparison.
        text2 (string): The second piece of text for comparison.

    Returns:
        int: An integer determining the Levenshtein distance between the two strings.
    '''

    return Levenshtein.distance(text1, text2)


def euclidean_dist(text1, text2):

    '''
    Return the Euclidean distance between two strings.

    Args:
        text1 (string): The first piece of text for comparison.
        text2 (string): The second piece of text for comparison.

    Returns:
        numpy.float64: A float determining the Euclidean distance between the two strings.
    '''

    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()

    return distance.euclidean(vectors[0], vectors[1])