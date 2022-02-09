from src.pdfextractor.core.pdf_extractor_utils import (
                                                    get_file_object_from_uri,
                                                    extract_data_from_pdf_uri,                                                   
)

import configparser
from io import BytesIO

import json
import pytest

from pdfminer.pdfparser import PDFSyntaxError

config = configparser.ConfigParser()
TESTS_DIRECTORY = "./tests"
config.read(TESTS_DIRECTORY + "/setup.cfg")

DATA_FILE_PATH = config["PATHS"]["DATA_FILE_PATH"]
PDF_DATA_FILE_NAME = config["PATHS"]["PDF_DATA_FILE_NAME"]
PDF_CONTENT_REFERENCE = config["PATHS"]["PDF_CONTENT_REFERENCE"]
PDF_METADATA_REFERENCE = config["PATHS"]["PDF_METADATA_REFERENCE"]
WRONG_PDF_URI = config["PATHS"]["WRONG_PDF_URI"]
NOT_FOUND_PDF_URI = config["PATHS"]["NOT_FOUND_PDF_URI"]
NOT_PDF_URI = config["PATHS"]["NOT_PDF_URI"]
PDF_URI = config["PATHS"]["PDF_URI"]

def test_get_file_object_from_uri_success(pdf_bytes, mocker):
    # TODO : mock the urlopen function with a dummy PDF
    #mocker.patch('src.pdfextractor.core.pdf_extractor.urllib.request.urlopen', return_value = pdf_bytes)

    # Create File Object from PDF URI
    file_object = get_file_object_from_uri(PDF_URI)
    # Check file_object is of type io.BytesIO
    assert type(file_object) == BytesIO

    # Create File Object from PDF stored locally
    with open(DATA_FILE_PATH + PDF_DATA_FILE_NAME, "rb") as pdf_file:
        pdf_txt = pdf_file.read()
        ref_file_object = BytesIO()
        ref_file_object.write(pdf_txt)
    # Check both File Objects contents are same
    assert file_object.readlines() == ref_file_object.readlines()

def test_get_file_object_from_uri_wrong_uri_format():
    with pytest.raises(ValueError):
        get_file_object_from_uri(WRONG_PDF_URI)

def test_get_file_object_from_uri_not_found_pdf_uri():
    with pytest.raises(FileNotFoundError):
        get_file_object_from_uri(NOT_FOUND_PDF_URI)

def test_extract_data_from_pdf_uri_success():
    extracted_metadata, extracted_content = extract_data_from_pdf_uri(PDF_URI)
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

def test_extract_data_from_pdf_uri_wrong_uri():
    with pytest.raises(ValueError):
        extract_data_from_pdf_uri(WRONG_PDF_URI)

def test_extract_data_from_pdf_uri_not_found():
    with pytest.raises(FileNotFoundError):
        extract_data_from_pdf_uri(NOT_FOUND_PDF_URI)