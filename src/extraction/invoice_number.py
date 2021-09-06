
from .utils import extract_item_by_key, normalize_text


def extract_invoice_number(input_data):

    regex_keys = [r"Invoice-No.:", r"invoice no.:", r"invoice no.", r"invoice"]
    regex_payload = r"(.+)"
    for regex_key in regex_keys:
        result_list = extract_item_by_key(input_data, regex_key, regex_payload, normalize_text)
        if result_list:
            return {'invoice_number': result_list[0]}

    return {'invoice_number': 'NOT_FOUND'}
