import pickle
import joblib
import pandas as pd
import os
import sys
from sklearn.preprocessing import LabelEncoder
from .text_processor import TextTransformer
from .text_manipulation import prepare_text
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC


def data_preparation():
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    with open(os.path.join(path, "classifier", "raw_texts.pickle"), "rb") as handle:
        dev_texts = pickle.load(handle)
    return dev_texts


def create_corpus(dev_texts):
    corpus_df = pd.DataFrame(dev_texts)
    corpus_df.columns = ["filename", "label", "text"]
    corpus_df = corpus_df.dropna(subset=["text"])
    return corpus_df


def label_encoding(corpus_df):
    labels = corpus_df["label"].unique()
    le = LabelEncoder()
    le.fit(labels)
    y = le.transform(corpus_df["label"])
    return y, le


def define_pipeline():
    classifier = Pipeline([('pre_processor', TextTransformer(prepare_text)),
                           ('c_vectorizer', CountVectorizer()),
                           ('tf_idf', TfidfTransformer()),
                           ('classifier', SVC(kernel='linear'))])

    return classifier


def run_classifier_svc(x, y, le):
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    classifier = define_pipeline()
    train_x, valid_x, train_y, valid_y = train_test_split(x, y, test_size=0.33, random_state=42)
    clf = classifier.fit(train_x, train_y)
    y_true, y_pred = valid_y, clf.predict(valid_x)
    print(classification_report(y_true, y_pred))
    print(f"\nValidation accuracy: {accuracy_score(y_true, y_pred)}")

    svc_clf = classifier.fit(x, y)

    joblib.dump(svc_clf, os.path.join(path, "classifier", "pipeline_linearsvc.pkl"))
    joblib.dump(le.classes_, os.path.join(path, "classifier", "mappings_linearsvc.pkl"))


def train_classifier():
    dev_texts = data_preparation()
    corpus_df = create_corpus(dev_texts)
    y, le = label_encoding(corpus_df)
    x = corpus_df["text"]
    run_classifier_svc(x, y, le)



