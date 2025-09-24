from exporter import export_resume

def test_export_resume_basic():
    resume = {"name": "John Doe", "skills": ["Python", "AI"]}
    try:
        result = export_resume(resume, "output.docx")
        assert result is True or result is None
    except Exception as e:
        assert False, f"export_resume raised an exception: {e}"
