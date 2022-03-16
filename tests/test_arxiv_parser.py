import pytest

import time
import threading

from tests.conftest import (
                        TIME_STEP,
                        ARXIV_URL,
                        CAT,
                        MAX_RESULTS,
                        COOLDOWN_MANAGER_URI
)

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

def test__fetch_atom_feed_from_arxiv_api(arxiv_parser, feed, mocker):
    # Success
    mocker.patch('src.arxivparser.core.arxiv_parser.get_permission_to_request_arxiv', return_value = True)
    mocker.patch('src.arxivparser.core.arxiv_parser.urllib.request.urlopen', return_value = feed)
    assert arxiv_parser._fetch_atom_feed_from_arxiv_api() == feed

    # Failure : no permission from Cooldown Manager
    mocker.patch('src.arxivparser.core.arxiv_parser.get_permission_to_request_arxiv', return_value = False)
    with pytest.raises(ConnectionRefusedError):
        arxiv_parser._fetch_atom_feed_from_arxiv_api()

def test__extract_pdf_metadatas_from_atom_feed(arxiv_parser, feed, pdf_metadatas_reference):
    # Success
    pdf_metadatas = arxiv_parser._extract_pdf_metadatas_from_atom_feed(feed)
    assert pdf_metadatas == pdf_metadatas_reference

    # Empty atom feed
    pdf_metadatas = arxiv_parser._extract_pdf_metadatas_from_atom_feed(b'svdfvdfv')
    assert pdf_metadatas == []

def test_fetch_new_pdf_metadatas(arxiv_parser, feed, mocker):
    # Success
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._fetch_atom_feed_from_arxiv_api', return_value = feed)
    mocked_push_to_task_queue = mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser._push_to_task_queue')
    fetch_thread = threading.Thread(target=arxiv_parser.fetch_new_pdf_metadatas, args=())
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
                                    'src.arxivparser.core.arxiv_parser.ArXivParser.fetch_new_pdf_metadatas',
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
    mocker.patch('src.arxivparser.core.arxiv_parser.ArXivParser.fetch_new_pdf_metadatas')
    arxiv_parser._time_step = 0.1
    arxiv_parser.start_cron()
    assert arxiv_parser._run_thread.is_alive()
    arxiv_parser.stop_cron()
    assert not arxiv_parser._run_thread
    assert not arxiv_parser._stopping