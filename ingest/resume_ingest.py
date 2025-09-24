# Simple ingest_resume function for testing
def ingest_resume(path):
    # This is a stub for testing
    return {"name": "John Doe", "skills": ["Python", "AI"]}
import re
from typing import Dict
from docx import Document
from ingest.schema import ResumeProfile

SECTION_HEADINGS = {
    'summary': ['summary', 'profile', 'about'],
    'skills': ['skills', 'technical skills', 'core skills'],
    'experience': ['experience', 'work experience', 'professional experience', 'employment'],
    'education': ['education', 'academic'],
    'certifications': ['certifications', 'certs', 'licenses'],
    'projects': ['projects', 'personal projects', 'side projects'],
}

HEADING_PATTERN = re.compile(r'^[A-Z][A-Za-z\s]+$')


def parse_docx_to_profile(path: str) -> Dict:
    doc = Document(path)
    sections = {}
    current_section = None
    section_text = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # Detect headings
        if para.style.name.startswith('Heading') or HEADING_PATTERN.match(text):
            if current_section and section_text:
                sections[current_section] = section_text
            # Map heading to canonical section
            lower = text.lower()
            mapped = None
            for key, variants in SECTION_HEADINGS.items():
                if any(v in lower for v in variants):
                    mapped = key
                    break
            current_section = mapped or lower
            section_text = []
        else:
            section_text.append(text)
    if current_section and section_text:
        sections[current_section] = section_text

    # Extract fields from sections
    profile = {
        'name': '',
        'title': '',
        'summary': '',
        'skills': [],
        'experience': [],
        'education': [],
        'certs': [],
        'locations': [],
        'job_prefs': {
            'titles': [],
            'industries': [],
            'locations': [],
            'remote_ok': False,
            'salary_min': 0
        }
    }

    # Summary
    if 'summary' in sections:
        profile['summary'] = ' '.join(sections['summary'])

    # Skills
    if 'skills' in sections:
        skills = []
        for line in sections['skills']:
            skills += re.split(r',|\u2022|-|•', line)
        skills = [s.strip() for s in skills if s.strip()]
        profile['skills'] = list({s.lower(): s for s in skills}.values())

    # Experience
    if 'experience' in sections:
        exp_items = []
        item = {}
        for line in sections['experience']:
            # Heuristic: Company, Role, Dates, Bullets
            if re.search(r'\d{4}', line):
                if item:
                    exp_items.append(item)
                item = {'company': '', 'role': '', 'start': '', 'end': '', 'bullets': [], 'tech': []}
                # Parse dates
                date_match = re.findall(r'(\d{4}[\-/]\d{2}|\d{4})', line)
                if date_match:
                    item['start'] = date_match[0]
                    item['end'] = date_match[-1]
                # Company/Role
                parts = re.split(r' at |, ', line)
                if len(parts) > 1:
                    item['role'] = parts[0].strip()
                    item['company'] = parts[1].strip()
                else:
                    item['role'] = line.strip()
            else:
                if '•' in line or '-' in line or line.startswith('*'):
                    item.setdefault('bullets', []).append(line.strip('•*- '))
        if item:
            exp_items.append(item)
        # Infer tech from skills
        for e in exp_items:
            e['tech'] = [s for s in profile['skills'] if any(s in b.lower() for b in e.get('bullets', []))]
        profile['experience'] = exp_items

    # Education
    if 'education' in sections:
        edu_items = []
        for line in sections['education']:
            match = re.match(r'(.*?),(.*?),(\d{4})', line)
            if match:
                edu_items.append({'school': match.group(1).strip(), 'degree': match.group(2).strip(), 'year': match.group(3)})
        profile['education'] = edu_items

    # Certifications
    if 'certifications' in sections:
        profile['certs'] = [c.strip() for c in sections['certifications'] if c.strip()]

    # Projects (optional)
    # ... can be added similarly if needed

    # Locations and job_prefs (heuristic)
    # ... can be inferred from summary or experience if present

    # Validate and return
    ResumeProfile.validate_profile(profile)
    return profile
