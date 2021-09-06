from pymongo import MongoClient
import datetime

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["dluca"] # set your own database, on your local MongoDB env
mongo_collection = mongo_db["extract"]


def insert_document(doc_id, file_name, doc_type="pdf", doc_source="local"):
    """
    Insert a new document in MongoDB
    @param doc_id - document id; this is composed based on file name and timestamp
    @param file_name - file name
    @param doc_type - type of the document; default value is pdf
    @param doc_source - source of the document; default value is local
    """
    mongo_dict = {"_id": f"/documents/{doc_id}/metadata.json",
                  "file": {"document_id": doc_id,
                           "document_name": file_name,
                           "document_type": doc_type,
                           "document_source": doc_source
                           },
                  "content_type": "application/json",
                  "created_timestamp": datetime.datetime.utcnow().isoformat()
              }
    try:
        mongo_collection.insert_one(mongo_dict)
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def write_pages_no_document(doc_id, pages_no):
    """
    Write a new pages_no document in MongoDB
    @param doc_id - document id
    @param pages_no - number of pages
    """
    mongo_dict = {"_id": f"/documents/{doc_id}/pages_no.json",
                  "pages_no": pages_no,
                  "content_type": "application/json",
                  "created_timestamp": datetime.datetime.utcnow().isoformat(),
                  "updated_timestamp": datetime.datetime.utcnow().isoformat()
              }
    try:
        mongo_collection.insert_one(mongo_dict)
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def write_hocr_document(doc_id, page, hocr):
    """
    Write the extracted text (using OCR) from one page of the document; one such document/page
    @param doc_id - document id
    @param page - current page
    @param hocr - xml with character position & value - from OCR
    """
    mongo_dict = {"_id": f"/documents/{doc_id}/{page}.hocr",
                  "file": hocr,
                  "content_type": "text/html",
                  "created_timestamp": datetime.datetime.utcnow().isoformat(),
                  "updated_timestamp": datetime.datetime.utcnow().isoformat()
              }
    try:
        mongo_collection.insert_one(mongo_dict)
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def write_extraction(doc_id, extraction_data):
    """
    Write the extraction dictionary in MongoDB
    @param doc_id - document id
    @param extraction_data - dictionary with the extraction data
    """
    mongo_dict = {"_id": f"/documents/{doc_id}/extraction.json",
                  "extraction": extraction_data,
                  "content_type": "application/json",
                  "created_timestamp": datetime.datetime.utcnow().isoformat(),
                  "updated_timestamp": datetime.datetime.utcnow().isoformat()
              }
    try:
        mongo_collection.insert_one(mongo_dict)
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def get_document_by_id(doc_id):
    """
    This function doesn't seems to be correctly implemented
    """
    try:
        mongo_query = {"_id": f"/documents/{doc_id}/metadata.json"}
        results = mongo_collection.find(mongo_query)
        if results:
            for result in results:
                return result
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def get_hocr_content_by_id_and_page(doc_id, page):
    """
    Get hocr content for a doc id and a page
    @param doc_id - document id
    @param page - current page
    @return - the hocr content for the given page
    """
    try:
        mongo_query = {"_id": f"/documents/{doc_id}/{page}.hocr"}
        results = mongo_collection.find(mongo_query)
        if results:
            for result in results:
                return result['file']
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def get_num_pages_document(doc_id):
    """
    Returns the number of the pages for a certain document, identified by doc_id
    @param doc_id - document id
    @return number of pages
    """
    try:
        mongo_query = {"_id": f"/documents/{doc_id}/pages_no.json"}
        results = mongo_collection.find(mongo_query)
        if results:
            for result in results:
                return result['pages_no']
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def get_extraction(doc_id):
    """
     Returns the extraction dictionary for a certain document, identified by doc_id
    @param doc_id - document id
    @return extraction data
    """
    try:
        mongo_query = {"_id": f"/documents/{doc_id}/extraction.json"}
        results = mongo_collection.find(mongo_query)
        if results:
            for result in results:
                return result
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass


def get_documents_list(filter_expression):
    """
    Return a list of documents based on a filter expression
    @param filter_expression: expression for filter
    @return document list
    """
    try:
        mongo_query = filter_expression
        results = mongo_collection.find(mongo_query)
        if results:
            return results
    except Exception as ex:
        print("Exception MongoDB:", ex)
        pass
