import asyncio
import json
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import httpx


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
    cards = soup.find_all("li")

    for card in cards[:limit]:
        title = card.find("h3", {"class": "base-search-card__title"})
        company = card.find("h4", {"class": "base-search-card__subtitle"})
        location_el = card.find("span", {"class": "job-search-card__location"})
        link = card.find("a", {"class": "base-card__full-link"})

        results.append({
            "title": title.get_text(strip=True) if title else None,
            "company": company.get_text(strip=True) if company else None,
            "location": location_el.get_text(strip=True) if location_el else None,
            "description": None,  # fetched separately if needed
            "url": link["href"] if link else None,
            "source": "linkedin",
            "date_posted": None,
        })

    return results


# Manual test
if __name__ == "__main__":
    jobs = asyncio.run(scrape_linkedin("software engineer", "Remote"))
    print(jobs)
