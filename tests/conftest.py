""""This file contains setup functions called fixtures that each test will use"""
from src.core.arxiv_parser import (
    ArXivParser,
)

import configparser
import json
import pickle
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
PDF_EXTRACTOR_FULL_RESP_REF_FILE_NAME = config["REFERENCES"]["PDF_EXTRACTOR_FULL_RESP_REF_FILE_NAME"]
APA_RAW_REF_VALUE = config["REFERENCES"]["APA_RAW_REF_VALUE"]
UNKNOWN_RAW_REF_VALUE = config["REFERENCES"]["UNKNOWN_RAW_REF_VALUE"]

# [ArXivParser]
TIME_STEP = int(config["ArXivParser"]["time_step"])
ARXIV_URL = config["ArXivParser"]["arxiv_url"]
CAT = config["ArXivParser"]["cat"]
MAX_RESULTS = int(config["ArXivParser"]["max_results"])
MAX_CONCURRENT_REQUEST_THREADS = int(config["ArXivParser"]["max_concurrent_request_threads"])

# [PDF Extractor]
PDF_EXTRACTOR_URL = config["PDFExtractor"]["pdf_extractor_url"]
API_KEY = config["PDFExtractor"]["api_key"]

@pytest.fixture
def arxiv_parser():
    return ArXivParser(
        arxiv_url = ARXIV_URL,
        pdf_extractor_url = PDF_EXTRACTOR_URL,
        api_key = API_KEY,
        cat = CAT,
        max_results = MAX_RESULTS,
        time_step = TIME_STEP,
        max_concurrent_request_threads = MAX_CONCURRENT_REQUEST_THREADS
        )

@pytest.fixture
def feed():
    with open(DATA_FILE_PATH + FEED_DATA_REFERENCE_FILE_NAME, "rb") as file_feed:
        atom_bytes_feed = file_feed.read()
    return atom_bytes_feed

@pytest.fixture
def pdf_metadatas_reference():
    with open(DATA_FILE_PATH + PDF_METADATAS_REFERENCE_FILE_NAME, "r") as pdf_metadatas_reference_file:
        pdf_metadatas_reference = json.load(pdf_metadatas_reference_file)
    return pdf_metadatas_reference

@pytest.fixture
def clean_references_reference():
    with open(DATA_FILE_PATH + CLEAN_REFERENCES_REFERENCE_FILE_NAME, "r") as clean_references_reference_file:
        clean_references_reference = json.load(clean_references_reference_file)
    return clean_references_reference

@pytest.fixture
def refextract_references_reference():
    with open(DATA_FILE_PATH + REFEXTRACT_REFERENCES_REFERENCE_FILE_NAME, "r") as refextract_references_reference_file:
        refextract_references_reference = json.load(refextract_references_reference_file)
    return refextract_references_reference

@pytest.fixture
def pdf_extractor_full_response_reference():
    with open(DATA_FILE_PATH + PDF_EXTRACTOR_FULL_RESP_REF_FILE_NAME, 'rb') as pdf_extractor_full_resp_ref_file:
        pdf_extractor_full_resp_ref = pickle.load(pdf_extractor_full_resp_ref_file)
    return pdf_extractor_full_resp_ref
