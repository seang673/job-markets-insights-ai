
from playwright.async_api import async_playwright

import asyncio
from playwright.async_api import async_playwright

#Responsible for scraping Indeed job postings using Playwright
async def scrape_indeed(query: str = "software engineer", location: str = "remote", limit: int = 10):
    """
    Returns a list of dicts matching your JobPostingCreate schema.
    """

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  #Runs Chrome invisibly
        page = await browser.new_page()

        url = f"https://www.indeed.com/jobs?q={query}&l={location}"
        await page.goto(url, timeout=60000)

        # Waits for job cards to load
        await page.wait_for_selector("div.job_seen_beacon")

        #Extracts job data from each card
        job_cards = await page.query_selector_all("div.job_seen_beacon")

        for card in job_cards[:limit]:
            title = await card.query_selector("h2.jobTitle")
            company = await card.query_selector("span.companyName")
            location_el = await card.query_selector("div.companyLocation")
            description_el = await card.query_selector("div.job-snippet")
            date_el = await card.query_selector("span.date")

            job = {
                "title": (await title.inner_text()) if title else None,
                "company": (await company.inner_text()) if company else None,
                "location": (await location_el.inner_text()) if location_el else None,
                "description": (await description_el.inner_text()) if description_el else None,
                "url": await card.get_attribute("data-jk"),
                "source": "indeed",
                "date_posted": (await date_el.inner_text()) if date_el else None,
            }

            # Convert job key to full URL
            if job["url"]:
                job["url"] = f"https://www.indeed.com/viewjob?jk={job['url']}"

            results.append(job)

        await browser.close()

    return results


# For quick manual testing
if __name__ == "__main__":
    jobs = asyncio.run(scrape_indeed("software engineer", "remote"))
    print(jobs)
