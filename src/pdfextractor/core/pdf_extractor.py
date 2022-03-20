from src.pdfextractor.core.pdf_extractor_utils import extract_pdf

import celery
import json
import toml
from typing import List

config = toml.load('settings/config.toml')
broker_url = config['PDFExtractor']['broker_url']
# backend_url = config['PDFExtractor']['backend_url']
cooldown_manager_uri = config['Cooldown Manager']['cooldown_manager_uri']

app = celery.Celery(
                'pdf_extractor',
                broker=broker_url,
                # backend=backend_url,
            )

@app.task
def extract_pdf_task(pdf_metadata:dict) -> List:
    # print("Task called with argument : " + pdf_metadata['uri'])
    pdf_urn = pdf_metadata['uri'].replace('http://arxiv.org/pdf/cs/', '')
    try:
        pdf_dict = extract_pdf(pdf_metadata, cooldown_manager_uri)
    except:
        return 'Extraction failed for PDF with URN \"' + pdf_urn + '\"'
    json_object = json.dumps(pdf_dict, indent = 4)
    with open("results/{}.json".format(pdf_urn), "w") as outfile:
        outfile.write(json_object)
    return 'Successfuly extracted PDF with URN \"' + pdf_urn + '\"'

if __name__ == '__main__':
    app.start()
