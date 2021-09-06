import spacy
import os
import json
from .utils import extract_document_text_items, get_matched_words_data_list
nlp = spacy.load("en_core_web_sm")


def extract_nouns(text, label_list):
    doc = nlp(text)
    results = []
    for entity in doc.ents:
        if entity.label_ in label_list:
            results.append({'text': entity.text, 'label': entity.label_})
    return results


def item_extractor_nlp(item_type, page_number, result_list):
    text = item_type["text"]
    labeled_list = ["PERSON", "ORG", "GPE"]
    proper_nouns = extract_nouns(text, labeled_list)
    if proper_nouns:
        for proper_noun in proper_nouns:
            value = proper_noun["text"]
            label = proper_noun["label"]
            value_words = get_matched_words_data_list(value.split(), item_type.get("words"))
            if value_words:
                match = {
                    "extraction": {
                        "value": value,
                        "label": label,
                        "value_words": value_words,
                        "page_number": page_number
                    }
                }
                result_list.append(match)


def filter_results_list(results_list):

    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    with open(f'{path}/extraction/catalogs/blacklist.json', encoding="utf8") as file:
        blacklist = json.load(file)

    filtered_results_list = []

    for result in results_list:
        keep = True
        for item in blacklist:
            if result['extraction']['label'] == item['label'] and result['extraction']['value'] == item['value']:
                keep = False
                break
        if keep:
            filtered_results_list.append(result)

    return filtered_results_list


def extract_proper_nouns(input_data):
    results_list = []
    for item in extract_document_text_items(input_data):
        item_extractor_nlp(item[0], item[1], results_list)

    if results_list:
        filtered_result_list = filter_results_list(results_list)

        return {"proper_nouns": filtered_result_list}

    return {"proper_nouns": "NOT_FOUND"}