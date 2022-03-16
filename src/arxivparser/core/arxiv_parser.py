from src.cooldown_manager_utils import get_permission_to_request_arxiv
from src.pdfextractor.core.pdf_extractor import extract_pdf_references_task

import urllib.request

from bs4 import BeautifulSoup
import threading
import time
from timeit import default_timer as timer
import toml
import validators


class ArXivParser():
    def __init__(
                    self,
                    arxiv_url:str='https://export.arxiv.org/api/',
                    cat:str='cs.ai',
                    max_results:int=1000,
                    cooldown_manager_uri:str='http://172.17.0.2:5000/',
                    time_step:int=604800
                ):

        self._check_constructor_arguments(
                                        arxiv_url,
                                        cat,
                                        max_results,
                                        cooldown_manager_uri,
                                        time_step
                                        )
        self._arxiv_url = arxiv_url
        self._cooldown_manager_uri = cooldown_manager_uri
        self._cat = cat
        self._max_results = int(max_results)
        self._time_step = int(time_step)
        self._run_thread = None
        self._stopping = None
        self._fetch_lock = threading.Lock()
    
    def _check_constructor_arguments(
                                        self,
                                        arxiv_url,
                                        cat,
                                        max_results,
                                        cooldown_manager_uri:str="http://172.17.0.2:5000/",
                                        time_step:int=604800
                                    ):
        # TODO: to test
        if (not type(arxiv_url) == str or not validators.url(arxiv_url)):
            raise ValueError("Wrong value for 'arxiv_url' argument. Expected an url-like string. Example 'http://www.google.com'")

        if (not type(cooldown_manager_uri) == str or not validators.url(cooldown_manager_uri)):
            raise ValueError("Wrong value for 'cooldown_manager_uri' argument. Expected an url-like string. Example 'http://172.17.0.2:5000/'")

        possible_cat_values = ['cs.ai',]
        if (not type(cat) == str or not cat in possible_cat_values):
            raise ValueError("Wrong value for 'cat' argument : should be one of these possible values : {}".format(possible_cat_values))            

        try:
            if (int(max_results) > 1000):
                raise ValueError("Wrong value for 'max_results' argument. Expected an int value inferior to 1000")
        except TypeError:
                raise TypeError("Wrong type for 'max_results' argument. Expected an int value inferior to 1000")

        try:
            if (int(time_step) <= 0):
                raise ValueError("Wrong value for 'time_step' argument. Expected an int value strictly superior to 0") 
        except TypeError:
                raise TypeError("Wrong type for 'time_step' argument. Expected an int value strictly superior to 0")

    def _fetch_atom_feed_from_arxiv_api(
                                            self,
                                            start:int=0,
                                        ) -> bytes:
        """Fetch Atom feed from ArXiv.org API
        
        Parameters:
        start (int) : the starting index from which fetch the PDFs from ArXiv.org.

        Returns:
        bytes : the Atom bytes feed returned from ArXiv.org API
        """

        query = "query?search_query=cat:{}&start={}&max_results={}&sortBy=lastUpdatedDate&sortOrder=ascending".format(
            self._cat, start, self._max_results
        )
        uri = self._arxiv_url + query
        if get_permission_to_request_arxiv(self._cooldown_manager_uri):
            bytes_feed = urllib.request.urlopen(uri)
            return bytes_feed
        else:
            raise ConnectionRefusedError('CooldownManager refused permission to connect to ArXiv.org')

    def _extract_pdf_metadatas_from_atom_feed(self, feed: bytes) -> list:
        """Extract PDF URIs and authors from an Atom feed

        Parameters:
        feed (bytes) : the Atom bytes feed from which extract PDF URIs

        Returns:
        list : List of PDF URI and authors as dict
        """
        
        soup = BeautifulSoup(feed, features="html.parser")
        pdf_metadatas = []
        results = soup.find_all("entry")
        for result in results:
            pdf_metadata = {
                'uri':None,
                'title':None,
                'authors':[],
            }
            # Extract pdf uri
            links = result.find_all("link")
            for link in links:
                if link.get("title") == "pdf":
                    pdf_metadata['uri']  = link.get("href")
            
            # Extract authors
            authors_names = []
            authors_tags = result.find_all("author")
            for author_tag in authors_tags:
                pdf_metadata['authors'].append(author_tag.find("name").next)

            # Extract title
            pdf_metadata['title'] = result.find("title").next

            pdf_metadatas.append(pdf_metadata)
            
        return pdf_metadatas

    def _push_to_task_queue(self, pdf_uri):
        extract_data_from_pdf_uri_task.delay(pdf_uri)

    def fetch_new_pdf_metadatas(self):
        """Fetch new PDF URIs and authors from ArXiv.org API \
            and creates tasks for each one of them to extract them asynchronously 

        Parameters:

        Returns:
        """
        # Look for index of last PDF in database
        # TODO : fetch it
        last_pdf_in_db_idx = 0

        no_more_pdf_to_fetch = False
        i=0
        while not no_more_pdf_to_fetch:
            # Gather atom feed
            atom_bytes_feed = self._fetch_atom_feed_from_arxiv_api(
                                                                    start=last_pdf_in_db_idx+i*self._max_results,
                                                                )

            # Extract PDF URIs from it
            pdf_metadatas = self._extract_pdf_metadatas_from_atom_feed(atom_bytes_feed)

            # Append them to the task queue
            if pdf_metadatas:  # Check whether pdf_metadatas is empty or not
                # add them to the task queue
                for pdf_metadata in pdf_metadatas:
                    self._push_to_task_queue(pdf_metadata)
            else:  # Means that there is no more pdf_uri to extract from ArXiv.org API
                no_more_pdf_to_fetch = True
        no_more_pdf_to_fetch = False
    
    def _run(self):
        while not self._stopping:
            with self._fetch_lock:
                self.fetch_new_pdf_metadatas()
            time.sleep(self._time_step)

    def start_cron(self):
        if not self._run_thread:
            self._run_thread = threading.Thread(target=self._run, args=())
            self._run_thread.start()

    def stop_cron(self):
        if self._run_thread and self._run_thread.is_alive():
            self._stopping = True
            self._run_thread.join()
            self._run_thread = None
            self._stopping = False


if __name__ == '__main__':
    config = toml.load('settings/config.toml')
    arxiv_url = config['ArXivParser']['arxiv_url']
    cat = config['ArXivParser']['cat']
    max_results = config['ArXivParser']['max_results']
    cooldown_manager_uri = config['Cooldown Manager']['cooldown_manager_uri']
    time_step = config['ArXivParser']['time_step']

    arxiv_parser = ArXivParser(arxiv_url, cat, max_results, cooldown_manager_uri, time_step)
    arxiv_parser.start_cron()
