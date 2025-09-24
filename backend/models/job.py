from pydantic import BaseModel
from typing import Optional

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: Optional[str]
    salary: Optional[str]
    url: Optional[str]
