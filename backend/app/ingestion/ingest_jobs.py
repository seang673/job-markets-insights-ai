import asyncio
import requests
from app.scraping.linkedin_scraper import scrape_linkedin
from app.db.crud import AsyncSession, create_job_posting
from app.db.schemas import JobPostingCreate


#FastAPI POST route for ingesting scraped jobs into the database
API_URL = "http://localhost:8000/api/jobs"

async def run_ingestion(role_query: str, db: AsyncSession):
    jobs = await scrape_linkedin(role_query) #Run the scraper
    print("Scraped jobs:", len(jobs))
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

        await create_job_posting(db, job_data)




if __name__ == "__main__":
    asyncio.run(run_ingestion())