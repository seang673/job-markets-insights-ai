const API_BASE_URL = "http://localhost:8000/api";

export async function scrapeJobs(role: string): Promise<void> {
  const url = `${API_BASE_URL}/scrape?role=${encodeURIComponent(role)}`;
  const res = await fetch(url, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`Failed to trigger job scraping: ${res.statusText}`);
  }
}