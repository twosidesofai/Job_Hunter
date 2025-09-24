# Overview

Job Hunter is an AI-powered Python application that streamlines your job search and application workflow from start to finish:

1. **Start in the UI:** Upload your Word resume, set job criteria, and select job boards or companies to target.
2. **Resume Ingestion:** Your resume is parsed and converted to structured JSON for accurate matching and customization.
3. **Job Discovery:** The system scrapes and queries multiple job boards, normalizes postings, and suggests relevant companies using AI/ML.
4. **Job Ranking:** Jobs are deduplicated and ranked for fit based on your profile and preferences.
5. **Application Generation:** Tailored resumes and personalized cover letters are created for each job, ensuring ATS-friendly formatting.
6. **Export & Submission:** Documents are exported to Word/PDF and can be saved locally or submitted via APIs (optional).
7. **Tracking:** All applications are logged in a local database, with status updates and analytics for your review.

This end-to-end pipeline automates repetitive tasks, provides a clean and customizable workflow, and helps you focus on landing the right job.
# Workflow Overview

Job Hunter Workflow (from UI to DB):

1. **User Interface (UI)**
	- User uploads/selects a Word resume (.docx)
	- Sets job search criteria (role, location, salary, remote, etc.)
	- Selects or adds job boards/companies to target

2. **Resume Ingestion**
	- System parses the Word resume and converts it to structured JSON
	- Validates and normalizes resume data for downstream processing

3. **Job Discovery & Matching**
	- Scrapes/queries multiple job boards (Adzuna, SerpApi, Indeed, etc.)
	- Normalizes job postings into a common data model
	- Suggests relevant companies/boards using AI/ML based on resume content
	- Allows manual job entry or import from JSON
	- Deduplicates job postings

4. **Job Ranking & Selection**
	- Ranks jobs for fit using resume, preferences, and job data
	- Presents ranked jobs in the UI for user review and selection

5. **Application Generation**
	- Generates tailored resumes and personalized cover letters for each selected job
	- Ensures formatting is ATS-friendly

6. **Export & Submission**
	- Exports resumes and cover letters to Word/PDF in the Applications folder
	- (Optional) Submits applications via email or job portal APIs

7. **Tracking & Logging**
	- Logs applied jobs in a local SQLite database with timestamps and status
	- Tracks application status and provides analytics



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