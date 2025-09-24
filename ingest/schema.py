from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ExperienceItem(BaseModel):
    company: str
    role: str
    start: str  # YYYY-MM
    end: str    # YYYY-MM or 'present'
    bullets: List[str]
    tech: List[str]

class EducationItem(BaseModel):
    school: str
    degree: str
    year: str  # YYYY

class JobPrefs(BaseModel):
    titles: List[str]
    industries: List[str]
    locations: List[str]
    remote_ok: bool = False
    salary_min: int = 0

class ResumeProfile(BaseModel):
    name: str
    title: str
    summary: str
    skills: List[str]
    experience: List[ExperienceItem]
    education: List[EducationItem]
    certs: List[str]
    locations: List[str]
    job_prefs: JobPrefs

    @classmethod
    def validate_profile(cls, data: Dict[str, Any]) -> "ResumeProfile":
        return cls(**data)
