from .invoice_amount import extract_invoice_amount
from .invoice_number import extract_invoice_number
from .invoice_currency import extract_invoice_currency
from .invoice_date import extract_invoice_date
from .signature import extract_signature
from .proper_nouns import extract_proper_nouns
from .commercial_invoice import extract_commercial_invoice
from .invoice_vat import extract_invoice_vat
from .invoice_net_value import extract_invoice_net_value
from ..storage.storage_service import get_text_content
from ..storage.storage_service import write_extraction_data


def extract(doc_id):
    """
    Extraction function. Extraction data is written in MongoDB
    @param doc_id - document id
    """
    input_data = get_text_content(doc_id, layout=True)

    invoice_amount = extract_invoice_amount(input_data)
    invoice_currency = extract_invoice_currency(input_data)
    invoice_date = extract_invoice_date(input_data)
    invoice_number = extract_invoice_number(input_data)
    # invoice_vat = extract_invoice_vat(input_data)
    invoice_net_value = extract_invoice_net_value(input_data)
    signature = extract_signature(doc_id)
    proper_nouns = extract_proper_nouns(input_data)
    commercial_invoice = extract_commercial_invoice(input_data)
    extraction_data = {**invoice_amount, **invoice_currency,
                       **invoice_date, **invoice_number,
                       **signature, **proper_nouns, **commercial_invoice,
                       **invoice_net_value}
    write_extraction_data(doc_id, extraction_data)
