import {InsightsOverview} from "../types/insights";

const API_BASE_URL = "http://localhost:8000/api";

export async function fetchInsightsOverview(role?: string): Promise<InsightsOverview> {
  const url = role ? `${API_BASE_URL}/insights/overview?role=${encodeURIComponent(role)}` : `${API_BASE_URL}/insights/overview`;
  const res = await fetch(url);

  if (!res.ok) {
    throw new Error(`Failed to fetch insights overview: ${res.statusText}`);
  }

  return res.json();
}