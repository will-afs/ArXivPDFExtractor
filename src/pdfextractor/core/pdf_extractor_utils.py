from src.cooldown_manager_utils import get_permission_to_request_arxiv

import re
from refextract import extract_references_from_url
import validators

def extract_references_from_pdf_uri(pdf_uri:str, cooldown_manager_uri:str)->list:
    """Return the references of a PDF

    Parameters:
    pdf_uri (str) : the PDF URI

    Returns:
    list: A list of the references found in the PDF
    """
    if not validators.url(pdf_uri):
        raise ValueError(
                            "Wrong URI format for 'pdf_uri' argument.\
                            Expected an url-like string. Example 'http://arxiv.org/pdf/cs/9308101v1'"
                        )
    elif get_permission_to_request_arxiv(cooldown_manager_uri):
        try:
            return extract_references_from_url(pdf_uri)
        except:
            return []
    else:
        raise ConnectionRefusedError('CooldownManager refused permission to connect to ArXiv.org')

def extract_pdf(pdf_metadata:dict, cooldown_manager_uri:str) -> dict:
    """Extract the references of a PDF and aggregates them to the PDF metadata

    Parameters:
    pdf_metadata (dict) : the PDF metadata 
    cooldown_manager_uri (str) : the URI through which ask permission to CooldownManager\
        to request ArXiv.org services

    Returns:
    dict: Text PDF metadata and references as a dictionnary
    """
    # 1 - Initialize the PDF dictionnary to return
    pdf_dict = {
        'uri':pdf_metadata['uri'],
        'authors':pdf_metadata['authors'],
        'title':pdf_metadata['title'],
        'references': [],
    }
    # 2 - Extract references
    extracted_references = extract_references_from_pdf_uri(pdf_metadata['uri'], cooldown_manager_uri)
    # 3 - Extract named entities from references
    for reference_dict in extracted_references:
        reference = {
            'authors':None
        }
        try:
            reference_dict['author']
        except: # no author found
            pass
        else:
            # extract each author from string
            reference['authors'] = extract_authors_from_apa_ref(reference_dict['raw_ref'][0])
            pdf_dict['references'].append(reference)

    return pdf_dict

def extract_authors_from_apa_ref(apa_ref:str)->list:
    """Extract the authors from an APA reference

    Parameters:
    authors_string (str) : the string which might contain authors
    
    Returns:
    list: the list of authors as string elements
    """
    authors = []
    # Searching pattern ' T. (1995)' or ' T. (1995b)' like
    pattern = re.compile(r" [A-Z]\.\ \([1-2][0-9][0-9][0-9][a-z]*\)")
    # 3 = len(' T.'), which should be included in authors_string
    end_authors_section_idx = re.search(pattern, apa_ref, flags=0).start() + 3
    authors_string = apa_ref[0:end_authors_section_idx]
    authors_string = authors_string.replace('& ', '')
    authors_string = authors_string.replace('.,', '..,')
    authors = authors_string.split('., ')
    return authors