import asyncio
from playwright.async_api import async_playwright

# Responsible for scraping Indeed job postings using Playwright
async def scrape_indeed(
    query: str = "software engineer",
    location: str = "remote",
    limit: int = 10
):
    """
    Returns a list of dicts matching JobPostingCreate schema.
    """

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ])
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )

        url = f"https://www.indeed.com/jobs?q={query}&l={location}"
        await page.goto(url, timeout=60000)

        # Handle cookie banner if present
        for text in ["Accept", "OK", "Continue", "I agree"]:
            try:
                await page.click(f"button:has-text('{text}')", timeout=2000)
                break
            except:
                pass

        await page.evaluate("window.scrollBy(0, 500)")
        await page.wait_for_timeout(500)
        await page.evaluate("window.scrollBy(0, 1000)")
        await page.wait_for_timeout(500)

        html = await page.content()
        if "captcha" in html.lower() or "verify" in html.lower():
            print("CAPTCHA detected")
            return []   

        # Wait for job cards (multiple layout support)
        await page.wait_for_selector(
            "div.slider_container, div.job_seen_beacon, div.cardOutline",
            timeout=60000
        )

        # Extract job cards
        job_cards = await page.query_selector_all(
            "div.slider_container, div.job_seen_beacon, div.cardOutline"
        )

        for card in job_cards[:limit]:
            #Title
            title_el = await card.query_selector("h2.jobTitle span")
            title = await title_el.inner_text() if title_el else None

            #Company
            company_el = await card.query_selector("span.companyName")
            company = await company_el.inner_text() if company_el else None

            # Location
            location_el = await card.query_selector("div.companyLocation")
            location_text = await location_el.inner_text() if location_el else None

            # Description snippet
            desc_el = await card.query_selector("div.job-snippet")
            description = await desc_el.inner_text() if desc_el else None

            # Date posted
            date_el = await card.query_selector("span.date")
            date_posted = await date_el.inner_text() if date_el else None

            # Job key (jk)
            jk = await card.get_attribute("data-jk")
            url = f"https://www.indeed.com/viewjob?jk={jk}" if jk else None

            job = {
                "title": title,
                "company": company,
                "location": location_text,
                "description": description,
                "url": url,
                "source": "indeed",
                "date_posted": date_posted,
            }

            results.append(job)

        await browser.close()

    return results


# For quick manual testing
if __name__ == "__main__":
    jobs = asyncio.run(scrape_indeed("software engineer", "remote"))
    print(jobs)
