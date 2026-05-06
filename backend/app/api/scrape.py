
from fastapi import APIRouter, Depends
from app.scraping.indeed_scraper import scrape_indeed
from app.db.crud import Session
from app.ingestion.ingest_jobs import run_ingestion
from app.db.database import get_db
from app.llm.process_jobs import process_unprocessed_jobs

router = APIRouter()

@router.post("/scrape")
async def scrape_jobs(role: str, db: Session = Depends(get_db)):
    await run_ingestion(role, db)
    await process_unprocessed_jobs(db)
    return {"status": "scraping_jobs", "role": role}