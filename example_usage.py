#!/usr/bin/env python3
"""
Example usage of Job Hunter with OpenAI Agent Structure.
This shows how to use the system with and without OpenAI API access.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def example_basic_usage():
    """Basic usage example without API calls."""
    print("📋 Example: Basic Job Hunter Usage")
    print("=" * 40)
    
    from models import SearchCriteria, ExportFormat
    from main import load_sample_master_resume
    
    # 1. Define search criteria
    search_criteria = SearchCriteria(
        keywords=["Python Developer", "Software Engineer"],
        location="Remote",
        job_type="Full-time",
        remote_ok=True,
        job_boards=["indeed", "linkedin"]
    )
    
    # 2. Load master resume
    master_resume = load_sample_master_resume()
    
    print(f"✅ Search Criteria: {', '.join(search_criteria.keywords)}")
    print(f"✅ Location: {search_criteria.location}")
    print(f"✅ Master Resume: {master_resume.personal_info['name']}")
    print(f"✅ Experience Items: {len(master_resume.experience)}")
    print(f"✅ Skills Categories: {len(master_resume.skills)}")
    
    return search_criteria, master_resume

def example_individual_agents():
    """Example of using individual agents."""
    print("\n🤖 Example: Individual Agent Usage")
    print("=" * 40)
    
    from jobs_fetcher import JobsFetcherAgent
    from resume_builder import ResumeBuilderAgent
    from cover_letter_builder import CoverLetterBuilderAgent
    from exporter import ExporterAgent
    from tracker import TrackerAgent
    
    agents = [
        JobsFetcherAgent(),
        ResumeBuilderAgent(), 
        CoverLetterBuilderAgent(),
        ExporterAgent(),
        TrackerAgent()
    ]
    
    for agent in agents:
        info = agent.get_agent_info()
        print(f"✅ {info['name']} initialized (Model: {info['model']})")
    
    return agents

def example_workflow_preparation():
    """Example of preparing for full workflow."""
    print("\n🔧 Example: Workflow Preparation")
    print("=" * 40)
    
    search_criteria, master_resume = example_basic_usage()
    agents = example_individual_agents()
    
    print(f"\n📊 Ready for workflow with:")
    print(f"   • Search Keywords: {len(search_criteria.keywords)}")
    print(f"   • Job Boards: {len(search_criteria.job_boards)}")
    print(f"   • Experience Items: {len(master_resume.experience)}")
    print(f"   • Active Agents: {len(agents)}")
    
    return True

def example_mock_job_processing():
    """Example of mock job processing workflow."""
    print("\n⚙️  Example: Mock Job Processing")
    print("=" * 40)
    
    from models import JobPosting
    from datetime import datetime
    
    # Create a mock job posting
    mock_job = JobPosting(
        title="Senior Python Developer",
        company="TechCorp Inc.",
        description="We're looking for an experienced Python developer...",
        requirements="5+ years Python experience, Django, REST APIs",
        posting_url="https://example.com/job1",
        location="Remote",
        salary_range="$90,000 - $120,000",
        job_type="Full-time",
        remote_ok=True,
        source="indeed",
        posted_date=datetime.now()
    )
    
    print(f"✅ Mock Job Created:")
    print(f"   • Title: {mock_job.title}")
    print(f"   • Company: {mock_job.company}")
    print(f"   • Location: {mock_job.location}")
    print(f"   • Source: {mock_job.source}")
    
    # Show what would happen in full workflow
    workflow_steps = [
        "1. Jobs Fetcher would normalize job data",
        "2. Resume Builder would analyze requirements",
        "3. Cover Letter Builder would research company", 
        "4. Exporter would create PDF/DOCX files",
        "5. Tracker would log the application"
    ]
    
    print(f"\n🔄 Workflow Steps (with OpenAI API):")
    for step in workflow_steps:
        print(f"   {step}")
    
    return mock_job

def main():
    """Run all examples."""
    print("🚀 Job Hunter - Usage Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_workflow_preparation()
        mock_job = example_mock_job_processing()
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Set up .env file with OpenAI API key")
        print(f"   2. Install dependencies: pip install -r requirements.txt")
        print(f"   3. Run: python main.py")
        print(f"   4. Check Applications/ folder for generated documents")
        
        print(f"\n🎯 OpenAI Agent Structure Benefits:")
        benefits = [
            "🧠 Intelligent job analysis and matching",
            "📝 AI-powered resume tailoring",
            "💌 Personalized cover letter generation", 
            "📊 Smart application insights",
            "🔄 Automated workflow orchestration"
        ]
        
        for benefit in benefits:
            print(f"   {benefit}")
            
        print(f"\n✅ Examples completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Example failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())