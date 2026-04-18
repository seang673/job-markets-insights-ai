from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.llm.extractor import extract_job_insights

#Add pipeline to update database

def process_unprocessed_jobs():
    db: Session = SessionLocal()

    jobs = db.query(models.JobPosting).filter(
        (models.JobPosting.skills_extracted.is_(None)) |
        (models.JobPosting.summary.is_(None))).all()

    print(f"Found {len(jobs)} unprocessed jobs.")

    for job in jobs:
        if not job.description:
            continue
        try:
             insights = extract_job_insights(job.description)

             job.skills_extracted = ", ".join(insights["skills"])
             job.summary = insights["summary"]

             db.add(job)
             db.commit()

             print(f"Processed job {job.id}: {job.title}")

        except Exception as e:
            print(f"Error processing job {job.id}: {e}")
    db.close()

if __name__ == "__main__":
    process_unprocessed_jobs()

