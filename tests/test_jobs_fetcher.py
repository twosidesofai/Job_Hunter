def test_fetch_jobs_returns_list():
    from jobs_fetcher import AdzunaAgent
    agent = AdzunaAgent()
    keywords = "Engineer"
    location = "Remote"
    filters = {}
    try:
        jobs = agent.fetch_jobs(keywords, location, filters)
        assert isinstance(jobs, list)
    except Exception as e:
        assert False, f"fetch_jobs raised an exception: {e}"
