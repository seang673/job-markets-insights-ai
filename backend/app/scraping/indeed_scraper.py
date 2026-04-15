
from playwright.async_api import async_playwright

async def scrape_indeed(query="software engineer", location="remote"):
    url = f"https://www.indeed.com/jobs?q={query}&l={location}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        job_cards = page.locator("div.job_seen_beacon")
        count = await job_cards.count()

        results = []

        for i in range(min(count, 10)):  # limit to top 10 results
            card = job_cards.nth(i)

            title = await card.locator("h2 span").inner_text()
            company = await card.locator("span.companyName").inner_text()
            location = await card.locator("div.companyLocation").inner_text()

            results.append({
                "title": title,
                "company": company,
                "location": location
            })

        await browser.close()
        return results