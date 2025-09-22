# cover_letter_builder.py
"""
Generates personalized cover letters using a template and job description.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import jinja2

# Abstract base agent for cover letter building
class CoverLetterBuilderAgent(ABC):
    @abstractmethod
    def build_cover_letter(self, job_posting: Dict[str, Any], resume: Dict[str, Any], template: str) -> str:
        pass

# Simple agent using Jinja2 template rendering
class JinjaCoverLetterBuilderAgent(CoverLetterBuilderAgent):
    def build_cover_letter(self, job_posting: Dict[str, Any], resume: Dict[str, Any], template: str) -> str:
        env = jinja2.Environment()
        tmpl = env.from_string(template)
        return tmpl.render(job=job_posting, resume=resume)

# Example cover letter template
DEFAULT_TEMPLATE = """
Dear {{ job.company }} Hiring Team,

I am excited to apply for the {{ job.title }} position. With my experience in {{ resume.skills | join(', ') }}, I am confident I can contribute to your team.

My background includes:
{% for exp in resume.experience %}
- {{ exp.title }} at {{ exp.company }}: {{ exp.description }}
{% endfor %}

Thank you for considering my application.

Sincerely,
{{ resume.name }}
"""

# Example usage (for testing)
if __name__ == "__main__":
    job = {
        "title": "Backend Developer",
        "company": "Indeed",
        "description": "Work on backend APIs.",
        "requirements": "Python, REST APIs",
        "url": "https://indeed.com/jobs/456"
    }
    resume = {
        "name": "John Doe",
        "skills": ["Python", "REST APIs"],
        "experience": [
            {"title": "Backend Developer", "company": "WebSolutions", "description": "Built RESTful APIs and integrated third-party services."}
        ]
    }
    agent = JinjaCoverLetterBuilderAgent()
    letter = agent.build_cover_letter(job, resume, DEFAULT_TEMPLATE)
    print(letter)

