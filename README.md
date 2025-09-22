# Job Hunter - OpenAI-Powered Job Application Automation

A comprehensive Python application that automates the job application process using OpenAI-powered agents. The system scrapes job postings, generates tailored resumes and cover letters, exports documents, and tracks application progress.

## 🤖 OpenAI Agent Architecture

This application leverages a sophisticated OpenAI agent structure where each component is implemented as an intelligent agent:

### Base Agent Structure
All agents inherit from `BaseAgent` which provides:
- **OpenAI Integration**: Standardized OpenAI API communication
- **Function Calling**: Support for OpenAI function calling capabilities
- **Error Handling**: Robust error handling and logging
- **Response Standardization**: Uniform response format across all agents
- **Configuration Management**: Centralized configuration and settings

### Agent Ecosystem

#### 1. 📋 Jobs Fetcher Agent (`jobs_fetcher.py`)
- **Purpose**: Scrapes and normalizes job postings from multiple job boards
- **AI Capabilities**: 
  - Intelligent data extraction from HTML content
  - Job posting normalization and deduplication
  - Quality assessment and filtering
- **Supported Sources**: Indeed, LinkedIn, ZipRecruiter (mock implementations included)

#### 2. 📝 Resume Builder Agent (`resume_builder.py`)
- **Purpose**: Creates tailored resumes based on job requirements
- **AI Capabilities**:
  - Job requirement analysis and skill extraction
  - Experience relevance scoring and selection
  - Resume content optimization for ATS compatibility
  - Dynamic summary generation

#### 3. 📨 Cover Letter Builder Agent (`cover_letter_builder.py`)
- **Purpose**: Generates personalized cover letters
- **AI Capabilities**:
  - Company culture analysis from job postings
  - Experience-to-requirement matching
  - Compelling narrative generation
  - Tone and style optimization

#### 4. 💾 Exporter Agent (`exporter.py`)
- **Purpose**: Exports documents to PDF and DOCX formats
- **AI Capabilities**:
  - Layout optimization recommendations
  - Content formatting decisions
  - File organization and naming

#### 5. 📊 Tracker Agent (`tracker.py`)
- **Purpose**: Tracks applications and provides insights
- **AI Capabilities**:
  - Application pattern analysis
  - Success rate predictions
  - Follow-up timing recommendations
  - Strategic insights generation

## 🚀 Features

- **Multi-Source Job Scraping**: Fetch jobs from multiple job boards simultaneously
- **Intelligent Resume Tailoring**: AI-powered resume customization for each job
- **Personalized Cover Letters**: Generate compelling, job-specific cover letters
- **Document Export**: Professional PDF and DOCX output
- **Application Tracking**: SQLite/PostgreSQL database with analytics
- **Follow-up Management**: Automated follow-up recommendations
- **Insights & Analytics**: AI-generated job search insights

## 📁 Project Structure

```
Job_Hunter/
├── base_agent.py           # Base OpenAI agent class
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── jobs_fetcher.py        # Jobs fetching agent
├── resume_builder.py      # Resume building agent
├── cover_letter_builder.py # Cover letter agent
├── exporter.py            # Document export agent
├── tracker.py             # Application tracking agent
├── main.py                # Main orchestrator
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── Applications/         # Generated documents folder
├── data/                # Data storage
└── templates/           # Document templates
```

## 🛠 Installation

1. Clone the repository:
```bash
git clone https://github.com/twosidesofai/Job_Hunter.git
cd Job_Hunter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

## ⚙️ Configuration

Set up your `.env` file with:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Database Configuration
DATABASE_URL=sqlite:///job_hunter.db

# Application Settings
DEFAULT_LOCATION=Remote
MAX_JOBS_PER_SEARCH=50
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2000
```

## 🎯 Usage

### Quick Start

Run the complete workflow:

```bash
python main.py
```

### Programmatic Usage

```python
from main import JobHunterOrchestrator, load_sample_master_resume
from models import SearchCriteria, ExportFormat

# Initialize the orchestrator
job_hunter = JobHunterOrchestrator()

# Load your master resume
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
    max_applications=5,
    export_format=ExportFormat.BOTH
)
```

### Individual Agent Usage

```python
# Use individual agents
from jobs_fetcher import JobsFetcherAgent
from resume_builder import ResumeBuilderAgent

# Initialize agents
jobs_agent = JobsFetcherAgent()
resume_agent = ResumeBuilderAgent()

# Search for jobs
jobs_response = jobs_agent.process_request(
    "search_jobs",
    context=search_criteria.model_dump()
)

# Build tailored resume
resume_response = resume_agent.process_request(
    "build_resume",
    context={
        "job_posting": job_posting.model_dump(),
        "master_resume": master_resume.model_dump()
    }
)
```

## 📊 Application Tracking

The system automatically tracks all applications with:

- **Status Management**: Track application progress through different stages
- **Analytics**: Response rates, success patterns, and trends
- **Follow-up Reminders**: Automated follow-up recommendations
- **Insights**: AI-generated strategic recommendations

## 🎨 Customization

### Adding New Job Boards

Extend the `JobsFetcherAgent` to support additional job boards:

```python
def _search_new_board(self, criteria: SearchCriteria) -> List[JobPosting]:
    # Implement scraping logic for new job board
    pass
```

### Custom Resume Templates

Modify the `ExporterAgent` to use custom document templates and styling.

### Enhanced AI Prompts

Customize the system prompts in each agent class to fine-tune AI behavior.

## 🧪 Testing

Run tests to ensure all agents are working correctly:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

- **Ethical Usage**: Always respect job board terms of service and rate limits
- **Data Privacy**: Ensure personal information is handled securely
- **API Costs**: Monitor OpenAI API usage to manage costs
- **Job Board Compliance**: Some job boards may restrict automated access

## 🆘 Support

For support, please open an issue on GitHub or contact the maintainers.

## 🔮 Future Enhancements

- **Email Integration**: Automated application submission
- **Interview Scheduling**: Calendar integration for interview management
- **Salary Negotiation**: AI-powered salary negotiation assistance
- **Market Analysis**: Job market trends and insights
- **Mobile App**: Cross-platform mobile application

---

Built with ❤️ using OpenAI, Python, and modern AI agent architecture.