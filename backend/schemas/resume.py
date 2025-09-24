from pydantic import BaseModel
from typing import List

class ResumeUploadRequest(BaseModel):
    file_path: str

class ResumeResponse(BaseModel):
    name: str
    email: str
    experiences: List[str]
    skills: List[str]
