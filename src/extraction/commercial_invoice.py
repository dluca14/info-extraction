import os
import joblib

from ..extraction.classifier.text_utils import extract_words


def classify_document(input_data):
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    pipeline = joblib.load(os.path.join(path, "extraction", "classifier", "pipeline_linearsvc.pkl"))
    mappings = joblib.load(os.path.join(path, "extraction", "classifier", "mappings_linearsvc.pkl"))
    doc_text = extract_words(input_data)
    doc_class = pipeline.predict([doc_text])
    print(doc_class)
    return doc_class


def extract_commercial_invoice(input_data):
    is_commercial_invoice = classify_document(input_data)
    extract = {
        "extraction": {
            "value": str(is_commercial_invoice[0]),
            "normalized_value": str(is_commercial_invoice[0]),
            "value_words": [{"x1":100, "x2":200, "y1": 100, "y2": 200}],
            "page_number": "0"
        }
    }
    return {'commercial_invoice': extract}
