from ai_company_suggester import suggest_companies

def test_suggest_companies_basic():
    resume = {"skills": ["Python", "AI"]}
    try:
        companies = suggest_companies(resume)
        assert isinstance(companies, list)
    except Exception as e:
        assert False, f"suggest_companies raised an exception: {e}"
