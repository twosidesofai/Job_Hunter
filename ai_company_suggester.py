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
            ' '.join(exp.get('description', '') for exp in resume.get('experience', [])),
            ' '.join(skill for exp in resume.get('experience', []) for skill in exp.get('skills', []))
        ]).lower()
        # Count company/board matches
        company_counter = Counter()
        for keyword, companies in self.keyword_company_map.items():
            if keyword in text:
                for company in companies:
                    company_counter[company] += 1
        # Return top N companies/boards
        return [c for c, _ in company_counter.most_common(top_n)]

if __name__ == "__main__":
    suggester = AICompanySuggester()
    suggestions = suggester.suggest("master_resume.json")
    print("Suggested companies/boards:", suggestions)
