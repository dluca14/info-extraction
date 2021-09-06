import hashlib

import datetime
from .mongo_db import insert_document, write_pages_no_document, write_hocr_document, get_num_pages_document,\
    write_extraction, get_extraction, get_documents_list

from .binary_storage import save_binary, get_document_path, get_make_image_path, get_image_partial_path, write_content,\
    get_content


def stage_document(filename):
    # create a unique identifier for document
    datetime_now = datetime.datetime.utcnow().isoformat()
    doc_id = hashlib.md5(f"{datetime_now}{filename}".encode("utf-8")).hexdigest()
    save_binary(doc_id, filename)
    insert_document(doc_id, filename)
    return doc_id


def write_pages_no(doc_id, pdf_info_num_pages):
    write_pages_no_document(doc_id, pdf_info_num_pages)


def write_hocr(doc_id, page, hocr):
    write_hocr_document(doc_id, page, hocr)


def write_text_content(doc_id, text_content, layout=False):
    write_content(doc_id, text_content, layout)


def write_extraction_data(doc_id, extraction_data):
    write_extraction(doc_id, extraction_data)


def get_document_binary_path(doc_id):
    return get_document_path(doc_id)


def get_image_path(doc_id, image_ext):
    return get_make_image_path(doc_id, image_ext)


def get_image_file_path(doc_id, page, num_pages):

    img_file_name = get_image_partial_path(doc_id)
    if num_pages == 1:
        return f"{img_file_name}.png"
    else:
        return f"{img_file_name}-{page}.png"


def get_num_pages(doc_id):
    return get_num_pages_document(doc_id)


def get_text_content(doc_id, layout=False):
    return get_content(doc_id, layout)


def get_extraction_data(doc_id):
    return get_extraction(doc_id)


def search_file_projection(filter_expression):
    return get_documents_list(filter_expression)
