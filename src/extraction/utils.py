import json
import re
from dateutil import parser


def normalize_text(text):
    normalized_text = re.sub(r'[!|]', '1', text)
    normalized_text = re.sub(r'\[', '', normalized_text)
    normalized_text = re.sub(r'\]', '', normalized_text)
    normalized_text = normalized_text.rstrip()
    normalized_text = normalized_text.lstrip()

    return normalized_text


def normalize_date(date):
    normalized_date = date.rstrip()
    normalized_date = normalized_date.lstrip()
    normalized_date = re.sub(r'\sist\s', ' 1 ', normalized_date)
    normalized_date = re.sub(r'\sis\s', ' 1 ', normalized_date)
    normalized_date = re.sub(r'\saus\s|\sAGGUST\s', ' august ', normalized_date)
    normalized_date = re.sub(r'\sOct\s|\s0Oct\s', ' Oct ', normalized_date)
    normalized_date = re.sub(r'\sMgr\s', ' Mar ', normalized_date)
    normalized_date = re.sub(r'\say\s', ' May ', normalized_date)
    normalized_date = re.sub(r'\sAyr\s', ' Apr ', normalized_date)
    normalized_date = re.sub(r' ', '.', normalized_date)
    normalized_date = re.sub(r'\*', '.', normalized_date)

    try:
        date_value = parser.parse(normalized_date, fuzzy=True, ignoretz=True).isoformat()
    except:
        date_value = "NOT_FOUND"

    return date_value


def generate_static_catalog(path_to_catalog):
    with open(path_to_catalog, encoding='utf-8') as file:
        static_catalog = json.load(file)
    return static_catalog


def extract_document_text_items(input_data):
    extracted_document_text_items = []
    for page_number, page_data in input_data.items():
        for item in page_data["layout"]:
            if item["type"] == "table":
                for row in item["rows"]:
                    for cell in row["cells"]:
                        extracted_document_text_items.append((cell, page_number))
            else:
                extracted_document_text_items.append((item, page_number))
    return extracted_document_text_items


def bbox_helper(word):
    return (word["x1"], word["y1"]), (word["x2"], word["y2"])


def bbox_merge(bbox_list):
    x_min = y_min = 10000
    x_max = y_max = 0
    for bbox in bbox_list:
        (x1, y1), (x2, y2) = bbox
        if x1 < x_min:
            x_min = x1
        if x2 > x_max:
            x_max = x2
        if y1 < y_min:
            y_min = y1
        if y2 > y_max:
            y_max = y2

    return x_min, y_min, x_max, y_max


def is_next_bbox(bbox_1, bbox_2, factor=4):
    x11, y11, x12, y12 = bbox_1
    (x21, y21), (x22, y22) = bbox_2
    dy = ((y21 + y22) - (y11 + y12)) / 2
    delta_y = abs(y21 - y22) / 2
    delta_x = factor * delta_y
    if (x21 > (x12 + delta_x)) & (abs(dy) < delta_y):
        return True
    else:
        return False


def is_bottom_side_bbox(bbox_1, bbox_2, delta_x=100, delta_y=400):
    x11, y11, x12, y12 = bbox_1
    (x21, y21), (x22, y22) = bbox_2
    dx = ((x21 + x22) - (x11 + x12)) / 2

    if ((y21 > y12) & (y21 < y12 + delta_y)) * (abs(dx) < delta_x):
        return True
    else:
        return False


def add_extracted_items(bbox, page, is_under, right_distance_factor, item_list, extracted_document_text_items):
    text_list = []
    word_list = []
    for word in item_list:
        if is_under:
            if is_bottom_side_bbox(bbox, bbox_helper(word)):
                text_list.append(word["t"])
                word_list.append(word)
        else:
            if is_next_bbox(bbox, bbox_helper(word), right_distance_factor):
                text_list.append(word["t"])
                word_list.append(word)
    if text_list is not None:
        text = " ".join(text_list)
        item = {"words": word_list, "text": text}
        extracted_document_text_items.append((item, page))


def extract_document_text_items_bbox_next(input_data, bbox, page, is_under=False, right_distance_factor=4):
    extracted_document_text_items = []
    for page_number, page_data in input_data.items():
        if int(page) == int(page_number):
            for item in page_data["layout"]:
                if item["type"] == "table":
                    for row in item["rows"]:
                        for cell in row["cells"]:
                            add_extracted_items(bbox, page, is_under, right_distance_factor, cell["words"],
                                                extracted_document_text_items)
                else:
                    add_extracted_items(bbox, page, is_under, right_distance_factor, item["words"],
                                        extracted_document_text_items)
    return extracted_document_text_items


def get_matched_words_data_list(matched_words_list, paragraph_words_data_list, trim_word_list=False):
    trimmed_matched_words_list = matched_words_list[1:-1] if trim_word_list else matched_words_list
    matched_words_list_length = len(matched_words_list)
    paragraph_words_data_list_length = len(paragraph_words_data_list)
    step = 0
    limit = paragraph_words_data_list_length - matched_words_list_length + 1
    while step < limit:
        sublist_end = step + matched_words_list_length
        sublist_to_be_compared = [word["t"][0] if isinstance(word["t"], list) else word["t"] for word in \
                                  paragraph_words_data_list[step:sublist_end]]
        if trimmed_matched_words_list == sublist_to_be_compared:
            return paragraph_words_data_list[step:sublist_end]
        is_partial_match = True
        for item in range(0, matched_words_list_length):
            if trimmed_matched_words_list[item] not in sublist_to_be_compared[item]:
                is_partial_match = False
                break
        if is_partial_match:
            return paragraph_words_data_list[step:sublist_end]
        step += 1
    return []


def item_extractor(item_type, page_number, regex, group, normalize, result_list, ignore_case=True):
    text = item_type["text"]
    pattern = re.compile(regex, re.UNICODE | re.IGNORECASE) if ignore_case else re.compile(regex, re.UNICODE)
    results = [match.group(group) for match in pattern.finditer(text)]
    if results:
        for result in results:
            if result:
                matched_words = result.split()
                value_words = get_matched_words_data_list(matched_words, item_type.get("words"))
                match = {
                    "extraction": {
                        "value": result,
                        "normalized_value": normalize(result),
                        "value_words": value_words,
                        "page_number": page_number
                    }
                }
                result_list.append(match)


def get_key_page_and_bounding_box(extraction):
    """
    Function to get page and bounding box
    """
    bbox_list = []
    for word in extraction["value_words"]:
        bbox_list.append(bbox_helper(word))
    return extraction["page_number"], bbox_merge(bbox_list)


def extract_item_by_key(input_data, regex_key, regex_payload, normalize_function, is_under=False,
                        right_distance_factor=4):
    group = 0
    result_list_anchor = []
    for item in extract_document_text_items(input_data):
        item_extractor(item[0], item[1], regex_key, group, normalize_function, result_list_anchor)
    anchor = result_list_anchor[0] if result_list_anchor else None

    if anchor:
        page, bbox = get_key_page_and_bounding_box(anchor["extraction"])
        result_list = []
        for item in extract_document_text_items_bbox_next(input_data, bbox, page, is_under, right_distance_factor):
            item_extractor(item[0], item[1], regex_payload, group, normalize_function, result_list)

        return result_list
