from copy import deepcopy
import json
import pytest
import time
import threading
import requests


from tests.conftest import (
                        ARXIV_URL,
                        PDF_EXTRACTOR_URL,
                        API_KEY,
                        CAT,
                        MAX_RESULTS,
                        TIME_STEP,
                        MAX_CONCURRENT_REQUEST_THREADS
)

def test_constructor_success(arxiv_parser):
    assert arxiv_parser
    assert arxiv_parser._arxiv_url == ARXIV_URL
    assert arxiv_parser._pdf_extractor_url == PDF_EXTRACTOR_URL
    assert arxiv_parser._api_key == API_KEY
    assert arxiv_parser._cat == CAT
    assert arxiv_parser._max_results == MAX_RESULTS
    assert arxiv_parser._time_step == TIME_STEP
    assert arxiv_parser._max_concurrent_request_threads == MAX_CONCURRENT_REQUEST_THREADS
    assert arxiv_parser._run_thread == None
    assert arxiv_parser._conc_req_num_obs_thread == None
    assert arxiv_parser._stopping == None
    assert arxiv_parser._request_threads_list == []
    assert type(arxiv_parser._fetch_lock) == type(threading.Lock())
    assert type(arxiv_parser._pdfs_data_lock) == type(threading.Lock())
    assert type(arxiv_parser._thread_being_modified_lock) == type(threading.Lock())
    assert type(
        arxiv_parser._run_new_request_thread_permission
        ) == type(arxiv_parser.RunNewRequestThreadPermission())

def test__fetch_atom_feed_from_arxiv_api(arxiv_parser, feed, mocker):
    # Success
    mocker.patch('src.core.arxiv_parser.request.urlopen', return_value = feed)
    assert arxiv_parser._fetch_atom_feed_from_arxiv_api() == feed

def test__extract_pdf_metadatas_from_atom_feed(arxiv_parser, feed, pdf_metadatas_reference):
    # Success
    pdf_metadatas = arxiv_parser._extract_pdf_metadatas_from_atom_feed(feed)
    assert pdf_metadatas == pdf_metadatas_reference

    # Empty atom feed
    pdf_metadatas = arxiv_parser._extract_pdf_metadatas_from_atom_feed(b'svdfvdfv')
    assert pdf_metadatas == []

def test__fetch_new_pdf_data(arxiv_parser, feed, pdf_metadatas_reference, mocker):
    # Success
    mocker.patch(
        'src.core.arxiv_parser.ArXivParser._fetch_atom_feed_from_arxiv_api',
        side_effect = [feed, None]
        )
    expected_feed_extraction_results = [pdf_metadatas_reference[0], pdf_metadatas_reference[1]]
    mocker.patch(
        'src.core.arxiv_parser.ArXivParser._extract_pdf_metadatas_from_atom_feed',
        side_effect = [expected_feed_extraction_results, None]
        )
    expected_extraction_results = deepcopy(expected_feed_extraction_results)
    for i in range(len(expected_extraction_results)):
        expected_extraction_results[i]['references'] = []

    mocker.patch(
        'src.core.arxiv_parser.ArXivParser._process_metadatas_batch'
        )
    mocked_push_to_task_queue = mocker.patch(
        'src.core.arxiv_parser.ArXivParser._push_to_task_queue',
        )
    arxiv_parser._fetch_new_pdf_data()
    mocked_push_to_task_queue.assert_called_once()    

def test__request_extraction(
    arxiv_parser,
    pdf_metadatas_reference,
    pdf_extractor_full_response_reference,
    mocker
    ):
    # Success
    post_mocker = mocker.patch(
        'src.core.arxiv_parser.requests.post',
        return_value = pdf_extractor_full_response_reference
    )
    authenticator = requests.auth.HTTPBasicAuth('api_key', arxiv_parser._api_key)
    mocker.patch(
        'src.core.arxiv_parser.requests.auth.HTTPBasicAuth',
        return_value = authenticator
    )
    pdfs_data = []
    arxiv_parser._request_extraction(pdf_metadatas_reference[0], pdfs_data)
    post_mocker.assert_called_once_with(
        arxiv_parser._pdf_extractor_url,
        data = json.dumps(pdf_metadatas_reference[0], indent=4, sort_keys=True),
        headers={'Content-Type':'application/json'},
        auth=authenticator,
        timeout=120
    )

def test__push_to_task_queue():
    assert True

def test__run(arxiv_parser, mocker):
    def side_effect():
        time.sleep(0.1)
    fetch_mocker = mocker.patch(
                                    'src.core.arxiv_parser.ArXivParser._fetch_new_pdf_data',
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
    mocker.patch('src.core.arxiv_parser.ArXivParser._fetch_new_pdf_data')
    arxiv_parser._time_step = 0.1
    arxiv_parser.start_cron()
    assert arxiv_parser._run_thread.is_alive()
    assert arxiv_parser._conc_req_num_obs_thread.is_alive()
    arxiv_parser.stop_cron()
    assert not arxiv_parser._run_thread
    assert not arxiv_parser._conc_req_num_obs_thread
    assert not arxiv_parser._stopping