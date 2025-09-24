from ingest.schema import ResumeProfile

def test_resume_profile_init():
    try:
        profile = ResumeProfile(name="John Doe", skills=["Python", "AI"])
        assert profile.name == "John Doe"
    except Exception as e:
        assert False, f"ResumeProfile init raised an exception: {e}"
