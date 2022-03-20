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
    extract_pdf,
    extract_authors_from_apa_ref                                               
)


def test_extract_pdf(pdf_metadatas_reference, clean_references_reference, refextract_references_reference, mocker):
    pdf_metadata_id = 11
    mocker.patch('src.pdfextractor.core.pdf_extractor_utils.extract_references_from_pdf_uri', return_value = refextract_references_reference)
    pdf_metadata = extract_pdf(pdf_metadatas_reference[pdf_metadata_id], COOLDOWN_MANAGER_URI)
    assert list(pdf_metadata.keys()) == ['uri', 'authors', 'title', 'references']
    assert pdf_metadata['uri'] == pdf_metadatas_reference[pdf_metadata_id]['uri']
    assert pdf_metadata['authors'] == pdf_metadatas_reference[pdf_metadata_id]['authors']
    assert pdf_metadata['title'] == pdf_metadatas_reference[pdf_metadata_id]['title']
    assert pdf_metadata['references'][pdf_metadata_id]['authors'] == [
        'Mitchell, D.',
        'Selman, B.',
        'Levesque, H.'
    ]

def test_extract_authors_from_apa_ref(refextract_references_reference):
    # Pattern to match : ' P. (1990)'
    raw_string = refextract_references_reference[23]['raw_ref'][0]
    assert extract_authors_from_apa_ref(raw_string) == [
        'Minton, S.', 
        'Johnston, M. D.',
        'Philips, A. B.',
        'Laird, P.'
        ]
    # Pattern to match : ' H. (1995b)'
    raw_string = refextract_references_reference[29]['raw_ref'][0]
    assert extract_authors_from_apa_ref(raw_string) == [
        'Selman, B.',
        'Kautz, H.'
    ]

