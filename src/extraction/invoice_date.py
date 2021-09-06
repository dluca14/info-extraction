from .utils import extract_item_by_key, normalize_date


def extract_invoice_date(input_data):
    regex_keys = [r"Date", r"Date:"]
    regex_payload = r"(.+)"
    for regex_key in regex_keys:
        result_list = extract_item_by_key(input_data, regex_key, regex_payload, normalize_date)
        if result_list:
            return {'invoice_date': result_list[0]}

    return {'invoice_date': 'NOT_FOUND'}
