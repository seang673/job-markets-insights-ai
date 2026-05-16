import os
import json
from dotenv import load_dotenv
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

load_dotenv()

MODEL = "gpt-4o-mini"

system_prompt = """
You are an AI system that extracts structured insights from job descriptions.
Respond ONLY with valid JSON in this exact format:

{
    "skills": [...],
    "tech_stack": [...],
    "seniority": "Junior | Mid-Level | Senior | Lead | Principal | Unknown",
    "summary": "3-5 sentence summary"
}
"""

async def extract_job_insights(description: str):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description}
            ],
            temperature=0
        )

        # Validate structure
        if not hasattr(response, "choices") or len(response.choices) == 0:
            print("LLM returned no choices:", response)
            return None

        content = response.choices[0].message.content
        if not content:
            print("LLM returned empty content:", response)
            return None

        # Parse JSON safely
        try:
            return json.loads(content)
        except Exception:
            print("LLM returned invalid JSON:", content)
            return None

    except Exception as e:
        print("Extractor error:", e)
        return None
