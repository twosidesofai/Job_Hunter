from job_search_ui import JobSearchUI

def test_job_search_ui_init():
    try:
        ui = JobSearchUI()
        assert ui is not None
    except Exception as e:
        assert False, f"JobSearchUI init raised an exception: {e}"
