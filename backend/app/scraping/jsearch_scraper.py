import asyncio
import httpx
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
from dotenv import load_dotenv

load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
async def fetch_job_details(job_id: str):
    # Correct job detail API
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}?geoId=103644278"

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=60
        )

    text = resp.text

    # Try JSON first
    try:
        data = resp.json()
        description = data.get("description")
        date_posted = data.get("listedAt")
        full_location = data.get("formattedLocationFull", "")
        print("DESCRIPTION FOUND:", bool(description))

        return description, date_posted, full_location
    except Exception:
        pass  # JSON failed → HTML fallback

    # HTML fallback
    soup = BeautifulSoup(text, "html.parser")

    # 1. Extract description (multiple fallbacks)
    description = None

    # Primary selector
    desc_el = soup.select_one("div.show-more-less-html__markup")
    if desc_el:
        description = desc_el.get_text(" ", strip=True)

    # Fallback 1 — older LinkedIn layout
    if not description:
        desc_el = soup.select_one("div.description__text")
        if desc_el:
            description = desc_el.get_text(" ", strip=True)

    # Fallback 2 — some regions wrap description differently
    if not description:
        desc_el = soup.find("section", {"class": lambda c: c and "description" in c.lower()})
        if desc_el:
            description = desc_el.get_text(" ", strip=True)

    # Fallback 3 — last resort: search for any large text block
    if not description:
        paragraphs = soup.find_all("p")
        if paragraphs:
            description = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

    # 2. Extract location
    loc_el = soup.select_one("span.topcard__flavor--bullet")
    full_location = loc_el.get_text(strip=True) if loc_el else None

    # 3. Extract posted date
    date_el = soup.select_one("span.posted-time-ago__text")
    date_posted = date_el.get_text(strip=True) if date_el else None

    return description, date_posted, full_location

async def scrape_jsearch(query="software engineer", limit=10):
    url = "https://jsearch.p.rapidapi.com/search"

    params = {
        "query": query,
        "num_pages": 1,
        "page": 1
    }
    if not JSEARCH_API_KEY:
        raise RuntimeError("JSEARCH_API_KEY is missing! Set it in your environment variables.")

    headers = {
        "X-RapidAPI-Key": str(JSEARCH_API_KEY),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers, timeout=30)

    data = resp.json()

    jobs = []
    for job in data.get("data", [])[:limit]:
        jobs.append({
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_city") or job.get("job_country"),
            "description": job.get("job_description"),
            "date_posted": job.get("job_posted_at_datetime_utc"),
            "url": job.get("job_apply_link") or job.get("job_apply_is_direct"),
            "source": "jsearch"
        })

    return jobs

if __name__ == "__main__":
    jobs = asyncio.run(scrape_jsearch("software engineer"))
    print(jobs)
