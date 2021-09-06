import os
import shutil
import json

# root_folder = "C:\\D\\Workspace\\ipgds001\\TEC\\Information Extraction Workshop\\src\\data"
root_folder = "C:\\Users\\daluca\\Workspace\\data"
input_folder = os.path.join(root_folder, "input")
output_folder = os.path.join(root_folder, "documents")
workflow_path = os.path.join(root_folder, "workflow")

"""
Structure of binary storage for a document
[] document_folder_hash
 |
 document.pdf
 [] page
    |-image-0.png
    |-image-1.png
 [] text
    |-content.json
    |-layout_content.json
"""


def create_if_not_exists(path):
    """
    Utility function to create a folder, if not exists
    @param: path - for the folder
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as ex:
        print(ex)
        pass


def save_binary(doc_id, filename):
    """
    Function used to stage an ingested document in binary storage
    @param doc_id - document id
    @param filename - file to be ingested. It is copied from input folder to documents (binary storage) folder

    """
    try:
        # create a folder with the file identifier
        os.makedirs(os.path.join(output_folder, doc_id), exist_ok=True)
        # copy the document in the file
        shutil.copy(os.path.join(input_folder, filename), os.path.join(output_folder, doc_id, "document.pdf"))
    except Exception as ex:
        print(ex)
        pass


def write_content(doc_id, text_content, layout):
    """
    Write text content (content.json or layout_content.json) to text folder in binary storage
    @param doc_id - document id
    @param text_content - text content to be saved (content/layout_content)
    @param layout  - flag, set to True if layout_content.json is saved
    """
    try:
        # create a folder with the file identifier
        text_folder = os.path.join(output_folder, doc_id, "text")
        os.makedirs(text_folder, exist_ok=True)
        # copy the document in the file
        if layout:
            file_name = "layout_content.json"
        else:
            file_name = "content.json"
        with open(os.path.join(text_folder, file_name), "wt") as file:
            json.dump(text_content, file)
        file.close()
    except Exception as ex:
        print(ex)
        pass


def get_document_path(doc_id):
    """
    Staged document path
    @param doc_id - document id
    @return staged document path
    """
    return os.path.join(output_folder, doc_id, "document.pdf")


def get_image_partial_path(doc_id):
    """
    Extracted image partial path
    @param doc_id - document id
    @return  image partial path
    """
    return os.path.join(output_folder, doc_id, "page", "image")


def get_make_image_path(doc_id, image_ext):
    """
    Create image folder and save image extracted
    @param doc_id - document id
    @param image_ext - extension of the image
    @return name of the saved file
    """
    save_file_name = f"image.{image_ext}"
    create_if_not_exists(os.path.join(output_folder, doc_id, "page"))
    save_file_name = os.path.join(output_folder, doc_id, "page", save_file_name)
    return save_file_name


def get_content(doc_id, layout):
    """
    Get the extracted text content
    @param doc_id - document id
    @param layout - flag for type of content file; if flag set to True, returns layout_content, else content
    @return text content
    """
    try:
        text_folder = os.path.join(output_folder, doc_id, "text")
        # read the document from the file
        if layout:
            file_name = "layout_content.json"
        else:
            file_name = "content.json"
        with open(os.path.join(text_folder, file_name), "rt") as file:
            text_content = json.load(file)
        file.close()
        return text_content
    except Exception as ex:
        print(ex)
        pass


def get_doc_id():
    """
    Function used by workflow to get current doc_id
    """
    with open(os.path.join(workflow_path, 'doc.id'), "rt") as f:
        doc_id = str(f.read())
    f.close()
    return doc_id


def get_doc_name():
    """
    Function used by workflow to get current doc name
    """
    with open(os.path.join(workflow_path, 'doc.name'), "rt") as f:
        doc_name = str(f.read())
    f.close()
    return doc_name


def write_doc_id(doc_id):
    """
    Function used by workflow to write current doc_id
    """
    with open(os.path.join(workflow_path, 'doc.id'), "wt") as f:
        f.write(f"{doc_id}")
    f.close()


def write_doc_name(doc_name):
    """
    Function used by workflow to write current doc name
    """
    with open(os.path.join(workflow_path, 'doc.name'), "wt") as f:
        f.write(f"{doc_name}")
    f.close()
