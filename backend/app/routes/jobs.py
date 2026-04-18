from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import crud, models, schemas
from app.db.database import SessionLocal

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Create job posting endpoint
@router.post("", response_model=schemas.JobPosting)
def create_job(job: schemas.JobPostingCreate, db: Session = Depends(get_db)):
    return crud.create_job_posting(db=db, job=job)

#Get all job postings endpoint
@router.get("", response_model=list[schemas.JobPosting])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_job_postings(db=db, skip=skip, limit=limit)

#Get single job posting by ID endpoint
@router.get("/{job_id}", response_model=schemas.JobPosting)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job_posting(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job