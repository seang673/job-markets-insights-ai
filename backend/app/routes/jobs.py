from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud, models, schemas
from app.db.database import async_get_db
from sqlalchemy import delete

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

# Create job posting endpoint
@router.post("", response_model=schemas.JobPosting)
async def create_job(
    job: schemas.JobPostingCreate,
    db: AsyncSession = Depends(async_get_db)
):
    created = await crud.create_job_posting(db=db, job=job)
    return created

# Get all job postings endpoint
@router.get("", response_model=list[schemas.JobPosting])
async def read_jobs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(async_get_db)
):
    jobs = await crud.get_job_postings(db=db, skip=skip, limit=limit)
    return jobs

# Get single job posting by ID endpoint
@router.get("/{job_id}", response_model=schemas.JobPosting)
async def read_job(
    job_id: int,
    db: AsyncSession = Depends(async_get_db)
):
    job = await crud.get_job_posting(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job

# Delete job postings by role endpoint
@router.delete("")
async def delete_jobs(role: str, db: AsyncSession = Depends(async_get_db)):
    stmt = delete(models.JobPosting).where(models.JobPosting.role == role)
    result = await db.execute(stmt)
    await db.commit()

    deleted_count = result.rowcount or 0

    return {"deleted": deleted_count, "role": role}

