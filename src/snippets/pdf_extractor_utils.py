from src.cooldown_manager_utils import get_permission_to_request_arxiv

from http.client import HTTPResponse
import urllib
from io import BytesIO
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser

from refextract import extract_journal_reference
import validators

def extract_references_from_pdf(pdf:BytesIO)->list:
    """Return the references of a PDF

    Parameters:
    pdf (BytesIO) : the PDF as a Python File Object
    cooldown_manager_uri (str) : the URI through which ask permission to CooldownManager\
        to request ArXiv.org services

    Returns:
    list: A list of the references found in the PDF
    """
    return extract_journal_reference(pdf)
        
def request_file_through_uri(file_uri: str, cooldown_manager_uri:str) -> HTTPResponse :
    """Request a file through the provided URI, after having obtained permission to cooldown manager

    Parameters:
    file_uri (str) : the URI to access the file
    cooldown_manager_uri (str) : the URI through which ask permission to CooldownManager\
        to request ArXiv.org services

    Returns:
    HTTPResponse: the response obtained from the server
    """
    if not validators.url(file_uri):
        raise ValueError(
                            "Wrong URI format for 'file_uri' argument.\
                            Expected an url-like string. Example 'https://export.arxiv.org/api/'"
                        )
    if get_permission_to_request_arxiv(cooldown_manager_uri):
        try:
            response = urllib.request.urlopen(file_uri)
        except urllib.error.HTTPError:
            raise FileNotFoundError("Could not access the provided URI")
        else:
            file = response.read()
            return file
    else:
        # TODO: should be printed as an error in logs rather than throwing an exception
        raise ConnectionRefusedError('CooldownManager refused permission to connect to ArXiv.org')
    

def get_file_object_from_uri(file_uri: str, cooldown_manager_uri:str) -> BytesIO :
    """Return a Python File Object obtained from an URI

    Parameters:
    file_uri (str) : the URI to access the file

    Returns:
    io.BytesIO: File object corresponding to the file being pointed by the URI
    """

    pdf_bytes = request_file_through_uri(file_uri, cooldown_manager_uri)
    pdf_bytesio_file_object = BytesIO()
    pdf_bytesio_file_object.write(pdf_bytes)
    return pdf_bytesio_file_object

# def extract_pdf_raw_data(file_obj:BytesIO, pdf_uri) -> dict:
#     pdf_parser = PDFParser(file_obj)
#     doc = PDFDocument(pdf_parser)

#     # 1. Extract PDF Metadata
#     pdf_metadata = doc.info[0]
#     for (key, value) in doc.info[0].items():
#         # Need to decode each value from bytestrings toward strings
#         pdf_metadata[key] = value.decode("utf-8", errors="ignore")
#     pdf_metadata['uri'] = pdf_uri
#     # 2. Extract PDF content
#     try:
#         pdf_content = extract_text(file_obj)
#     except TypeError:
#         raise TypeError('Something went wrong in the PDF content extraction, due to a bug in pdfminer library')
#     return pdf_metadata, pdf_content

def extract_pdf_content(file_obj:BytesIO) -> str:
    """Return the text content from a PDF File Object

    Parameters:
    file_obj (BytesIO) : the PDF under Python File Object format

    Returns:
    str: Text content of the PDF File Object
    """
    try:
        pdf_content = extract_text(file_obj)
    except TypeError:
        raise TypeError('Something went wrong in the PDF content extraction, due to a bug in pdfminer library')
    return pdf_content

# def extract_data_from_pdf_uri(pdf_uri:str, cooldown_manager_uri:str) -> dict:
#     """Extracts data from a PDF being pointed by a URI
#     Parameters:
#     pdf_uri (str) : the URI through which access the file
#     cooldown_manager_uri (str) : the URI through which ask permission to CooldownManager\
#        to request ArXiv.org services

#     Returns:
#     dict: metadata of the PDF, presented as a JSON structured as follows :
#         {
#             "Producer": "GPL Ghostscript SVN PRE-RELEASE 8.62",
#             "CreationDate": "D:20080203020500-05'00'",
#             "ModDate": "D:20080203020500-05'00'",
#             "Creator": "dvips 5.499 Copyright 1986, 1993 Radical Eye Software",
#             "Title": "dynamic.dvi"
#         }
#     str: PDF content
#     """
#     file_obj = get_file_object_from_uri(pdf_uri, cooldown_manager_uri)
#     pdf_metadata, pdf_content = extract_pdf_raw_data(file_obj, pdf_uri)

#     return pdf_metadata, pdf_content

def extract_references_from_pdf_content(pdf_content:str)->list:
    """Return the references of a PDF

    Parameters:
    pdf_content (str) : the textual content of the PDF 

    Returns:
    list: A list of the references found in the PDF
    """
    references = []
    # TODO: to fill
    return references

def extract_pdf_references(pdf_metadata:dict, cooldown_manager_uri:str) -> dict:
    """Extract the references of a PDF and aggregates them to the PDF metadata

    Parameters:
    pdf_metadata (dict) : the PDF metadata 
    cooldown_manager_uri (str) : the URI through which ask permission to CooldownManager\
        to request ArXiv.org services

    Returns:
    str: Text content of the PDF File Object
    """
    pdf_dict = {
        'uri':pdf_metadata['uri'],
        'authors':pdf_metadata['authors'],
        'title':pdf_metadata['title'],
        # 'date':None,
        'references':None,
    }
    pdf_file_object = get_file_object_from_uri(pdf_metadata['uri'], cooldown_manager_uri)
    pdf_content = extract_pdf_content(pdf_file_object)
    pdf_dict['references'] = extract_references_from_pdf_content(pdf_content)
    
    return pdf_dict