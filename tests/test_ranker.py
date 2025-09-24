from match.ranker import rank_jobs

def test_rank_jobs_basic():
    jobs = [{"title": "AI Engineer", "skills": ["Python", "AI"]}]
    profile = {"skills": ["Python", "AI"]}
    ranked = rank_jobs(jobs, profile)
    assert isinstance(ranked, list)
 