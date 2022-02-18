from tests.conftest import (
                        DATA_FILE_PATH,
                        PDF_DATA_FILE_NAME,
                        PDF_CONTENT_REFERENCE,
                        PDF_METADATA_REFERENCE,                    
                        PDF_URI,
                        NOT_FOUND_PDF_URI,
                        NOT_PDF_URI,
                        WRONG_URI,
                        FEED_DATA_FILE_NAME,
                        REFERENCE_PDF_URIS_FILE_NAME,
                        COOLDOWN_MANAGER_URI
)


from src.pdfextractor.core.pdf_extractor_utils import (
                                                    get_file_object_from_uri,
                                                    extract_data_from_pdf_uri,
                                                    extract_pdf_raw_data,                                                   
)

from io import BytesIO

import json
import pytest

def test_get_file_object_from_uri_success(pdf_bytes, mocker):
    mocker.patch('src.pdfextractor.core.pdf_extractor_utils.request_file_through_uri', return_value = pdf_bytes)
    # Create File Object from PDF URI
    file_object = get_file_object_from_uri(PDF_URI, COOLDOWN_MANAGER_URI)
    # Check file_object is of type io.BytesIO
    assert type(file_object) == BytesIO

    # Create File Object from PDF stored locally
    with open(DATA_FILE_PATH + PDF_DATA_FILE_NAME, "rb") as pdf_file:
        pdf_txt = pdf_file.read()
        ref_file_object = BytesIO()
        ref_file_object.write(pdf_txt)
    # Check both File Objects contents are same
    assert file_object.getvalue() == ref_file_object.getvalue()

def test_get_file_object_from_uri_wrong_uri_format(mocker):
    with pytest.raises(ValueError):
        mocker.patch('src.pdfextractor.core.pdf_extractor_utils.get_permission_to_request_arxiv', return_value = True)
        get_file_object_from_uri(WRONG_URI, COOLDOWN_MANAGER_URI)

def test_get_file_object_from_uri_not_found_pdf_uri(mocker):
    with pytest.raises(FileNotFoundError):
        mocker.patch('src.pdfextractor.core.pdf_extractor_utils.get_permission_to_request_arxiv', return_value = True)
        get_file_object_from_uri(NOT_FOUND_PDF_URI, COOLDOWN_MANAGER_URI)

def test_extract_data_from_pdf_uri_success(pdf_bytes, mocker):
    mocker.patch('src.pdfextractor.core.pdf_extractor_utils.request_file_through_uri', return_value = pdf_bytes)
    extracted_metadata, extracted_content = extract_data_from_pdf_uri(PDF_URI, COOLDOWN_MANAGER_URI)
    # Checks metadata
    with open(
        DATA_FILE_PATH + PDF_METADATA_REFERENCE, "r"
    ) as pdf_metadata_reference_file:
        reference_metadata = json.load(pdf_metadata_reference_file)
    assert extracted_metadata == reference_metadata
    # Checks content
    with open(
        DATA_FILE_PATH + PDF_CONTENT_REFERENCE, "r"
    ) as pdf_content_reference_file:
        reference_content = pdf_content_reference_file.read()
    assert extracted_content == reference_content

def test_extract_data_from_pdf_uri_wrong_uri(mocker):
    mocker.patch('src.pdfextractor.core.pdf_extractor_utils.get_permission_to_request_arxiv', return_value = True)
    with pytest.raises(ValueError):
        extract_data_from_pdf_uri(WRONG_URI, COOLDOWN_MANAGER_URI)

def test_extract_data_from_pdf_uri_not_found(mocker):
    mocker.patch('src.pdfextractor.core.pdf_extractor_utils.get_permission_to_request_arxiv', return_value = True)
    with pytest.raises(FileNotFoundError):
        extract_data_from_pdf_uri(NOT_FOUND_PDF_URI, COOLDOWN_MANAGER_URI)

def test_extract_pdf_raw_data(pdf_bytesio, pdf_content_reference, pdf_metadata_reference):
    extracted_metadata, extracted_content = extract_pdf_raw_data(pdf_bytesio, PDF_URI)
    assert extracted_metadata == pdf_metadata_reference
    assert extracted_content == pdf_content_reference