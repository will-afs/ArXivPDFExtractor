from src.pdfextractor.core.pdf_extractor_utils import extract_data_from_pdf_uri

import celery
import toml
from typing import List

config = toml.load('settings/config.toml')
broker_url = config['PDFExtractor']['broker_url']
# backend_url = config['PDFExtractor']['backend_url']

app = celery.Celery(
                'pdf_extractor',
                broker=broker_url,
                # backend=backend_url,
            )

@app.task
def extract_data_from_pdf_uri_task(pdf_uri:str) -> List:
    print("Task called with argument : " + pdf_uri)
    # return extract_data_from_pdf_uri(pdf_uri)

if __name__ == '__main__':
    app.start()