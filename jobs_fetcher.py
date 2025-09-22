"""
Job fetcher agent that scrapes and normalizes job postings using OpenAI agent structure.
"""
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base_agent import BaseAgent, AgentResponse
from models import JobPosting, SearchCriteria

class JobsFetcherAgent(BaseAgent):
    """
    Agent responsible for fetching and normalizing job postings from multiple job boards.
    Uses OpenAI to help with data normalization and extraction.
    """
    
    def __init__(self):
        system_prompt = """
        You are a specialized job posting data extraction and normalization agent. Your role is to:
        
        1. Parse raw HTML content from job boards and extract structured job information
        2. Normalize job postings into a consistent format with fields: title, company, description, requirements, URL
        3. Clean and standardize job descriptions and requirements
        4. Extract additional metadata like location, salary, job type when available
        5. Identify and remove duplicate or low-quality postings
        
        When processing job data:
        - Extract the most important requirements and qualifications
        - Clean up HTML formatting and excessive whitespace
        - Standardize company names and job titles
        - Identify remote work opportunities
        - Extract salary information when present
        
        Always return structured JSON data that matches the JobPosting model schema.
        """
        super().__init__("JobsFetcher", system_prompt)
        self.supported_functions = ["extract_job_data", "normalize_job_posting", "deduplicate_jobs"]
    
    def execute_function(self, function_name: str, args: Dict[str, Any]) -> Any:
        """Execute specific job fetching functions."""
        if function_name == "extract_job_data":
            return self._extract_job_data_from_html(args.get("html_content", ""), args.get("source", ""))
        elif function_name == "normalize_job_posting":
            return self._normalize_job_data(args.get("raw_job_data", {}))
        elif function_name == "deduplicate_jobs":
            return self._deduplicate_jobs(args.get("job_list", []))
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process job fetching requests."""
        try:
            if "search_jobs" in request.lower():
                criteria = SearchCriteria(**context) if context else None
                jobs = self.search_jobs(criteria)
                return AgentResponse(
                    success=True,
                    data={"jobs": [job.model_dump() for job in jobs]},
                    message=f"Successfully fetched {len(jobs)} job postings"
                )
            else:
                # Use OpenAI to help with data extraction
                messages = self._prepare_messages(request, context)
                response = self._make_openai_request(messages)
                return self._handle_response(response)
                
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return AgentResponse(
                success=False,
                message="Failed to process job fetching request",
                errors=[str(e)]
            )
    
    def search_jobs(self, criteria: SearchCriteria) -> List[JobPosting]:
        """
        Search for jobs across multiple job boards based on criteria.
        
        Args:
            criteria: Job search criteria
            
        Returns:
            List of normalized job postings
        """
        all_jobs = []
        
        for job_board in criteria.job_boards:
            try:
                if job_board.lower() == "indeed":
                    jobs = self._search_indeed(criteria)
                elif job_board.lower() == "linkedin":
                    jobs = self._search_linkedin(criteria)
                elif job_board.lower() == "ziprecruiter":
                    jobs = self._search_ziprecruiter(criteria)
                else:
                    self.logger.warning(f"Unsupported job board: {job_board}")
                    continue
                    
                all_jobs.extend(jobs)
                
            except Exception as e:
                self.logger.error(f"Error searching {job_board}: {str(e)}")
                continue
        
        # Deduplicate and normalize jobs using OpenAI
        deduplicated_jobs = self._deduplicate_jobs(all_jobs)
        return deduplicated_jobs[:criteria.job_boards.__len__() * 25]  # Limit results
    
    def _search_indeed(self, criteria: SearchCriteria) -> List[JobPosting]:
        """Search Indeed job board."""
        jobs = []
        
        try:
            # Setup Selenium with headless Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # For demo purposes, we'll create mock data that would normally come from scraping
            # In a real implementation, you would use Selenium to scrape Indeed
            mock_jobs_data = self._get_mock_indeed_jobs(criteria)
            
            for job_data in mock_jobs_data:
                normalized_job = self._normalize_job_with_ai(job_data, "Indeed")
                if normalized_job:
                    jobs.append(normalized_job)
                    
        except Exception as e:
            self.logger.error(f"Error searching Indeed: {str(e)}")
            
        return jobs
    
    def _search_linkedin(self, criteria: SearchCriteria) -> List[JobPosting]:
        """Search LinkedIn job board."""
        jobs = []
        
        try:
            # For demo purposes, using mock data
            # Real implementation would require LinkedIn API or careful scraping
            mock_jobs_data = self._get_mock_linkedin_jobs(criteria)
            
            for job_data in mock_jobs_data:
                normalized_job = self._normalize_job_with_ai(job_data, "LinkedIn")
                if normalized_job:
                    jobs.append(normalized_job)
                    
        except Exception as e:
            self.logger.error(f"Error searching LinkedIn: {str(e)}")
            
        return jobs
    
    def _search_ziprecruiter(self, criteria: SearchCriteria) -> List[JobPosting]:
        """Search ZipRecruiter job board."""
        jobs = []
        
        try:
            # Mock implementation for ZipRecruiter
            mock_jobs_data = self._get_mock_ziprecruiter_jobs(criteria)
            
            for job_data in mock_jobs_data:
                normalized_job = self._normalize_job_with_ai(job_data, "ZipRecruiter")
                if normalized_job:
                    jobs.append(normalized_job)
                    
        except Exception as e:
            self.logger.error(f"Error searching ZipRecruiter: {str(e)}")
            
        return jobs
    
    def _normalize_job_with_ai(self, raw_job_data: Dict[str, Any], source: str) -> Optional[JobPosting]:
        """
        Use OpenAI to normalize raw job data into structured format.
        """
        try:
            prompt = f"""
            Please normalize this raw job data from {source} into a structured format.
            
            Raw job data:
            {json.dumps(raw_job_data, indent=2)}
            
            Please extract and return a JSON object with these fields:
            - title: Clean job title
            - company: Company name
            - description: Clean job description (remove HTML, excessive formatting)
            - requirements: Key requirements and qualifications
            - location: Job location
            - salary_range: Salary information if available
            - job_type: Full-time, part-time, contract, etc.
            - remote_ok: Boolean indicating if remote work is mentioned
            
            Make the description and requirements concise but informative.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                content = response["choices"][0]["message"]["content"]
                # Extract JSON from the response
                try:
                    # Find JSON in the response
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                    normalized_data = json.loads(json_str)
                    
                    # Create JobPosting object
                    job_posting = JobPosting(
                        title=normalized_data.get("title", ""),
                        company=normalized_data.get("company", ""),
                        description=normalized_data.get("description", ""),
                        requirements=normalized_data.get("requirements", ""),
                        posting_url=raw_job_data.get("url", "https://example.com"),
                        location=normalized_data.get("location"),
                        salary_range=normalized_data.get("salary_range"),
                        job_type=normalized_data.get("job_type"),
                        remote_ok=normalized_data.get("remote_ok"),
                        source=source,
                        posted_date=datetime.now() - timedelta(days=1)  # Mock posted date
                    )
                    
                    return job_posting
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing AI response JSON: {str(e)}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error normalizing job data with AI: {str(e)}")
            return None
    
    def _deduplicate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate job postings."""
        seen_jobs = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a hash based on title, company, and location
            job_hash = f"{job.title.lower()}_{job.company.lower()}_{job.location or ''}"
            
            if job_hash not in seen_jobs:
                seen_jobs.add(job_hash)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _extract_job_data_from_html(self, html_content: str, source: str) -> Dict[str, Any]:
        """Extract job data from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # This would be specific to each job board's HTML structure
        # For now, return a basic structure
        return {
            "title": soup.find("title").text if soup.find("title") else "",
            "content": soup.get_text()
        }
    
    def _normalize_job_data(self, raw_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize job data structure."""
        return {
            "title": raw_job_data.get("title", "").strip(),
            "company": raw_job_data.get("company", "").strip(),
            "description": raw_job_data.get("description", "").strip(),
            "requirements": raw_job_data.get("requirements", "").strip(),
            "location": raw_job_data.get("location", "").strip(),
            "url": raw_job_data.get("url", "")
        }
    
    # Mock data generators for demonstration
    def _get_mock_indeed_jobs(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Generate mock Indeed job data for demonstration."""
        return [
            {
                "title": f"Senior {criteria.keywords[0]} Developer",
                "company": "TechCorp Inc.",
                "description": f"We are looking for an experienced {criteria.keywords[0]} developer to join our team. You will work on cutting-edge projects using modern technologies.",
                "requirements": f"5+ years experience in {criteria.keywords[0]}, strong problem-solving skills, team player",
                "location": criteria.location,
                "salary": "$90,000 - $120,000",
                "job_type": "Full-time",
                "url": "https://indeed.com/job1"
            },
            {
                "title": f"{criteria.keywords[0]} Engineer",
                "company": "StartupXYZ",
                "description": f"Join our fast-growing startup as a {criteria.keywords[0]} engineer. Work on innovative products that impact millions of users.",
                "requirements": f"3+ years experience in {criteria.keywords[0]}, startup experience preferred",
                "location": criteria.location,
                "job_type": "Full-time",
                "remote_friendly": True,
                "url": "https://indeed.com/job2"
            }
        ]
    
    def _get_mock_linkedin_jobs(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Generate mock LinkedIn job data for demonstration."""
        return [
            {
                "title": f"Lead {criteria.keywords[0]} Architect",
                "company": "Enterprise Solutions Ltd.",
                "description": f"Lead a team of {criteria.keywords[0]} developers in designing and implementing scalable solutions for enterprise clients.",
                "requirements": f"7+ years in {criteria.keywords[0]}, leadership experience, architecture design",
                "location": criteria.location,
                "salary": "$130,000 - $160,000",
                "job_type": "Full-time",
                "url": "https://linkedin.com/job1"
            }
        ]
    
    def _get_mock_ziprecruiter_jobs(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Generate mock ZipRecruiter job data for demonstration."""
        return [
            {
                "title": f"Junior {criteria.keywords[0]} Developer",
                "company": "GrowthCorp",
                "description": f"Entry-level position for a {criteria.keywords[0]} developer. Great opportunity for recent graduates.",
                "requirements": f"1-2 years experience in {criteria.keywords[0]}, degree in Computer Science or related field",
                "location": criteria.location,
                "salary": "$60,000 - $80,000",
                "job_type": "Full-time",
                "url": "https://ziprecruiter.com/job1"
            }
        ]