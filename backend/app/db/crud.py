from sqlalchemy.orm import Session
from . import models, schemas

#Create a new job posting
def create_job_posting(db: Session, job: schemas.JobPostingCreate):
    db_job = models.JobPosting(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        url=job.url,
        source=job.source,
        date_posted=job.date_posted
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

#Get all job postings with pagination
def get_job_postings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JobPosting).offset(skip).limit(limit).all()

#Get a single job posting by ID
def get_job_posting(db: Session, job_id: int):
    return db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()