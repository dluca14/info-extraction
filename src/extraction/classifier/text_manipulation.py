import re
import sys
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import nltk

ENGLISH_STOPWORDS = en_stop = set(stopwords.words("english"))
ENGLISH_STEMMER = SnowballStemmer("english")


def pre_processing_text(document):
    tokens = document.lower()
    tokens = re.sub(r'[^\w\s]', '', tokens)
    tokens = re.sub(r'[^a-z ]', '', tokens)
    return tokens


def prepare_text(document, stem=True, lemma=False, stop=True):
    tokens = pre_processing_text(document)
    tokens = word_tokenize(tokens)
    if stop:
        tokens = [token for token in tokens if token not in ENGLISH_STOPWORDS]
    if stem:
        tokens = [ENGLISH_STEMMER.stem(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens


def prepare_by_regex(document, patterns):
    tokens = pre_processing_text(document)
    keywords = re.findall('|'.join(patterns), tokens)
    return ' '.join(keywords)