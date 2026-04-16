from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    source = Column(String(100), default="indeed")

    date_posted = Column(String(100), nullable=True)
    date_scraped = Column(DateTime(timezone=True), server_default=func.now())

    # LLM‑ready fields (filled later)
    skills_extracted = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    embedding_id = Column(String(255), nullable=True)
