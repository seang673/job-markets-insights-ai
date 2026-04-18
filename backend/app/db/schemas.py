from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Pydantic models for job postings. Represents how data is validated and returned
class JobPostingBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = "indeed"
    date_posted: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPosting(JobPostingBase):
    id: int
    date_scraped: Optional[datetime] = None
    skills_extracted: Optional[str] = None
    summary: Optional[str] = None
    embedding_id: Optional[str] = None

    class Config:
        from_attributes = True   #Tells Pydantic to read data from ORM models using attribute access
