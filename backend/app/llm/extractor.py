import os
import requests
from dotenv import load_dotenv


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-40-mini"
load_dotenv()

def extract_job_insights(description: str):
    prompt = f"""
    You are an AI that analyzes job postings.

    Extract the following insights from the job description:
    1. Required skills (technical and soft skills)
    2. Tech stack (programming languages, frameworks, tools, cloud platforms)
    3. Seniority level (e.g., Junior, Mid-Level, Senior, Lead, Principal)
    4. A concise 3-5 sentence summary of the role

    Return you answer in JSON format with keys:
    - skills:
    - summary:
    - seniority:
    - tech_stack:

    Job Description:
    {description}
    """

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
    )

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Parse the JSON response from the gpt model
    import json
    return json.loads(content)
