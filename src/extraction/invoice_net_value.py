from .utils import extract_item_by_key, normalize_text


def extract_invoice_net_value(input_data):
    regex_keys = [r"Net value"]
    regex_payload = r"(.+)"
    for regex_key in regex_keys:
        result_list = extract_item_by_key(input_data, regex_key, regex_payload, normalize_text)
        if result_list:
            return {'invoice_net_value': result_list[0]}

    return {'invoice_net_value': 'NOT_FOUND'}
