
from fastapi import APIRouter
from app.scraping.indeed_scraper import scrape_indeed

router = APIRouter()

@router.get("/scrape")
async def scrape_jobs():
    jobs = await scrape_indeed()
    return {"jobs": jobs}