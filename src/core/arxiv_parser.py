from urllib import request
import requests
import json

from bs4 import BeautifulSoup
import threading
import time
import toml
import validators

from src.core.timer_utils import Timer

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
    pdf_extractor_url : str
        the uri from which PDFExtractor Lambda service can be reached
    api_key : str
        the api key needed to access the PDFExtractor service
    cat : str
        the category of PDFs to fetch from ArXiv
    max_results : int
        the number of max results that can be retrieved 
        per request to ArXiv.org
    time_step : int
        the delay between each time the ArXivParser triggers
    max_concurrent_request_threads : int
        the maximal number possible of simultaneous request threads

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
                    pdf_extractor_url:str='https://qp1s494gph.execute-api.eu-west-3.amazonaws.com/default/PDFExtractor',
                    api_key:str="c0eg58cWwH45sciGATOR27dCcaGMbfPbakyQrrTb",
                    cat:str='cs.ai',
                    max_results:int=1000,
                    time_step:int=604800,
                    max_concurrent_request_threads:int=20
                ):

        self._check_constructor_arguments(
                                        arxiv_url,
                                        pdf_extractor_url,
                                        api_key,
                                        cat,
                                        max_results,
                                        time_step,
                                        max_concurrent_request_threads
                                        )
        self._arxiv_url = arxiv_url
        self._pdf_extractor_url = pdf_extractor_url
        self._api_key = api_key
        self._cat = cat
        self._max_results = int(max_results)
        self._time_step = int(time_step)
        self._max_concurrent_request_threads = int(max_concurrent_request_threads)
        self._run_thread = None
        self._conc_req_num_obs_thread = None
        self._stopping = None
        self._request_threads_list = []
        self._fetch_lock = threading.Lock()
        self._pdfs_data_lock = threading.Lock()
        self._thread_being_modified_lock = threading.Lock()
        self._run_new_request_thread_permission = self.RunNewRequestThreadPermission()
        self._cumulated_number_of_requests = 0
    
    def _check_constructor_arguments(
                                        self,
                                        arxiv_url:str,
                                        pdf_extractor_url:str,
                                        api_key:str,
                                        cat:str,
                                        max_results:int,
                                        time_step:int,
                                        max_concurrent_request_threads:int
                                    ):
        """Check ArXivParser constructor arguments

        Parameters:

        Returns:
        """
        if (not type(arxiv_url) == str or not validators.url(arxiv_url)):
            raise ValueError("Wrong value for 'arxiv_url' argument. Expected an url-like string. Example 'http://www.google.com'")

        if (not type(pdf_extractor_url) == str or not validators.url(pdf_extractor_url)):
            raise ValueError("Wrong value for 'pdf_extractor_url' argument. Expected an url-like string. Example 'http://www.google.com'")

        if (not type(api_key) == str):
            raise ValueError("Wrong value for 'api_key' argument. Expected an string.")

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

        try:
            if (int(max_concurrent_request_threads) <= 0):
                raise ValueError("Wrong value for 'max_concurrent_request_threads' argument. Expected an int value strictly superior to 0") 
        except TypeError:
                raise TypeError("Wrong type for 'max_concurrent_request_threads' argument. Expected an int value strictly superior to 0")

    def start_cron(self):
        """Start ArXivParser bot

        Parameters:

        Returns:
        """
        if not self._run_thread and not self._conc_req_num_obs_thread:
            self._conc_req_num_obs_thread = threading.Thread(
                target=self._observe_concurrent_request_threads_number,
                args=()
            )
            self._conc_req_num_obs_thread.start()
            self._run_thread = threading.Thread(target=self._run, args=())
            self._run_thread.start()
            print("Started ArXivParser bot")

    def stop_cron(self):
        """Stop ArXivParser bot

        Parameters:

        Returns:
        """
        if (self._run_thread and self._run_thread.is_alive()) \
            or (self._conc_req_num_obs_thread and self._conc_req_num_obs_thread.is_alive()):
            self._stopping = True
            self._run_thread.join()
            self._run_thread = None
            self._conc_req_num_obs_thread.join()
            self._conc_req_num_obs_thread = None
            self._stopping = False
            print("Stopped ArXivParser bot")

    def _run(self):
        """Run ArXivParser data fetching loop

        Parameters:

        Returns:
        """
        while not self._stopping:
            with self._fetch_lock:
                self._fetch_new_pdf_data()
            time.sleep(self._time_step)

    def _fetch_new_pdf_data(self):
        """Extract data from ArXiv.org API and push it to a task queue as a JSON

        Parameters:

        Returns:
        """
        last_pdf_in_db_idx = 0 # Could fetch it in a future version

        no_more_pdf_to_fetch = False
        pdfs_data = []
        i=0
        with Timer():
            while not no_more_pdf_to_fetch:
                # Gather atom feed
                atom_bytes_feed = self._fetch_atom_feed_from_arxiv_api(
                                                                        start=last_pdf_in_db_idx+i*self._max_results,
                                                                    )
                # Extract PDF URIs from it
                pdf_metadatas = []
                pdf_metadatas = self._extract_pdf_metadatas_from_atom_feed(atom_bytes_feed)
                if pdf_metadatas:  # Check whether pdf_metadatas is empty or not
                    self._process_metadatas_batch(pdf_metadatas, pdfs_data)
                else:  # Means that there is no more pdf_uri to extract from ArXiv.org API
                    no_more_pdf_to_fetch = True
                i += 1
        # Append them to the task queue
        self._push_to_task_queue(pdfs_data)

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
            
        print("Fetched the following batch of PDFs metadata from ArXiv :\n\
            " +json.dumps(pdf_metadatas, indent=4, sort_keys=True))
        return pdf_metadatas

    class RunNewRequestThreadPermission(threading.Event):
        pass

    def _observe_concurrent_request_threads_number(self):
        """Observe the current number of concurrent request threads
        Whenever it is not reached, triggers the RunNewRequestThreadPermission Event
        Otherwise, unset this Event

        Parameters:

        Returns:
        """
        while not self._stopping:
            thread_count = 0
            for thread in self._request_threads_list:
                with self._thread_being_modified_lock:
                    if not thread.is_alive():
                        self._request_threads_list.remove(thread)
                    else:
                        thread_count += 1
            if thread_count >= self._max_concurrent_request_threads:
                self._run_new_request_thread_permission.clear()
            else:
                self._run_new_request_thread_permission.set()
            time.sleep(1)

    def _process_metadatas_batch(self, pdf_metadatas:list, pdfs_data:list):
        """Populate pdfs_data list by requesting data extraction for each
        PDF in pdf_metadatas batch

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
        pdfs_data (list) : the list of PDF data to append extracted data to
        For example:
        [
            "uri": "http://arxiv.org/pdf/cs/9308102v1",
            "title": "Dynamic Backtracking",
            "authors": [
                "M. L. Ginsberg"
            ]
            "references":
            [
                {
                    "authors": [
                        "Bruynooghe, M."
                    ]
                },
                {
                    "authors": [
                        "Dechter, R.",
                        "Meiri, I."
                    ]
                }
            ]
        ]
        """
        self._request_threads_list = []
        for pdf_metadata in pdf_metadatas:
            time.sleep(3)
            self._run_new_request_thread_permission.wait()
            with self._thread_being_modified_lock:
                thread = threading.Thread(
                    target=self._request_extraction,
                    args=(pdf_metadata, pdfs_data)
                    )
                self._request_threads_list.append(thread)
                thread.start()
        for thread in self._request_threads_list:
            try:
                thread.join()
            except Exception as exc:
                print(str(exc))

    def _request_extraction(self, pdf_metadata:dict, pdfs_data:list):
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
        pdfs_data (list) : the list of PDF data to append extracted data to
        For example:
        [
            "uri": "http://arxiv.org/pdf/cs/9308102v1",
            "title": "Dynamic Backtracking",
            "authors": [
                "M. L. Ginsberg"
            ]
            "references":
            [
                {
                    "authors": [
                        "Bruynooghe, M."
                    ]
                },
                {
                    "authors": [
                        "Dechter, R.",
                        "Meiri, I."
                    ]
                }
            ]
        ]
        """
        print('Requesting extraction for PDF :\n{}'.format(pdf_metadata))
        full_response = requests.post(
            self._pdf_extractor_url,
            data=json.dumps(pdf_metadata, indent=4, sort_keys=True),
            headers={'Content-Type':'application/json'},
            auth = requests.auth.HTTPBasicAuth('apikey', self._api_key),
            timeout = 120
        )
        pdf_extractor_response = full_response.json()
        print('Received response from PDFExtractor :\n{}'.format(pdf_extractor_response))
        exc_log = {
            "uri":pdf_metadata['uri'],
            "status":'',
            "full_response":'',
        }
        with open('results/execution_logs.json', 'a') as logs_file:
            try:
                status = pdf_extractor_response['status']
            except KeyError:
                print(
                    'Something went wrong when requesting PDFExtractor API:\n\
                        {}'.format(json.dumps(pdf_extractor_response, indent=4, sort_keys=True))
                    )
                exc_log['status'] = "Failure"
            else:
                if status != 200:
                    print(
                        'Something went wrong when requesting PDFExtractor API:\n\
                            {}'.format(json.dumps(pdf_extractor_response, indent=4, sort_keys=True))
                        )
                    exc_log['status'] = "Failure"
                else:
                    with self._pdfs_data_lock:
                        pdfs_data.append(pdf_extractor_response['body'])
                    exc_log['status'] = "Success"
            exc_log['full_response'] = pdf_extractor_response
            logs_file.write(",\n"+json.dumps(exc_log, indent=4, sort_keys=True))
    

    def _push_to_task_queue(self, pdfs_data:dict):
        with open('results/metastructure.json', 'w') as json_file:
            json_file.write(json.dumps(pdfs_data, indent=4, sort_keys=True))
        #TODO: Push directly to task queue instead of saving in file
        # celery_app.send_task('fetch_data', kwargs={'url': request.json['url']})
        # task_function_name.delay(args)
        print('\n\n\nPushed to task queue the following JSON structure:\n{}'.format(pdfs_data))


if __name__ == '__main__':
    config = toml.load('settings/config.toml')
    arxiv_url = config['ArXivParser']['arxiv_url']
    pdf_extractor_url = config['PDFExtractor']['pdf_extractor_url']
    from dotenv import load_dotenv
    import os
    load_dotenv()
    api_key = os.getenv('API_KEY')
    cat = config['ArXivParser']['cat']
    max_results = config['ArXivParser']['max_results']
    time_step = config['ArXivParser']['time_step']
    max_concurrent_request_threads = config['ArXivParser']['max_concurrent_request_threads']

    arxiv_parser = ArXivParser(
        arxiv_url = arxiv_url,
        pdf_extractor_url = pdf_extractor_url,
        api_key = api_key,
        cat = cat,
        max_results = max_results,
        time_step = time_step,
        max_concurrent_request_threads = max_concurrent_request_threads
    )
    arxiv_parser.start_cron()
