from src.arxivparser.core.arxiv_parser import (
    ArXivParser,
)

import configparser
from io import BytesIO
import json
import pytest

config = configparser.ConfigParser()
TESTS_DIRECTORY = "./tests"
config.read(TESTS_DIRECTORY + "/setup.cfg")

# [PATHS]
DATA_FILE_PATH = config["PATHS"]["DATA_FILE_PATH"]

# [PDF URIs]
PDF_URI = config["PDF URIs"]["PDF_URI"]
NOT_FOUND_PDF_URI = config["PDF URIs"]["NOT_FOUND_PDF_URI"]
NOT_PDF_URI = config["PDF URIs"]["NOT_PDF_URI"]
WRONG_PDF_URI = config["PDF URIs"]["WRONG_PDF_URI"]


@pytest.fixture
def pdf_bytes():
    with open(DATA_FILE_PATH + PDF_DATA_REFERENCE_FILE_NAME, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    return pdf_bytes
    
@pytest.fixture
def pdf_bytesio():
    with open(DATA_FILE_PATH + PDF_DATA_REFERENCE_FILE_NAME, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    pdf_bytesio_file_object = BytesIO()
    pdf_bytesio_file_object.write(pdf_bytes)
    return pdf_bytesio_file_object

@pytest.fixture
def pdf_content_reference():
    with open(DATA_FILE_PATH + PDF_CONTENT_REFERENCE_FILE_NAME, "r") as pdf_content_reference_file:
        pdf_content_reference = pdf_content_reference_file.read()
    return pdf_content_reference

@pytest.fixture
def pdf_metadata_reference():
    with open(DATA_FILE_PATH + PDF_METADATA_REFERENCE_FILE_NAME, "r") as pdf_metadata_reference_file:
        pdf_metadata_reference = json.load(pdf_metadata_reference_file)
    return pdf_metadata_reference