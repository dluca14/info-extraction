
from ...storage.storage_service import search_file_projection
from ...storage.storage_service import get_text_content


def extract_words(json_data):
    doc_text = []
    for page_number, page_data in json_data.items():
        for item in page_data["layout"]:
            if item["type"] == "table":
                for row in item["rows"]:
                    for cell in row["cells"]:
                        for word in cell["words"]:
                            doc_text.append(word["t"][0] if isinstance(word["t"], list) else word["t"])
            else:
                for word in item["words"]:
                    doc_text.append(word["t"][0] if isinstance(word["t"], list) else word["t"])
    doc_text = " ".join(doc_text)
    return doc_text


def get_doc_texts():
    filter_document = {"_id":  {"$regex": "/metadata.json"}}
    documents = search_file_projection(filter_document)
    doc_text_list = []
    for document in documents:
        file_name = document['file']['document_name']
        doc_id = document['file']['document_id']
        json_data = get_text_content(doc_id, True)
        doc_text = extract_words(json_data)
        doc_text_list.append([file_name, doc_text])

    return doc_text_list
