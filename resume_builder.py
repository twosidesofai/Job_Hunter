# resume_builder.py
"""
Generates tailored resumes from a master resume JSON file.
"""


import json
from typing import Dict, Any, List
from abc import ABC, abstractmethod

# Abstract base agent for resume building
class ResumeBuilderAgent(ABC):
	@abstractmethod
	def build_resume(self, job_posting: Dict[str, Any], master_resume_path: str) -> Dict[str, Any]:
		pass

# Simple agent that selects relevant experience based on keyword overlap
class KeywordResumeBuilderAgent(ResumeBuilderAgent):
	def build_resume(self, job_posting: Dict[str, Any], master_resume_path: str) -> Dict[str, Any]:
		with open(master_resume_path, 'r') as f:
			master_resume = json.load(f)

		job_keywords = set(
			job_posting.get('requirements', '').lower().split() +
			job_posting.get('description', '').lower().split()
		)

		# Select relevant experience
		relevant_experience = []
		for exp in master_resume.get('experience', []):
			exp_keywords = set([s.lower() for s in exp.get('skills', [])])
			if job_keywords & exp_keywords:
				relevant_experience.append(exp)

		tailored_resume = {
			'name': master_resume.get('name'),
			'contact': master_resume.get('contact'),
			'summary': master_resume.get('summary'),
			'experience': relevant_experience,
			'education': master_resume.get('education'),
			'skills': list(set(master_resume.get('skills', [])) & job_keywords)
		}
		return tailored_resume

# Example usage (for testing)
if __name__ == "__main__":
	# Example job posting
	job = {
		"title": "Backend Developer",
		"company": "Indeed",
		"description": "Work on backend APIs.",
		"requirements": "Python, REST APIs",
		"url": "https://indeed.com/jobs/456"
	}
	agent = KeywordResumeBuilderAgent()
	tailored = agent.build_resume(job, "master_resume.json")
	print(json.dumps(tailored, indent=2))
