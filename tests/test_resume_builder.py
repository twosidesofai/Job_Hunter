def test_build_resume_basic():
    from resume_builder import KeywordResumeBuilderAgent
    master_resume_path = "master_resume.json"  # Use a test path or mock
    job_posting = {"title": "AI Engineer", "keywords": ["AI", "Python"]}
    builder = KeywordResumeBuilderAgent()
    # You may need to mock file reading if build_resume expects a file
    try:
        tailored = builder.build_resume(job_posting, master_resume_path)
        assert isinstance(tailored, dict)
    except Exception as e:
        assert False, f"build_resume raised an exception: {e}"
