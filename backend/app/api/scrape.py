
from fastapi import APIRouter, Depends
from app.scraping.indeed_scraper import scrape_indeed
from backend.app.db.crud import Session
from backend.app.ingestion.ingest_jobs import run_ingestion

router = APIRouter()

@router.get("/scrape")
def scrape_jobs(role: str, db: Session = Depends(get_db)):
    run_ingestion(role)
    return {"status": "ok", "role": role}