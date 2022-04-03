from src.core.arxiv_parser import (
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

# [REFERENCES]
PDF_DATA_REFERENCE_FILE_NAME = config["REFERENCES"]["PDF_DATA_REFERENCE_FILE_NAME"]
PDF_CONTENT_REFERENCE_FILE_NAME = config["REFERENCES"]["PDF_CONTENT_REFERENCE_FILE_NAME"]
PDF_METADATA_REFERENCE_FILE_NAME = config["REFERENCES"]["PDF_METADATA_REFERENCE_FILE_NAME"]
FEED_DATA_REFERENCE_FILE_NAME = config["REFERENCES"]["FEED_DATA_REFERENCE_FILE_NAME"]
PDF_METADATAS_REFERENCE_FILE_NAME = config["REFERENCES"]["PDF_METADATAS_REFERENCE_FILE_NAME"]
CLEAN_REFERENCES_REFERENCE_FILE_NAME = config["REFERENCES"]["CLEAN_REFERENCES_REFERENCE_FILE_NAME"]
REFEXTRACT_REFERENCES_REFERENCE_FILE_NAME = config["REFERENCES"]["REFEXTRACT_REFERENCES_REFERENCE_FILE_NAME"]
APA_RAW_REF_VALUE = config["REFERENCES"]["APA_RAW_REF_VALUE"]
UNKNOWN_RAW_REF_VALUE = config["REFERENCES"]["UNKNOWN_RAW_REF_VALUE"]

# [ArXivParser]
TIME_STEP = int(config["ArXivParser"]["time_step"])
ARXIV_URL = config["ArXivParser"]["arxiv_url"]
CAT = config["ArXivParser"]["cat"]
MAX_RESULTS = int(config["ArXivParser"]["max_results"])

# [Cooldown Manager]
COOLDOWN_MANAGER_URI = config['Cooldown Manager']['cooldown_manager_uri']

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