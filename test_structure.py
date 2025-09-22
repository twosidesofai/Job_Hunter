"""
Test script to validate Job Hunter OpenAI agent structure implementation.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import JobHunterOrchestrator, load_sample_master_resume
from models import SearchCriteria, ExportFormat
from config import Config

def test_agent_initialization():
    """Test that all agents initialize correctly."""
    print("🧪 Testing agent initialization...")
    
    try:
        # This should work even without OpenAI API key for initialization
        job_hunter = JobHunterOrchestrator()
        
        print("✅ All agents initialized successfully")
        print(f"   - Jobs Fetcher: {job_hunter.jobs_fetcher.name}")
        print(f"   - Resume Builder: {job_hunter.resume_builder.name}")
        print(f"   - Cover Letter Builder: {job_hunter.cover_letter_builder.name}")
        print(f"   - Exporter: {job_hunter.exporter.name}")
        print(f"   - Tracker: {job_hunter.tracker.name}")
        
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {str(e)}")
        return False

def test_model_validation():
    """Test that all data models work correctly."""
    print("\n🧪 Testing data model validation...")
    
    try:
        # Test SearchCriteria
        search_criteria = SearchCriteria(
            keywords=["Python Developer"],
            location="Remote",
            job_boards=["indeed"]
        )
        print("✅ SearchCriteria model works")
        
        # Test MasterResume
        master_resume = load_sample_master_resume()
        print("✅ MasterResume model works")
        
        # Test model serialization
        search_dict = search_criteria.model_dump()
        resume_dict = master_resume.model_dump()
        print("✅ Model serialization works")
        
        return True
    except Exception as e:
        print(f"❌ Model validation failed: {str(e)}")
        return False

def test_directory_structure():
    """Test that all required directories exist."""
    print("\n🧪 Testing directory structure...")
    
    try:
        required_dirs = [
            Config.APPLICATIONS_DIR,
            Config.DATA_DIR,
            Config.TEMPLATES_DIR
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                print(f"✅ Directory exists: {directory}")
            else:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
        
        return True
    except Exception as e:
        print(f"❌ Directory structure test failed: {str(e)}")
        return False

def test_base_agent_structure():
    """Test base agent structure without OpenAI calls."""
    print("\n🧪 Testing base agent structure...")
    
    try:
        from base_agent import BaseAgent, AgentResponse
        from jobs_fetcher import JobsFetcherAgent
        
        # Test agent response model
        response = AgentResponse(
            success=True,
            message="Test response",
            data={"test": "data"}
        )
        print("✅ AgentResponse model works")
        
        # Test agent info (doesn't require API key)
        jobs_agent = JobsFetcherAgent()
        agent_info = jobs_agent.get_agent_info()
        print(f"✅ Agent info retrieval works: {agent_info['name']}")
        
        return True
    except Exception as e:
        print(f"❌ Base agent structure test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🔍 Job Hunter - OpenAI Agent Structure Tests")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_model_validation,
        test_base_agent_structure,
        test_agent_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Job Hunter OpenAI agent structure is ready.")
        if not Config.OPENAI_API_KEY:
            print("⚠️  Note: Set OPENAI_API_KEY environment variable to enable full functionality.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())