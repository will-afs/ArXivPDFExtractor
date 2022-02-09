""""This file contains setup functions called fixtures that each test will use"""
from src.arxivparser.core.arxiv_parser import (
    ArXivParser,
)

import configparser
import pytest


config = configparser.ConfigParser()
TESTS_DIRECTORY = "./tests"
config.read(TESTS_DIRECTORY + "/setup.cfg")

# [PATHS]
DATA_FILE_PATH = config["PATHS"]["DATA_FILE_PATH"]
PDF_DATA_FILE_NAME = config["PATHS"]["PDF_DATA_FILE_NAME"]
PDF_CONTENT_REFERENCE = config["PATHS"]["PDF_CONTENT_REFERENCE"]
PDF_METADATA_REFERENCE = config["PATHS"]["PDF_METADATA_REFERENCE"]
PDF_URI = config["PATHS"]["PDF_URI"]
NOT_FOUND_PDF_URI = config["PATHS"]["NOT_FOUND_PDF_URI"]
NOT_PDF_URI = config["PATHS"]["NOT_PDF_URI"]
WRONG_PDF_URI = config["PATHS"]["WRONG_PDF_URI"]
FEED_DATA_FILE_NAME = config["PATHS"]["FEED_DATA_FILE_NAME"]
REFERENCE_PDF_URIS_FILE_NAME = config["PATHS"]["REFERENCE_PDF_URIS_FILE_NAME"]

# [ArXivParser]
TIME_STEP = int(config["ArXivParser"]["time_step"])
ARXIV_URL = config["ArXivParser"]["arxiv_url"]
CAT = config["ArXivParser"]["cat"]
MAX_RESULTS = int(config["ArXivParser"]["max_results"])

# [Cooldown Manager]
COOLDOWN_MANAGER_URI = config['Cooldown Manager']['cooldown_manager_uri']


@pytest.fixture
def arxiv_parser():
    return ArXivParser(ARXIV_URL, CAT, MAX_RESULTS, COOLDOWN_MANAGER_URI, TIME_STEP)

@pytest.fixture
def feed():
    with open(DATA_FILE_PATH + FEED_DATA_FILE_NAME, "rb") as file_feed:
        atom_bytes_feed = file_feed.read()
    return atom_bytes_feed

@pytest.fixture
def reference_pdf_uris():
    with open(DATA_FILE_PATH + REFERENCE_PDF_URIS_FILE_NAME, "r") as reference_pdf_uris_file:
        reference_pdf_uris = [pdf_uri.replace('\n', '') for pdf_uri in reference_pdf_uris_file.readlines()] 
    return reference_pdf_uris

@pytest.fixture
def pdf_bytes():
    with open(DATA_FILE_PATH + PDF_DATA_FILE_NAME, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    return pdf_bytes
