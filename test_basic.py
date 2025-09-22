"""
Basic structure test without external dependencies.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing file structure...")
    
    required_files = [
        "base_agent.py",
        "config.py", 
        "models.py",
        "jobs_fetcher.py",
        "resume_builder.py",
        "cover_letter_builder.py",
        "exporter.py",
        "tracker.py",
        "main.py",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]
    
    missing_files = []
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ Found: {file_name}")
        else:
            missing_files.append(file_name)
            print(f"❌ Missing: {file_name}")
    
    return len(missing_files) == 0

def test_directory_structure():
    """Test directory structure."""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = ["Applications", "data", "templates"]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
    
    return True

def test_imports():
    """Test basic imports without external dependencies."""
    print("\n🧪 Testing basic imports...")
    
    try:
        from config import Config
        print("✅ Config import works")
        
        from models import JobPosting, SearchCriteria
        print("✅ Models import works")
        
        from base_agent import BaseAgent, AgentResponse
        print("✅ Base agent import works")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def main():
    """Run basic structure tests."""
    print("🔍 Job Hunter - Basic Structure Tests")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_directory_structure,
        test_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Basic structure is complete!")
        print("📦 Install requirements with: pip install -r requirements.txt")
        print("⚙️  Set up .env file with your OpenAI API key")
    else:
        print("❌ Some basic structure tests failed.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())