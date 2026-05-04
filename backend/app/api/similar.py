from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db import models

from embeddings.embedder import embed_job
from embeddings.vector_store import query_similar_jobs

router = APIRouter()

@router.get("/similar/{job_id}")
async def get_similar_jobs(job_id: int, top_k: int = 5):
    db: Session = SessionLocal()

    #Fetch the job from the database
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()

    #If Job not found
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    #Build embedding input
    job_dict = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "summary": job.summary,
        "skills": job.skills_extracted.split(", ") if job.skills_extracted else [],
        "tech_stack": job.tech_stack.split(", ") if job.tech_stack else [],
        "description": job.description
    }

    #Generate embedding for the job
    embedding = await embed_job(job_dict)

    #Query similar jobs from ChromaDB
    results = query_similar_jobs(embedding=embedding, top_k=top_k)

    #Format results
    similar_jobs = []
    for idx, match_id in enumerate(results["ids"][0]):
        if str(job_id) == match_id:
            continue  # Skip the same job
        similar_jobs.append({
            "job_id": match_id,
            "score": results["distances"][0][idx],
            "metadata": results["metadatas"][0][idx]
        })

    return {"results": similar_jobs}