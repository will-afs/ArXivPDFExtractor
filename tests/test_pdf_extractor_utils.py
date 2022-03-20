from tests.conftest import (
                        DATA_FILE_PATH,
                        PDF_URI,
                        NOT_FOUND_PDF_URI,
                        NOT_PDF_URI,
                        PDF_DATA_REFERENCE_FILE_NAME,
                        PDF_CONTENT_REFERENCE_FILE_NAME,
                        PDF_METADATA_REFERENCE_FILE_NAME,
                        WRONG_PDF_URI,
                        COOLDOWN_MANAGER_URI
)


from src.pdfextractor.core.pdf_extractor_utils import (
    extract_pdf                                                
)


def test_extract_pdf(pdf_metadatas_reference, references_reference, mocker):
    pdf_metadata_id = 2
    mocker.patch('src.pdfextractor.core.pdf_extractor_utils.get_permission_to_request_arxiv', return_value = True)
    pdf_metadata = extract_pdf(pdf_metadatas_reference[pdf_metadata_id], COOLDOWN_MANAGER_URI)
    
    assert list(pdf_metadata.keys()) == ['uri', 'authors', 'title', 'references']
    assert pdf_metadata['uri'] == pdf_metadatas_reference[pdf_metadata_id]['uri']
    assert pdf_metadata['authors'] == pdf_metadatas_reference[pdf_metadata_id]['authors']
    assert pdf_metadata['title'] == pdf_metadatas_reference[pdf_metadata_id]['title']
    # assert pdf_metadata['references'] == references_reference

# def test_extract_references_from_pdf_content():
#     assert True

