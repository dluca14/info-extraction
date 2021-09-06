from ..storage.storage_service import get_num_pages, write_text_content
from ..storage.mongo_db import get_hocr_content_by_id_and_page
from ..ocr.pdf_to_image import pdf_to_img
from ..ocr.image_to_hocr import ocr_core_image_process
from ..text_format.hocr_to_json import extract_hocr_json
from ..text_format.layout_analyzer import layout


def process_pdf_image(doc_id):
    """
    Process staged document, to extract images from pages and then to apply OCR to page images
    Images are stored in binary storage
    Extracted text is stored (as xml) in MongoDB
    hOCR data is then converted to content.json and this is stored to binary storage
    @param doc_id - document id
    @return doc_id
    """
    pdf_to_img(doc_id)
    num_pages = get_num_pages(doc_id)
    text_content = {}
    for page in range(num_pages):
        ocr_core_image_process(doc_id, page, num_pages)
        hocr_content = get_hocr_content_by_id_and_page(doc_id, page)
        text = extract_hocr_json(hocr_content)
        text_content[page] = text
    write_text_content(doc_id, text_content)

    return doc_id

