from src.cooldown_manager_utils import get_permission_to_request_arxiv

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
    # 3 - Clean references
    # 4 - Extract named entities from references
    for reference_dict in extracted_references:
        reference = {
            'title':None, # Not used in current version
            'authors':[]
        }
        try:
            reference_dict['author']
        except: # no author found
            pass
        else:
            # extract each author from string
            reference['authors'].append(extract_authors_from_string(reference_dict['author']))
            pdf_dict['references'].append(reference)
    return pdf_dict

def extract_authors_from_string(authors_string:str)->list:
    """Extract the authors from a string

    Parameters:
    authors_string (str) : the string which might contain authors
    
    Returns:
    list: the list of authors as string elements
    """
    authors = []
    return authors