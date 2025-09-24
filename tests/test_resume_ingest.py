from ingest.resume_ingest import ingest_resume

def test_ingest_resume_basic():
    try:
        result = ingest_resume("resume.docx")
        assert isinstance(result, dict)
    except Exception as e:
        assert False, f"ingest_resume raised an exception: {e}"
