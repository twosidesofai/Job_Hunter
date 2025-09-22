# jobs_fetcher.py
"""
Fetches and normalizes job postings from multiple job boards.
"""



from abc import ABC, abstractmethod
from typing import List, Dict, Any
from bs4 import BeautifulSoup

# Common data model for job postings
class JobPosting:
	def __init__(self, title: str, company: str, description: str, requirements: str, url: str):
		self.title = title
		self.company = company
		self.description = description
		self.requirements = requirements
		self.url = url

	def to_dict(self) -> Dict[str, Any]:
		return {
			"title": self.title,
			"company": self.company,
			"description": self.description,
			"requirements": self.requirements,
			"url": self.url
		}

# Abstract base agent for job board fetchers
class JobBoardAgent(ABC):
	@abstractmethod
	def fetch_jobs(self, keywords: str, location: str, filters: Dict[str, Any]) -> List[JobPosting]:
		pass


# Example agent for Adzuna API (free tier)
class AdzunaAgent(JobBoardAgent):
	def __init__(self, app_id: str = None, app_key: str = None):
		self.app_id = app_id
		self.app_key = app_key

	def fetch_jobs(self, keywords, location, filters):
		# TODO: Implement real API call using requests if credentials provided
		# For now, return mock data
		return [
			JobPosting(
				title="Full Stack Engineer",
				company="Adzuna",
				description="Work on full stack applications.",
				requirements="Python, JavaScript",
				url="https://adzuna.com/jobs/111"
			)
		]

# Example agent for SerpApi (Google Jobs, free tier)
class SerpApiAgent(JobBoardAgent):
	def __init__(self, api_key: str = None):
		self.api_key = api_key

	def fetch_jobs(self, keywords, location, filters):
		# TODO: Implement real API call using requests if credentials provided
		# For now, return mock data
		return [
			JobPosting(
				title="DevOps Engineer",
				company="Google Jobs",
				description="Automate infrastructure.",
				requirements="Python, AWS",
				url="https://google.com/jobs/222"
			)
		]

# Scraper agent for Monster
class MonsterScraperAgent(JobBoardAgent):
	def fetch_jobs(self, keywords, location, filters):
		# TODO: Implement scraping logic with BeautifulSoup/Selenium
		# For now, return mock data
		return [
			JobPosting(
				title="QA Engineer",
				company="Monster",
				description="Test software systems.",
				requirements="Python, Testing",
				url="https://monster.com/jobs/333"
			)
		]

# Scraper agent for Built In (e.g., Built In Chicago)
class BuiltInScraperAgent(JobBoardAgent):
	def fetch_jobs(self, keywords, location, filters):
		# TODO: Implement scraping logic with BeautifulSoup/Selenium
		# For now, return mock data
		return [
			JobPosting(
				title="Frontend Developer",
				company="Built In Chicago",
				description="Build UI components.",
				requirements="JavaScript, React",
				url="https://builtinchicago.com/jobs/444"
			)
		]

# Mock agent for Indeed
class IndeedAgent(JobBoardAgent):
	def fetch_jobs(self, keywords, location, filters):
		return [
			JobPosting(
				title="Backend Developer",
				company="Indeed",
				description="Work on backend APIs.",
				requirements="Python, REST APIs",
				url="https://indeed.com/jobs/456"
			)
		]

# Mock agent for ZipRecruiter
class ZipRecruiterAgent(JobBoardAgent):
	def fetch_jobs(self, keywords, location, filters):
		return [
			JobPosting(
				title="Data Scientist",
				company="ZipRecruiter",
				description="Analyze data and build models.",
				requirements="Python, Machine Learning",
				url="https://ziprecruiter.com/jobs/789"
			)
		]

# Main agent to coordinate all job board agents

class JobsFetcherAgent:
	def __init__(self, adzuna_app_id=None, adzuna_app_key=None, serp_api_key=None):
		self.agents = [
			AdzunaAgent(adzuna_app_id, adzuna_app_key),
			SerpApiAgent(serp_api_key),
			IndeedAgent(),
			ZipRecruiterAgent(),
			MonsterScraperAgent(),
			BuiltInScraperAgent()
		]

	def fetch_all_jobs(self, keywords: str, location: str, filters: Dict[str, Any] = None, manual_jobs: list = None) -> List[Dict[str, Any]]:
		if filters is None:
			filters = {}
		jobs = []
		for agent in self.agents:
			jobs.extend([job.to_dict() for job in agent.fetch_jobs(keywords, location, filters)])
		# Add manual jobs from argument
		if manual_jobs:
			jobs.extend(manual_jobs)
		# Add manual jobs from file if exists
		try:
			import json
			with open('manual_jobs.json', 'r') as f:
				file_jobs = json.load(f)
				jobs.extend(file_jobs)
		except Exception:
			pass
		# Deduplicate by (title, company, url)
		seen = set()
		deduped = []
		for job in jobs:
			key = (job['title'].lower(), job['company'].lower(), job['url'])
			if key not in seen:
				seen.add(key)
				deduped.append(job)
		return deduped

# Example usage (for testing)
if __name__ == "__main__":
	fetcher = JobsFetcherAgent()
	# CLI prompt for manual job entry
	import json
	manual_jobs = []
	add_manual = input("Do you want to add a manual job? (y/n): ").strip().lower()
	while add_manual == 'y':
		title = input("Job Title: ")
		company = input("Company: ")
		description = input("Description: ")
		requirements = input("Requirements (comma separated): ")
		url = input("Job URL: ")
		manual_jobs.append({
			"title": title,
			"company": company,
			"description": description,
			"requirements": requirements,
			"url": url
		})
		add_manual = input("Add another manual job? (y/n): ").strip().lower()
	results = fetcher.fetch_all_jobs("python developer", "remote", manual_jobs=manual_jobs)
	for job in results:
		print(job)
