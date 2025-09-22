"""
Data models for the Job Hunter application.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

try:
    from pydantic import BaseModel, Field, HttpUrl
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Warning: pydantic package not installed. Using basic data structures.")
    
    # Fallback base class
    class BaseModel:
        def model_dump(self):
            return self.__dict__
    
    # Mock Field for compatibility
    def Field(**kwargs):
        return None
    
    # Mock HttpUrl
    HttpUrl = str

class JobStatus(str, Enum):
    """Enumeration for job application status."""
    FOUND = "found"
    APPLIED = "applied"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    REJECTED = "rejected"
    OFFERED = "offered"
    ACCEPTED = "accepted"

class JobPosting(BaseModel):
    """Normalized job posting data model."""
    id: Optional[str] = Field(default=None, description="Unique identifier for the job posting")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    description: str = Field(description="Job description")
    requirements: str = Field(description="Job requirements")
    posting_url: HttpUrl = Field(description="URL to the original job posting")
    location: Optional[str] = Field(default=None, description="Job location")
    salary_range: Optional[str] = Field(default=None, description="Salary range if available")
    job_type: Optional[str] = Field(default=None, description="Job type (full-time, part-time, contract)")
    remote_ok: Optional[bool] = Field(default=None, description="Whether remote work is allowed")
    source: str = Field(description="Job board source (LinkedIn, Indeed, etc.)")
    posted_date: Optional[datetime] = Field(default=None, description="When the job was posted")
    scraped_date: datetime = Field(default_factory=datetime.now, description="When we scraped this job")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }

class ExperienceItem(BaseModel):
    """Experience item for resume building."""
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    duration: str = Field(description="Duration of employment")
    description: str = Field(description="Job description")
    skills: List[str] = Field(default_factory=list, description="Relevant skills used")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")

class EducationItem(BaseModel):
    """Education item for resume building."""
    degree: str = Field(description="Degree earned")
    institution: str = Field(description="Educational institution")
    year: Optional[str] = Field(default=None, description="Graduation year")
    gpa: Optional[str] = Field(default=None, description="GPA if relevant")

class MasterResume(BaseModel):
    """Master resume data structure."""
    personal_info: Dict[str, str] = Field(description="Personal information (name, email, phone, etc.)")
    summary: str = Field(description="Professional summary")
    experience: List[ExperienceItem] = Field(description="Work experience")
    education: List[EducationItem] = Field(description="Education background")
    skills: Dict[str, List[str]] = Field(description="Skills categorized by type")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    projects: List[Dict[str, str]] = Field(default_factory=list, description="Personal/professional projects")

class TailoredResume(BaseModel):
    """Tailored resume for a specific job."""
    job_posting_id: str = Field(description="ID of the job posting this resume is for")
    personal_info: Dict[str, str] = Field(description="Personal information")
    summary: str = Field(description="Tailored professional summary")
    experience: List[ExperienceItem] = Field(description="Selected and tailored experience")
    education: List[EducationItem] = Field(description="Education background")
    skills: List[str] = Field(description="Most relevant skills for this job")
    certifications: List[str] = Field(default_factory=list, description="Relevant certifications")
    projects: List[Dict[str, str]] = Field(default_factory=list, description="Relevant projects")

class CoverLetter(BaseModel):
    """Cover letter data model."""
    job_posting_id: str = Field(description="ID of the job posting this cover letter is for")
    content: str = Field(description="The complete cover letter content")
    key_points: List[str] = Field(description="Key points highlighted in the cover letter")

class JobApplication(BaseModel):
    """Job application tracking model."""
    id: Optional[str] = Field(default=None, description="Unique application ID")
    job_posting: JobPosting = Field(description="The job posting")
    status: JobStatus = Field(default=JobStatus.FOUND, description="Application status")
    applied_date: Optional[datetime] = Field(default=None, description="When application was submitted")
    resume_path: Optional[str] = Field(default=None, description="Path to generated resume file")
    cover_letter_path: Optional[str] = Field(default=None, description="Path to generated cover letter file")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    follow_up_date: Optional[datetime] = Field(default=None, description="When to follow up")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class SearchCriteria(BaseModel):
    """Job search criteria."""
    keywords: List[str] = Field(description="Job search keywords")
    location: str = Field(description="Preferred job location")
    job_type: Optional[str] = Field(default=None, description="Job type filter")
    salary_min: Optional[int] = Field(default=None, description="Minimum salary")
    salary_max: Optional[int] = Field(default=None, description="Maximum salary")
    remote_ok: Optional[bool] = Field(default=None, description="Remote work acceptable")
    experience_level: Optional[str] = Field(default=None, description="Experience level")
    job_boards: List[str] = Field(default=["indeed", "linkedin"], description="Job boards to search")

class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    DOCX = "docx"
    BOTH = "both"