import asyncio
import requests
from app.scaping.indeed_scraper import scrape_indeed

#FastAPI POST route for ingesting scraped jobs into the database
API_URL = "http://localhost:8000/api/jobs"

async def run_ingestion():
    jobs = await scrape_indeed("software engineer", "remote", limit=10) #Run the scraper
    for job in jobs:
        try:
            response = requests.post(API_URL, json=job)  #Post each job
            if response.status_code == 200:
                print(f"Successfully ingested job: {job['title']} at {job['company']}")
            else:
                print(f"✗ Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"Error: {e}") 

if __name__ == "__main__":
    asyncio.run(run_ingestion())