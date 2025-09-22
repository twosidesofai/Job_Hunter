"""
Main Job Hunter application that orchestrates all OpenAI-powered agents.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from jobs_fetcher import JobsFetcherAgent
from resume_builder import ResumeBuilderAgent
from cover_letter_builder import CoverLetterBuilderAgent
from exporter import ExporterAgent
from tracker import TrackerAgent
from models import (
    SearchCriteria, JobPosting, MasterResume, TailoredResume, 
    CoverLetter, JobApplication, JobStatus, ExportFormat
)
from config import Config
from base_agent import AgentResponse

class JobHunterOrchestrator:
    """
    Main orchestrator that coordinates all OpenAI-powered agents for job hunting automation.
    """
    
    def __init__(self):
        """Initialize all agents."""
        # Validate configuration
        Config.validate_config()
        
        # Initialize all agents with OpenAI structure
        self.jobs_fetcher = JobsFetcherAgent()
        self.resume_builder = ResumeBuilderAgent()
        self.cover_letter_builder = CoverLetterBuilderAgent()
        self.exporter = ExporterAgent()
        self.tracker = TrackerAgent()
        
        # Ensure directories exist
        os.makedirs(Config.APPLICATIONS_DIR, exist_ok=True)
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.TEMPLATES_DIR, exist_ok=True)
        
        print("Job Hunter initialized with OpenAI-powered agents:")
        print(f"- Jobs Fetcher Agent: {self.jobs_fetcher.name}")
        print(f"- Resume Builder Agent: {self.resume_builder.name}")
        print(f"- Cover Letter Builder Agent: {self.cover_letter_builder.name}")
        print(f"- Exporter Agent: {self.exporter.name}")
        print(f"- Tracker Agent: {self.tracker.name}")
    
    def run_full_job_application_workflow(
        self, 
        search_criteria: SearchCriteria, 
        master_resume: MasterResume,
        max_applications: int = 5,
        export_format: ExportFormat = ExportFormat.BOTH
    ) -> Dict[str, Any]:
        """
        Run the complete job application workflow.
        
        Args:
            search_criteria: Job search criteria
            master_resume: Master resume data
            max_applications: Maximum number of applications to process
            export_format: Export format for documents
            
        Returns:
            Dictionary with workflow results
        """
        print(f"\n🚀 Starting job application workflow for: {', '.join(search_criteria.keywords)}")
        results = {
            "jobs_found": [],
            "resumes_created": [],
            "cover_letters_created": [],
            "applications_tracked": [],
            "exported_files": [],
            "errors": []
        }
        
        try:
            # Step 1: Fetch jobs using Jobs Fetcher Agent
            print("\n📋 Step 1: Fetching job postings...")
            jobs_response = self.jobs_fetcher.process_request(
                "search_jobs",
                context=search_criteria.model_dump()
            )
            
            if not jobs_response.success:
                results["errors"].append(f"Job fetching failed: {jobs_response.message}")
                return results
            
            jobs_data = jobs_response.data.get("jobs", [])
            job_postings = [JobPosting(**job_data) for job_data in jobs_data[:max_applications]]
            results["jobs_found"] = [job.model_dump() for job in job_postings]
            print(f"✅ Found {len(job_postings)} job postings")
            
            # Step 2-6: Process each job posting
            for i, job_posting in enumerate(job_postings, 1):
                print(f"\n📄 Processing job {i}/{len(job_postings)}: {job_posting.company} - {job_posting.title}")
                
                try:
                    # Step 2: Build tailored resume using Resume Builder Agent
                    print("   📝 Building tailored resume...")
                    resume_response = self.resume_builder.process_request(
                        "build_resume",
                        context={
                            "job_posting": job_posting.model_dump(),
                            "master_resume": master_resume.model_dump()
                        }
                    )
                    
                    if not resume_response.success:
                        results["errors"].append(f"Resume building failed for {job_posting.company}: {resume_response.message}")
                        continue
                    
                    tailored_resume = TailoredResume(**resume_response.data["tailored_resume"])
                    results["resumes_created"].append(tailored_resume.model_dump())
                    
                    # Step 3: Build cover letter using Cover Letter Builder Agent
                    print("   📨 Building cover letter...")
                    cover_letter_response = self.cover_letter_builder.process_request(
                        "build_cover_letter",
                        context={
                            "job_posting": job_posting.model_dump(),
                            "master_resume": master_resume.model_dump()
                        }
                    )
                    
                    if not cover_letter_response.success:
                        results["errors"].append(f"Cover letter building failed for {job_posting.company}: {cover_letter_response.message}")
                        continue
                    
                    cover_letter = CoverLetter(**cover_letter_response.data["cover_letter"])
                    results["cover_letters_created"].append(cover_letter.model_dump())
                    
                    # Step 4: Export documents using Exporter Agent
                    print("   💾 Exporting documents...")
                    export_response = self.exporter.process_request(
                        "export",
                        context={
                            "job_posting": job_posting.model_dump(),
                            "resume": tailored_resume.model_dump(),
                            "cover_letter": cover_letter.model_dump(),
                            "format": export_format
                        }
                    )
                    
                    if not export_response.success:
                        results["errors"].append(f"Export failed for {job_posting.company}: {export_response.message}")
                        continue
                    
                    file_paths = export_response.data["file_paths"]
                    results["exported_files"].extend(list(file_paths.values()))
                    
                    # Step 5: Track application using Tracker Agent
                    print("   📊 Tracking application...")
                    job_application = JobApplication(
                        job_posting=job_posting,
                        status=JobStatus.FOUND,
                        resume_path=file_paths.get("resume_pdf"),
                        cover_letter_path=file_paths.get("cover_letter_pdf"),
                        notes=f"Auto-generated application for {job_posting.title} at {job_posting.company}"
                    )
                    
                    track_response = self.tracker.process_request(
                        "track",
                        context={"job_application": job_application.model_dump()}
                    )
                    
                    if track_response.success:
                        results["applications_tracked"].append(track_response.data["application_id"])
                        print(f"   ✅ Successfully processed application for {job_posting.company}")
                    else:
                        results["errors"].append(f"Tracking failed for {job_posting.company}: {track_response.message}")
                
                except Exception as e:
                    error_msg = f"Error processing {job_posting.company} - {job_posting.title}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
            
            # Summary
            print(f"\n📊 Workflow completed!")
            print(f"   Jobs found: {len(results['jobs_found'])}")
            print(f"   Resumes created: {len(results['resumes_created'])}")
            print(f"   Cover letters created: {len(results['cover_letters_created'])}")
            print(f"   Applications tracked: {len(results['applications_tracked'])}")
            print(f"   Files exported: {len(results['exported_files'])}")
            print(f"   Errors: {len(results['errors'])}")
            
            return results
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            return results
    
    def get_application_insights(self) -> Dict[str, Any]:
        """Get insights from the Tracker Agent."""
        print("\n📈 Getting application insights...")
        
        insights_response = self.tracker.process_request("insights")
        
        if insights_response.success:
            return insights_response.data.get("insights", {})
        else:
            return {"error": insights_response.message}
    
    def get_follow_up_recommendations(self) -> List[Dict[str, Any]]:
        """Get follow-up recommendations from the Tracker Agent."""
        print("\n📅 Getting follow-up recommendations...")
        
        return self.tracker.get_follow_up_recommendations()
    
    def update_application_status(self, application_id: str, status: JobStatus, notes: Optional[str] = None) -> bool:
        """Update application status."""
        print(f"\n🔄 Updating application {application_id} to {status.value}")
        
        updates = {"status": status.value}
        if notes:
            updates["notes"] = notes
        if status == JobStatus.APPLIED:
            updates["applied_date"] = datetime.utcnow()
        
        update_response = self.tracker.process_request(
            "update",
            context={
                "application_id": application_id,
                "updates": updates
            }
        )
        
        return update_response.success

def load_sample_master_resume() -> MasterResume:
    """Load a sample master resume for demonstration."""
    return MasterResume(
        personal_info={
            "name": "John Developer",
            "email": "john.developer@email.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA",
            "linkedin": "https://linkedin.com/in/johndeveloper",
            "github": "https://github.com/johndeveloper"
        },
        summary="Experienced software developer with 5+ years of expertise in full-stack web development, specializing in Python, JavaScript, and cloud technologies. Proven track record of delivering scalable applications and leading development teams.",
        experience=[
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Solutions",
                "duration": "2021 - Present",
                "description": "Led development of microservices architecture serving 1M+ users, implemented CI/CD pipelines reducing deployment time by 60%, mentored junior developers and conducted code reviews.",
                "skills": ["Python", "Django", "React", "AWS", "Docker"],
                "achievements": [
                    "Reduced application response time by 40% through optimization",
                    "Led team of 4 developers on critical product features"
                ]
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "duration": "2019 - 2021",
                "description": "Developed and maintained web applications using React and Node.js, integrated payment systems and third-party APIs, collaborated with design team on user experience improvements.",
                "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Stripe API"],
                "achievements": [
                    "Built payment system processing $500K+ monthly",
                    "Improved user engagement by 25% through feature development"
                ]
            },
            {
                "title": "Software Developer",
                "company": "WebDev Agency",
                "duration": "2018 - 2019",
                "description": "Developed custom websites and web applications for clients, worked with various CMS platforms, performed website optimization and maintenance.",
                "skills": ["PHP", "WordPress", "MySQL", "HTML/CSS", "jQuery"],
                "achievements": [
                    "Delivered 20+ client projects on time and under budget",
                    "Improved website loading speed by average 50%"
                ]
            }
        ],
        education=[
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "year": "2018",
                "gpa": "3.7"
            }
        ],
        skills={
            "Programming Languages": ["Python", "JavaScript", "TypeScript", "PHP", "Java"],
            "Frontend": ["React", "Vue.js", "HTML5", "CSS3", "SASS"],
            "Backend": ["Django", "Node.js", "Express", "FastAPI"],
            "Databases": ["PostgreSQL", "MongoDB", "Redis", "MySQL"],
            "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "CI/CD"],
            "Tools": ["Git", "Jenkins", "JIRA", "VS Code"]
        },
        certifications=[
            "AWS Certified Solutions Architect",
            "Certified Kubernetes Administrator (CKA)",
            "Agile/Scrum Master Certification"
        ],
        projects=[
            {
                "name": "E-commerce Platform",
                "description": "Built scalable e-commerce platform with microservices architecture, handling 10K+ daily transactions",
                "technologies": "Python, Django, React, PostgreSQL, AWS"
            },
            {
                "name": "Real-time Chat Application",
                "description": "Developed real-time messaging app with WebSocket support and end-to-end encryption",
                "technologies": "Node.js, Socket.io, React, MongoDB"
            }
        ]
    )

def main():
    """Main function to demonstrate the Job Hunter application."""
    print("🔍 Job Hunter - OpenAI-Powered Job Application Automation")
    print("=" * 60)
    
    try:
        # Initialize the orchestrator
        job_hunter = JobHunterOrchestrator()
        
        # Load sample master resume
        master_resume = load_sample_master_resume()
        
        # Define search criteria
        search_criteria = SearchCriteria(
            keywords=["Python Developer", "Software Engineer"],
            location="Remote",
            job_type="Full-time",
            remote_ok=True,
            job_boards=["indeed", "linkedin"]
        )
        
        # Run the full workflow
        results = job_hunter.run_full_job_application_workflow(
            search_criteria=search_criteria,
            master_resume=master_resume,
            max_applications=3,
            export_format=ExportFormat.BOTH
        )
        
        # Display results
        print(f"\n📊 Final Results:")
        print(f"   Applications processed: {len(results['applications_tracked'])}")
        print(f"   Files created: {len(results['exported_files'])}")
        if results["errors"]:
            print(f"   Errors encountered: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"     - {error}")
        
        # Get insights
        insights = job_hunter.get_application_insights()
        if insights and "insights" in insights:
            print(f"\n💡 Job Search Insights:")
            for insight in insights.get("insights", [])[:3]:
                print(f"   • {insight}")
        
        print(f"\n✅ Job Hunter workflow completed successfully!")
        print(f"📂 Check the '{Config.APPLICATIONS_DIR}' folder for generated documents.")
        
    except Exception as e:
        print(f"❌ Error running Job Hunter: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())