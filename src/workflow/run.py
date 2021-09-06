import luigi
import sys
import os

sys.path.append("..//..")
sys.path.append("..")

from src.extraction.extract import extract
from src.ingestion.input import ingest_document
from src.ocr.process_ocr import process_pdf_image
from src.text_format.process_text import process_layout_text
from src.notebooks.plot_utils import plot_extraction
from src.storage.binary_storage import get_doc_name, get_doc_id, write_doc_name, write_doc_id


if __name__ == '__main__':
    doc_name = 'Invoice_28092018-171040.pdf'
    doc_id = ingest_document(doc_name)
    process_pdf_image(doc_id)
    process_layout_text(doc_id)
    extract(doc_id)
    plot_extraction(doc_id)


def run_workflow(doc_name):
    doc_id = ingest_document(doc_name)
    process_pdf_image(doc_id)
    process_layout_text(doc_id)
    extract(doc_id)
    plot_extraction(doc_id)


def run_workflow_luigi(doc_name):
    write_doc_name(doc_name)
    os.system("python -m luigi --module run Extract --local-scheduler")


class IngestDocument(luigi.Task):

    is_complete = False

    @property
    def output(self):
        return self.doc_id

    @property
    def name(self):
        return 'ingest-document'

    def requires(self):
        return None

    def run(self):
        doc_id = ingest_document(get_doc_name())
        write_doc_id(doc_id)
        self.is_complete = True

    def complete(self):
        return True if self.is_complete else False


class OcrDocument(luigi.Task):

    is_complete = False

    @property
    def name(self):
        return 'ocr-document'

    def requires(self):
        return IngestDocument()

    def run(self):
        process_pdf_image(get_doc_id())
        self.is_complete = True

    def complete(self):
        return True if self.is_complete else False


class TextAggregateDocument(luigi.Task):

    is_complete = False

    @property
    def name(self):
        return 'aggregate-document'

    def requires(self):
        return OcrDocument()

    def run(self):
        process_layout_text(get_doc_id())
        self.is_complete = True

    def complete(self):
        return True if self.is_complete else False


class Extract(luigi.Task):

    is_complete = False

    @property
    def name(self):
        return 'extraction'

    def requires(self):
        return TextAggregateDocument()

    def run(self):
        extract(get_doc_id())
        self.is_complete = True

    def complete(self):
        return True if self.is_complete else False


class PlotExtraction(luigi.Task):

    is_complete = False

    @property
    def name(self):
        return 'extraction'

    def requires(self):
        return Extract()

    def run(self):
        plot_extraction(get_doc_id())
        self.is_complete = True

    def complete(self):
        return True if self.is_complete else False