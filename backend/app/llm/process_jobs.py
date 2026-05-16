from chromadb import db
from sqlalchemy.orm import Session
from app.db import models
from app.llm.extractor import extract_job_insights
from sqlalchemy import or_

from app.api.insights import Depends, select
from app.db.database import AsyncSession
from embeddings.vector_store import upsert_job_embedding
from embeddings.embedder import embed_job


#Add pipeline to update database

async def process_unprocessed_jobs(db: AsyncSession):

    #Recieves raw jobs that are unprocessed
    result = await db.execute(
         select(models.JobPosting).where(
            or_(
                models.JobPosting.skills_extracted.is_(None),
                models.JobPosting.skills_extracted == "",
                models.JobPosting.summary.is_(None),
                models.JobPosting.summary == "",
                models.JobPosting.tech_stack.is_(None),
                models.JobPosting.tech_stack == "",
                models.JobPosting.seniority.is_(None),
                models.JobPosting.seniority == ""
            )
        )
    )

    jobs = result.scalars().all()
    print(f"Found {len(jobs)} unprocessed jobs.")

    for job in jobs:
        if not job.description:
            print(f"Job {job.id} has no description — marking as processed anyway.")
            job.skills_extracted = ""
            job.summary = ""
            job.seniority = ""
            job.tech_stack = ""
            await db.commit()
            continue

        try:
            # LLM extraction of insights from job
            print("Extracting insights for job:", job.id)
            insights = await extract_job_insights(job.description)
            job.skills_extracted = ", ".join(insights["skills"])
            job.summary = insights["summary"]
            job.seniority = insights["seniority"]
            job.tech_stack = ", ".join(insights["tech_stack"])


            # Embedding generation for job
            embedding = await embed_job({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "summary": job.summary,
                "tech_stack": job.tech_stack,
                "skills": job.skills_extracted,
                "description": job.description
            })

            # Stores embedding as vector in ChromaDB
            upsert_job_embedding(
                job_id=str(job.id),
                embedding=embedding,
                metadata={
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "url": job.url
                }
            )

            # Persist updates to database
            db.add(job)
            await db.commit()

            print(f"Processed job {job.id}: {job.title}")

        except Exception as e:
            print(f"Error processing job {job.id}: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(process_unprocessed_jobs())

