from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.llm.extractor import extract_job_insights

from embeddings.vector_store import upsert_job_embedding
from embeddings.embedder import embed_job
from app.llm.extractor import extract_fields #NOT IMPLEMNTED YET

#Add pipeline to update database

async def process_unprocessed_jobs():
    db: Session = SessionLocal()

    #Recieves raw jobs
    jobs = db.query(models.JobPosting).filter(
        (models.JobPosting.skills_extracted.is_(None)) |
        (models.JobPosting.summary.is_(None)) |
        (models.JobPosting.tech_stack.is_(None)) |
        (models.JobPosting.seniority.is_(None))).all()

    print(f"Found {len(jobs)} unprocessed jobs.")

    for job in jobs:
        if not job.description:
            continue
        try:

            #LLM extraction
            insights = extract_job_insights(job.description)

            job.skills_extracted = ", ".join(insights["skills"])
            job.summary = insights["summary"]
            job.seniority = insights["seniority"]
            job.tech_stack = ", ".join(insights["tech_stack"])

            embedding = await embed_job({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "summary": job.summary,
                "tech_stack": job.tech_stack,
                "skills": job.skills_extracted,
                "description": job.description
            })
            
            #Store embedding in ChromaDB
            upsert_job_embedding(job_id=str(job.id), embedding=embedding, metadata={
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url
            })

            db.add(job)
            db.commit()

            print(f"Processed job {job.id}: {job.title}")

        except Exception as e:
            print(f"Error processing job {job.id}: {e}")
    db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(process_unprocessed_jobs())

