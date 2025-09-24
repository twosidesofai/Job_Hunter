# Job Hunter

## Overview
Job Hunter is a modular Python application that automates the job search and application process. Now supports starting from a Word resume (.docx) and agentic pipeline. It can:
- Scrape or query multiple job boards (Adzuna, SerpApi, Indeed, ZipRecruiter, Monster, Built In, JPMorgan, and more)
- Normalize job postings into a common data model
- Generate tailored resumes and personalized cover letters for each job
- Export resumes and cover letters to Word/PDF format in an Applications folder
- Log applied jobs in a local SQLite database with timestamps and status
- (Optional) Integrate with email or job portal APIs to auto-submit applications
- Suggest relevant companies/boards to scrape based on your resume using AI/ML
- Provide a dynamic UI to control search criteria and select companies/boards
- Allow manual job entry and import from JSON
 - Ingest a Word resume (.docx), convert to structured JSON, and run the agentic pipeline: suggest roles/boards → fetch jobs → dedupe → rank → tailor resume/cover letter → export → track

## Features
- **jobs_fetcher.py**: Gathers and normalizes job postings from APIs and scrapers, with deduplication
- **resume_builder.py**: Generates tailored resumes from a master resume JSON file
- **cover_letter_builder.py**: Generates personalized cover letters using a template and job description
- **exporter.py**: Outputs resumes and cover letters to PDF/DOCX in the Applications folder
- **tracker.py**: Logs and tracks applications in a local SQLite database
- **ai_company_suggester.py**: Suggests companies/boards to scrape based on your resume (AI/ML approach)
- **job_search_ui.py**: Tkinter UI to control search input, select/add/remove companies/boards dynamically
- **manual_jobs.json**: Add jobs manually for inclusion in the workflow
- **.env**: Store API keys for Adzuna, SerpApi, etc.
 - **ingest/resume_ingest.py**: Converts resume.docx to structured JSON profile
 - **ingest/schema.py**: Pydantic models for resume profile validation
 - **match/ranker.py**: Ranks jobs with rationale fields

## Setup
1. Clone the repo and install requirements:
	```bash
	pip install -r requirements.txt
	```
2. Add your API keys to a `.env` file (see example in repo)
3. Upload or provide your resume as a Word file (`resume.docx`).
4. Run the CLI or UI:

### CLI Example
```bash
python run.py --resume-docx ./resume.docx --top 15 --remote-only true --locations "Chicago, Remote"
```

### UI Example
```bash
python job_search_ui.py
```
In the UI, upload/select your resume.docx, preview suggested roles/boards, and start the agentic pipeline.

## Current Status
- [x] Modular structure implemented
- [x] Job board scraping and API integration (mock and real, with deduplication)
- [x] Resume and cover letter generation
- [x] Export to PDF/DOCX
- [x] Application tracking (SQLite)
- [x] Manual job entry and import
- [x] Dynamic UI for search and board selection
- [x] AI/ML-based company/board suggestion from resume
- [ ] (Optional) Auto-submission via email/APIs (planned)
 - [x] Word resume ingestion and agentic pipeline
 - [x] Job ranking with rationale

## How to Extend
- Add new scrapers or API agents in `jobs_fetcher.py`
- Update `ai_company_suggester.py` for more advanced AI/ML logic
- Customize the UI in `job_search_ui.py`
- Add new export formats or tracking fields as needed
 - Extend `ingest/resume_ingest.py` for more robust parsing
 - Update `match/ranker.py` for custom ranking logic

## License
MIT