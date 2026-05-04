import asyncio
import requests
from app.scaping.indeed_scraper import scrape_indeed
from backend.app.db.crud import create_job_posting
from backend.app.db.schemas import JobPostingCreate

#FastAPI POST route for ingesting scraped jobs into the database
API_URL = "http://localhost:8000/api/jobs"

async def run_ingestion(role_query: str):
    jobs = await scrape_indeed(role_query) #Run the scraper
    for job in jobs:
        job_data = JobPostingCreate(
            title=job["title"],
            company=job["company"],
            location=job.get("location"),
            description=job.get("description"),
            url=job.get("url"),
            date_posted=job.get("date_posted"),
            source="indeed",
            role=role_query  
        )
        
        created = create_job_posting(db, job_data)
        
        #Extract skills, summary, seniority
        enrich_job_posting(created.id) # type: ignore
        
        #Embed into vector store
        embed_job_posting(created.id)
       

if __name__ == "__main__":
    asyncio.run(run_ingestion())