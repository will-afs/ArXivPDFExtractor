from src.pdfextractor.core.pdf_extractor_utils import extract_pdf

import celery
import json
from os import path
import sys
import toml
from typing import List

config = toml.load('settings/config.toml')
broker_url = config['PDFExtractor']['broker_url']
backend_url = config['PDFExtractor']['backend_url']
cooldown_manager_uri = config['Cooldown Manager']['cooldown_manager_uri']

app = celery.Celery(
                'pdf_extractor',
                broker=broker_url,
                backend=backend_url,
            )

@app.task
def extract_pdf_task(pdf_metadata:dict, erase_file=True) -> List:
    pdf_urn = pdf_metadata['uri'].replace('http://arxiv.org/pdf/cs/', '')
    if not erase_file and (path.exists('results/errors/'+pdf_urn) or path.exists('results/success/'+pdf_urn)):
        return 'File \"' + pdf_urn + '\" alredy exists'
    else:
        # try:
        pdf_dict = extract_pdf(pdf_metadata, cooldown_manager_uri)
        # except AuthorsExtractionError as err:
        #     # Storing the pdf_metadata that lead to an error to debug it
        #     pdf_metadata['unsupported_raw_ref'] = str(err)
        #     json_object = json.dumps(pdf_metadata, indent = 4)
        #     with open("results/errors.json".format(pdf_urn), "a") as outfile:
        #         outfile.write(json_object)
        #     return '\nExtraction failed for PDF with metadata \"' + json.dumps(pdf_metadata) + '\"\n'
        json_object = json.dumps(pdf_dict, indent = 4)
        with open("results/success/{}.json".format(pdf_urn), "w") as outfile:
            outfile.write(json_object)
        return 'Successfuly extracted PDF with URN \"' + pdf_urn + '\"'

if __name__ == '__main__':
    app.start()
