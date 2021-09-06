
from ..text_format.layout_analyzer import layout
from ..storage.storage_service import get_num_pages, get_text_content, write_text_content


def process_layout_text(doc_id):
    """
    Process text content, to generate the layout information (paragraphs, tables)
    @param doc_id - document id
    @return doc_id - not actually needed
    """
    num_pages = get_num_pages(doc_id)
    text_content = get_text_content(doc_id, layout=False)
    layout_text_content = {}
    for page in range(num_pages):
        layout_text_content[page] = layout(text_content[str(page)])
    write_text_content(doc_id, layout_text_content, layout=True)
    return doc_id
