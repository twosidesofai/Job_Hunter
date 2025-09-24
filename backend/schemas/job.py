from pydantic import BaseModel
from typing import List, Optional

class JobSearchRequest(BaseModel):
    keywords: List[str]
    locations: List[str]
    remote_only: bool = False
    top: int = 10

class JobSearchResponse(BaseModel):
    jobs: List[dict]
