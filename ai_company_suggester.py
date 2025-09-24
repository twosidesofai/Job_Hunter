# Simple suggest_companies function for testing
def suggest_companies(resume):
    # This is a stub for testing
    return ["CompanyA", "CompanyB"]
# ai_company_suggester.py
"""
Suggests relevant companies/boards to scrape based on resume content using AI/ML or keyword-matching.
"""

import json
from collections import Counter

# Example mapping of keywords to companies/boards
KEYWORD_COMPANY_MAP = {
    "python": ["Adzuna", "SerpApi", "Indeed", "ZipRecruiter", "Monster", "Built In", "JPMorgan", "Google", "Meta", "Amazon"],
    "distributed systems": ["Adzuna", "Google", "Amazon"],
    "machine learning": ["Adzuna", "SerpApi", "Indeed", "Google", "Meta", "Amazon"],
    "data analysis": ["Adzuna", "Indeed", "DataX", "Google"],
    "rest apis": ["Adzuna", "SerpApi", "Indeed", "WebSolutions"],
    "backend": ["Adzuna", "Monster", "Built In", "JPMorgan"],
    "integration": ["Adzuna", "Built In", "WebSolutions"],
    "software": ["Adzuna", "Monster", "Built In", "JPMorgan"]
}

# Simple AI/ML-like approach: count keyword matches and rank companies
class AICompanySuggester:
    def __init__(self, keyword_company_map=None):
        self.keyword_company_map = keyword_company_map or KEYWORD_COMPANY_MAP

    def suggest(self, resume_json_path, top_n=7):
        with open(resume_json_path, 'r') as f:
            resume = json.load(f)
        # Gather all text fields
        text = ' '.join([
            resume.get('summary', ''),
            ' '.join(resume.get('skills', [])),
            ' '.join(exp.get('role', '') for exp in resume.get('experience', [])),
            ' '.join(exp.get('company', '') for exp in resume.get('experience', [])),
            ' '.join(b for exp in resume.get('experience', []) for b in exp.get('bullets', [])),
        ]).lower()

        # Infer titles from roles and skills
        titles = list({exp.get('role', '').title() for exp in resume.get('experience', []) if exp.get('role', '')})
        if not titles:
            titles = [resume.get('title', '')]
        # Infer industries from keywords in summary/experience
        industries = []
        for kw in ['software', 'finance', 'healthcare', 'data', 'cloud', 'ai', 'ml', 'project', 'manager']:
            if kw in text:
                industries.append(kw.title())
        industries = list(set(industries))

        # Keywords from skills
        keywords = [s for s in resume.get('skills', [])]

        # Count company/board matches
        company_counter = Counter()
        sources = []
        for keyword, companies in self.keyword_company_map.items():
            if keyword in text:
                for company in companies:
                    company_counter[company] += 1
                    sources.append({
                        "name": company.lower().replace(' ', ''),
                        "queries": [f"{t} {keyword} {loc}" for t in titles for loc in resume.get('locations', [])]
                    })
        # Deduplicate sources
        sources = [dict(t) for t in {tuple(sorted(s.items())) for s in sources}]

        return {
            "suggested_titles": titles,
            "industries": industries,
            "keywords": keywords,
            "sources": sources[:top_n]
        }

if __name__ == "__main__":
    suggester = AICompanySuggester()
    suggestions = suggester.suggest("master_resume.json")
    print("Suggested companies/boards:", suggestions)
