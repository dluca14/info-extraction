import pandas as pd
import pickle
import os
from .text_utils import get_doc_texts


def create_raw_texts():
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    path_to_labels = os.path.join(path, "classifier", "labels.csv")

    raw_texts = get_doc_texts()

    data_df = pd.DataFrame(raw_texts)
    data_df.columns = ["filename", "text"]
    label_data = pd.read_csv(path_to_labels)
    labeled_data = pd.merge(label_data, data_df, on="filename", how="right")
    labeled_data.columns = ["filename", "label", "text"]

    with open(os.path.join(path, "classifier", "raw_texts.pickle"), "wb") as handle:
        pickle.dump(labeled_data.values, handle, protocol=pickle.HIGHEST_PROTOCOL)


