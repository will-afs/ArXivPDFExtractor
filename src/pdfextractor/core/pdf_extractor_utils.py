import urllib
from io import BytesIO
from typing import List
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from PyPDF2 import PdfFileReader
import pdftotext

def get_file_object_from_uri(file_uri: str) -> BytesIO:
    """Return a Python File Object obtained from an URI
    Parameters:
    file_uri (str) : the URI to access the file
    Returns:
    io.BytesIO: File object corresponding to the file being pointed by the URI
    """
    try:
        response = urllib.request.urlopen(file_uri)
    except urllib.error.HTTPError:
        raise FileNotFoundError("Could not access the provided URI")
    except ValueError:
        raise ValueError("Wrong URI format")
    else:
        pdf= response.read()
        pdf_bytesio_file_object = BytesIO()
        pdf_bytesio_file_object.write(pdf)
        return pdf_bytesio_file_object

def extract_pdf_raw_data_from_pdf_miner(file_obj:BytesIO, pdf_uri) -> List:
    pdf_parser = PDFParser(file_obj)
    doc = PDFDocument(pdf_parser)

    # 1. Extract PDF Metadata
    pdf_metadata = doc.info[0]
    for (key, value) in doc.info[0].items():
        # Need to decode each value from bytestrings toward strings
        pdf_metadata[key] = value.decode("utf-8", errors="ignore")
    pdf_metadata['uri'] = pdf_uri
    # 2. Extract PDF content
    try:
        pdf_content = extract_text(file_obj)
    except TypeError:
        raise TypeError('Something went wrong in the PDF content extraction, due to a bug in pdfminer library')
    return pdf_metadata, pdf_content


def extract_pdf_raw_data_from_pypdf_and_pdftotext(file_obj:BytesIO, pdf_uri) -> List:
    # 1. Extract PDF Metadata
    pdf = PdfFileReader(file_obj)
    info = pdf.getDocumentInfo()
    # number_of_pages = pdf.getNumPages()
    # author = info.author
    # creator = info.creator
    # producer = info.producer
    # subject = info.subject
    # title = info.title
    pdf_metadata = {
                        'uri':pdf_uri,
                        'author':info.author,
                        'producer':info.producer,
                        'subject':info.subject,
                        'title':info.title,
                        # 'creator':info.creator,
    }
    # 2. Extracting PDF content
    pdf_content = pdftotext.PDF(file_obj)
    return pdf_metadata, pdf_content

def extract_data_from_pdf_uri(pdf_uri:str) -> List:
    """Extracts data from a PDF being pointed by a URI
    Parameters:
    pdf_uri (str) : the URI through which access the file
    Returns:
    dict: metadata of the PDF, presented as a JSON structured as follows :
        {
            "Producer": "GPL Ghostscript SVN PRE-RELEASE 8.62",
            "CreationDate": "D:20080203020500-05'00'",
            "ModDate": "D:20080203020500-05'00'",
            "Creator": "dvips 5.499 Copyright 1986, 1993 Radical Eye Software",
            "Title": "dynamic.dvi"
        }
    str: PDF content
    """
    # TODO : request permission to CooldownManager to request ArXiv
    file_obj = get_file_object_from_uri(pdf_uri)
    pdf_metadata, pdf_content = extract_pdf_raw_data_from_pdf_miner(file_obj, pdf_uri)

    return pdf_metadata, pdf_content