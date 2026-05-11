from select import select
from unittest import result
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas

#Create a new job posting
async def create_job_posting(db: AsyncSession, job: schemas.JobPostingCreate):
    db_job = models.JobPosting(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        url=job.url,
        source=job.source,
        date_posted=job.date_posted,
        role=job.role
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job

#Get all job postings with pagination
async def get_job_postings(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.JobPosting).offset(skip).limit(limit)
    )
    return result.scalars().all()

#Get a single job posting by ID
async def get_job_posting(db: AsyncSession, job_id: int):
    result = await db.execute(
        select(models.JobPosting).where(models.JobPosting.id == job_id)
    )
    return result.scalar_one_or_none()