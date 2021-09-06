import re

from wand.image import Image as Img

from ..storage.storage_service import get_document_binary_path, get_image_path, write_pages_no


def count_pages(filename):
    """
    function: count the number of pages in a pdf document
    input: filename - pdf file name
    output: number of pages in pdf document
    """
    rxcountpages = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE | re.DOTALL)

    f = open(filename, "rt", encoding='latin1')
    data = f.read()
    f.close()
    return len(rxcountpages.findall(data))


def pdf_to_img(doc_id, image_ext='png', resolution=300):
    """
    function: function to split of pdf pages in images; images are created and saved in the working directory for each
              page in the pdf
    input: doc_id - image file to scan
    input: image_ext - default is jpg
    """
    pdf_file_path = get_document_binary_path(doc_id)
    pdf_info_num_pages = count_pages(pdf_file_path)

    save_file_path = get_image_path(doc_id, image_ext)

    try:
        with Img(filename=pdf_file_path, resolution=resolution) as img:
            img.compression_quality = 99
            img.convert("RGBA").save(filename=save_file_path)
        write_pages_no(doc_id, pdf_info_num_pages)
    except Exception as e:
        print(f"Exception PDF2IMG: {e}")
        pass

