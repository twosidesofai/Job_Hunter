def test_log_application():
    from tracker import TrackerAgent
    agent = TrackerAgent()
    job_title = "AI Engineer"
    url = "https://example.com/job/123"
    company = "TechCorp"
    try:
        result = agent.log_application(job_title, url, company)
        assert result is True or result is None
    except Exception as e:
        assert False, f"log_application raised an exception: {e}"
