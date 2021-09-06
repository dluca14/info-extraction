from ..storage.storage_service import stage_document


def ingest_document(doc_name):
    """
    Stage the input document; a doc_id is generated and is used as index for all information related to the current doc
    @param doc_name - the document name
    @return doc_id - the document id
    """
    doc_id = stage_document(doc_name)
    return doc_id

