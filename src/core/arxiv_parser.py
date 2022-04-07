from urllib import request
import requests
import json

from bs4 import BeautifulSoup
import threading
import time
from timeit import default_timer as timer
import toml
import validators


class ArXivParser():
    """
    Process scientific articles (PDFs) available on ArXiv.org.

    ArXivParser fetches periodically batches PDF metadata, from ArXiv.org Open API.
    For each PDF metadata fetched, it delegates further data extraction 
    to a PDFExtractor Lambda service.
    Whenever the data of all the PDF fetched from ArXiv are extracted,
    ArXivParser makes an agregated JSON structure of them, and send it to a
    Redis Task Queue for populating an Ontology.

    ...

    Attributes
    ----------
    arxiv_url : str
        the url from which ArXiv.org can be reached
    cat : str
        the category of PDFs to fetch from ArXiv
    max_results : int
        the number of max results that can be retrieved 
        per request to ArXiv.org
    pdf_extractor_uri : str
        the uri from which PDFExtractor Lambda service can be reached 
    time_step : int
        the delay between each time the ArXivParser triggers

    Methods
    -------
    start_cron():
        Start the ArXivParser scheduler
    stop_cron():
        Stop the ArXivParser scheduler
    """
    def __init__(
                    self,
                    arxiv_url:str='https://export.arxiv.org/api/',
                    cat:str='cs.ai',
                    max_results:int=1000,
                    pdf_extractor_uri:str='https://lbninhtxlc.execute-api.eu-west-3.amazonaws.com/beta/test-function',
                    time_step:int=604800
                ):

        self._check_constructor_arguments(
                                        arxiv_url,
                                        cat,
                                        max_results,
                                        pdf_extractor_uri,
                                        time_step
                                        )
        self._arxiv_url = arxiv_url
        self._pdf_extractor_uri = pdf_extractor_uri
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
                                        pdf_extractor_uri:str='https://lbninhtxlc.execute-api.eu-west-3.amazonaws.com/beta/test-function',
                                        time_step:int=604800
                                    ):
        if (not type(arxiv_url) == str or not validators.url(arxiv_url)):
            raise ValueError("Wrong value for 'arxiv_url' argument. Expected an url-like string. Example 'http://www.google.com'")

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

    def _run(self):
        while not self._stopping:
            with self._fetch_lock:
                self._fetch_new_pdf_data()
            time.sleep(self._time_step)

    def _fetch_new_pdf_data(self):
        """Extract data from ArXiv.org API and push it to a task queue as a JSON

        Parameters:

        Returns:
        """
        # Look for index of last PDF in database
        last_pdf_in_db_idx = 43000 # Could fetch it in a future version

        no_more_pdf_to_fetch = False
        i=0
        pdfs_data = []
        while not no_more_pdf_to_fetch:
            # Gather atom feed
            atom_bytes_feed = self._fetch_atom_feed_from_arxiv_api(
                                                                    start=last_pdf_in_db_idx+i*self._max_results,
                                                                )
            # Extract PDF URIs from it
            pdf_metadatas = []
            pdf_metadatas = self._extract_pdf_metadatas_from_atom_feed(atom_bytes_feed)
            if pdf_metadatas:  # Check whether pdf_metadatas is empty or not
                # Delegate further data extraction to PDFExtractor
                for pdf_metadata in pdf_metadatas:
                    pdfs_data.append(self._request_extraction(pdf_metadata))
            else:  # Means that there is no more pdf_uri to extract from ArXiv.org API
                no_more_pdf_to_fetch = True
        # Append them to the task queue
        self._push_to_task_queue(pdfs_data)
        print("Pushed to Redis task queue the following JSON:\n".format(pdfs_data))

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
        bytes_feed = request.urlopen(uri)
        return bytes_feed

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
            authors_tags = result.find_all("author")
            for author_tag in authors_tags:
                pdf_metadata['authors'].append(author_tag.find("name").next)

            # Extract title
            pdf_metadata['title'] = result.find("title").next

            pdf_metadatas.append(pdf_metadata)
            
        return pdf_metadatas

    def _request_extraction(self, pdf_metadata:dict)->dict:
        """Request PDFExtractor Lambda service for extracting PDF data

        Parameters:
        pdf_metadata (dict) : the metadata of the PDF from which extract further data
            For example:
            {
                "uri": "http://arxiv.org/pdf/cs/9308102v1",
                "title": "Dynamic Backtracking",
                "authors": [
                    "M. L. Ginsberg"
                ]
            }

        Returns:
        dict : the refined data from the PDF
            For example:
            {
                "uri": "http://arxiv.org/pdf/cs/9308102v1",
                "title": "Dynamic Backtracking",
                "authors": [
                    "M. L. Ginsberg"
                ]
                "references":
                [
                    {
                        "title": "Solving combinatorial search problems by intelligent backtracking",
                        "authors": [
                            "Bruynooghe, M."
                        ]
                    },
                    {
                        "title": "Experimental evaluation of preprocessing techniques in constraint satisfaction problems",
                        "authors": [
                            "Dechter, R.",
                            "Meiri, I."
                        ]
                    }
                ]
            }
        """
        url = self._pdf_extractor_uri
        headers = {'Content-Type':'application/json'}
        data = pdf_metadata
        print('Requesting extraction for PDF :\n{}'.format(pdf_metadata))
        full_response = requests.post(url, data=json.dumps(data), headers=headers)
        print('Received answer:\n{}\n'.format(full_response))
        pdf_extractor_response = full_response.json()
        if pdf_extractor_response['statusCode'] != 200:
            print(
                'Something went wrong when requesting PDFExtractor API:\n\
                    {}'.format(json.dumps(pdf_extractor_response))
                )
        else:
            return pdf_extractor_response['body']

    def _push_to_task_queue(self, pdfs_data:dict):
        print('\n\n\nPushed to task queue the following JSON structure:\n{}'.format(pdfs_data))
        #celery_app.send_task('fetch_data', kwargs={'url': request.json['url']})
        # task_function_name.delay(args)
        pass


if __name__ == '__main__':
    config = toml.load('settings/config.toml')
    arxiv_url = config['ArXivParser']['arxiv_url']
    cat = config['ArXivParser']['cat']
    max_results = config['ArXivParser']['max_results']
    pdf_extractor_uri = config['PDFExtractor']['pdf_extractor_uri']
    time_step = config['ArXivParser']['time_step']

    arxiv_parser = ArXivParser(arxiv_url, cat, max_results, pdf_extractor_uri, time_step)
    arxiv_parser.start_cron()
