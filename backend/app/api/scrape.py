
from fastapi import APIRouter, Depends
from app.scraping.indeed_scraper import scrape_indeed
from app.db.crud import Session
from app.ingestion.ingest_jobs import run_ingestion
from app.llm.process_jobs import process_unprocessed_jobs
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_get_db

router = APIRouter()

@router.post("/scrape")
async def scrape_jobs(role: str, db: AsyncSession = Depends(async_get_db)):
    await run_ingestion(role, db)
    await process_unprocessed_jobs(db)
    return {"status": "scraping_jobs", "role": role}