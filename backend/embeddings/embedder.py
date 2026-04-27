import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"

def build_embedding(job: Dict) -> str:
    """
    Convert a job posting into a structured text block for embedding.
    """
    title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    summary = job.get("summary", "")
    tech_stack = ", ".join(job.get("tech_stack", []))
    skills = ", ".join(job.get("skills_extracted", []))
    description = job.get("description", "")

    return f"""
    Title: {title}
    Company: {company}
    Location: {location}
    Summary: {summary}
    Tech Stack: {tech_stack}
    Skills: {skills}
    Description: {description}
    """

async def embed_job(job: Dict) -> List[float]:
    """
    Generates an embedding vector for a single job posting.
    """
    text = build_embedding(job)

    response = await client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )

    return response.data[0].embedding