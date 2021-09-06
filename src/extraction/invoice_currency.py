import json
import os
import re

from .utils import extract_item_by_key, normalize_text


def validate_currency(extracted):
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    with open(f'{path}/extraction/catalogs/currency.json', encoding="utf8") as file:
        currency_list = json.load(file)

    if extracted and extracted != "NOT_FOUND":
        for currency in currency_list.items():

            # check full match
            if extracted["extraction"]["normalized_value"] == currency[1]["symbol"] or \
                    extracted["extraction"]["normalized_value"] == currency[1]["currency"]:
                return extracted

    # check partial match + extract
    regex = f"({re.escape(currency[1]['symbol'])}|{re.escape(currency[1]['currency'])})"
    group = 0
    pattern = re.compile(regex, re.UNICODE | re.IGNORECASE)
    results = [match.group(group) for match in pattern.finditer(extracted["extraction"]["normalized_value"])]
    if results:
        extracted["extraction"]["normalized_value"] = currency[1]["currency"]
        return extracted
    return "NOT_FOUND"


def extract_invoice_currency(input_data):
    regex_keys = [r"Currency", r"currency"]
    regex_payload = r"(.+)"
    for regex_key in regex_keys:
        result_list = extract_item_by_key(input_data, regex_key, regex_payload, normalize_text, right_distance_factor=1)
        if result_list:
            extracted = validate_currency(result_list[0])
            if extracted and extracted != "NOT_FOUND":
                return {'invoice_currency': result_list[0]}

    return {'invoice_currency': 'NOT_FOUND'}
