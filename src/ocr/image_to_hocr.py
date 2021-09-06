import pytesseract
from PIL import Image

from ..storage.storage_service import write_hocr, get_image_file_path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def ocr_core_image_process(doc_id, page, num_pages):
    """
    function: function to handle the core OCR processing of images.
    input: filename - image file to scan
    input: page - current page in the current document (filename)
    input: pdf_info_num_pages - number of pages in current document
    input: work_folder_scan - working folder for scanned images
    output: text extracted
    """
    file_img = get_image_file_path(doc_id, page, num_pages)
    image_handler = Image.open(file_img)
    try:
        hocr = pytesseract.image_to_pdf_or_hocr(image_handler, extension='hocr')
        write_hocr(doc_id, page, hocr)

    except Exception as ex:
        print(f"Exception OCR: {ex}")
        pass
