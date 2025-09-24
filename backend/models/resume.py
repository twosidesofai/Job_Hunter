from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: Optional[str]
    description: Optional[str]

class Resume(BaseModel):
    name: str
    email: str
    experiences: List[Experience]
    skills: List[str]
