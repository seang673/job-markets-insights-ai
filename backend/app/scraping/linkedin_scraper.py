import asyncio
import json
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import httpx

async def fetch_job_details(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        desc_el = soup.find("div", {"class": "description__text"})
        date_el = soup.find("span", {"class": "posted-time-ago__text"})

        description = desc_el.get_text("\n", strip=True) if desc_el else None
        date_posted = date_el.get_text(strip=True) if date_el else None

        return description, date_posted

async def scrape_linkedin(query="software engineer", location="Remote", limit=10):
    results = []

    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={query}&location={location}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)

    if response.status_code != 200:
        print("LinkedIn request failed:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("li", {"class": "base-card"})

    for card in cards[:limit]:
        title = card.find("h3", {"class": "base-search-card__title"})
        company = card.find("h4", {"class": "base-search-card__subtitle"})
        location_el = card.find("span", {"class": "job-search-card__location"})
        link = card.find("a", {"class": "base-card__full-link"})
        if not link or not link.get("href"):
            continue
        description, date_posted = await fetch_job_details(link["href"])

        results.append({
            "title": title.get_text(strip=True) if title else None,
            "company": company.get_text(strip=True) if company else None,
            "location": location_el.get_text(strip=True) if location_el else None,
            "description": description,
            "date_posted": date_posted,
            "url": link["href"] if link else None,
            "source": "linkedin",
        })

    return results


# Manual test
if __name__ == "__main__":
    jobs = asyncio.run(scrape_linkedin("software engineer", "Remote"))
    print(jobs)
