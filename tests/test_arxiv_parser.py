import configparser

import pytest

import time
import threading

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

def test_constructor_success(arxiv_parser):
    assert arxiv_parser
    assert arxiv_parser._arxiv_url == ARXIV_URL
    assert arxiv_parser._cat == CAT
    assert arxiv_parser._max_results == MAX_RESULTS
    assert arxiv_parser._cooldown_manager_uri == COOLDOWN_MANAGER_URI
    assert arxiv_parser._time_step == TIME_STEP
    assert arxiv_parser._run_thread == None
    assert arxiv_parser._stopping == None
    assert type(arxiv_parser._fetch_lock) == type(threading.Lock())
    assert arxiv_parser._stopping == None

def test__get_permission_to_request_arxiv(arxiv_parser, mocker):
    # Success
    mocker.patch('src.arxivparser.core.arxiv_parser.urllib.request.urlopen', return_value = True)
    assert arxiv_parser._get_permission_to_request_arxiv()
    # Failure
    mocker.patch('src.arxivparser.core.arxiv_parser.urllib.request.urlopen', return_value = False)
    assert not arxiv_parser._get_permission_to_request_arxiv()

def test__fetch_atom_feed_from_arxiv_api(arxiv_parser, feed, mocker):
    # Success
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._get_permission_to_request_arxiv', return_value = True)
    mocker.patch('src.arxivparser.core.arxiv_parser.urllib.request.urlopen', return_value = feed)
    assert arxiv_parser._fetch_atom_feed_from_arxiv_api() == feed

    # Failure
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._get_permission_to_request_arxiv', return_value = False)
    with pytest.raises(ConnectionRefusedError):
        arxiv_parser._fetch_atom_feed_from_arxiv_api()

def test__extract_pdf_uris_from_atom_feed(arxiv_parser, feed, reference_pdf_uris):
    # Success
    pdf_uris = arxiv_parser._extract_pdf_uris_from_atom_feed(feed)
    assert pdf_uris == reference_pdf_uris

    # Empty atom feed
    pdf_uris = arxiv_parser._extract_pdf_uris_from_atom_feed(b'svdfvdfv')
    assert pdf_uris == []

def test_fetch_new_pdf_uris(arxiv_parser, feed, mocker):
    # Success
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._fetch_atom_feed_from_arxiv_api', return_value = feed)
    mocked_push_to_task_queue = mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._push_to_task_queue')
    fetch_thread = threading.Thread(target=arxiv_parser.fetch_new_pdf_uris, args=())
    fetch_thread.start()
    while not mocked_push_to_task_queue.call_count >= 1:
        time.sleep(0.1)
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._fetch_atom_feed_from_arxiv_api', return_value = b'svdfvdfv')
    assert mocked_push_to_task_queue.call_count >= 1
    fetch_thread.join(0.5) # Let some time to the join to terminate
    assert not fetch_thread.is_alive()
    

def test__run(arxiv_parser, mocker):
    def side_effect():
        time.sleep(0.1)
    fetch_mocker = mocker.patch(
                                    'src.arxivparser.core.arxiv_parser.ArXivParser.fetch_new_pdf_uris',
                                    side_effect = side_effect
                                )
    arxiv_parser._time_step = 0
    run_thread = threading.Thread(target=arxiv_parser._run, args=())
    run_thread.start()
    time.sleep(0.3)
    arxiv_parser._stopping = True
    assert fetch_mocker.call_count >= 1
    run_thread.join(0.5)
    assert not run_thread.is_alive()


def test_start_stop_cron(arxiv_parser, mocker):
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser.fetch_new_pdf_uris')
    arxiv_parser._time_step = 0.1
    arxiv_parser.start_cron()
    assert arxiv_parser._run_thread.is_alive()
    arxiv_parser.stop_cron()
    assert not arxiv_parser._run_thread
    assert not arxiv_parser._stopping