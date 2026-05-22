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
  "tech_stack": [],
  "skills": [],
  "seniority": "",
  "summary": ""
}

Rules for extraction:

1. "tech_stack" MUST include ONLY concrete technologies like:
   - Programming languages (such as Python, Java, C++, TypeScript)
   - Frameworks (such as React, Django, Spring Boot, FastAPI)
   - Libraries (such as NumPy, Pandas, TensorFlow, PyTorch)
   - Databases (such as PostgreSQL, MongoDB, Redis)
   - Cloud platforms (such as AWS, Azure, GCP)
   - DevOps tools (such as Docker, Kubernetes, Terraform, Jenkins)
   - Other specific tools (such as Git, Linux, Kafka, Spark)

   DO NOT include soft skills, general abilities, or abstract concepts.
   For each word, the first letter should be uppercase, and the rest of the letters in the word should be lowercase.
   If no technologies are mentioned, return an empty array.

2. "skills" should include broader competencies and abilities mentioned in the job description, such as:
   - Soft skills (such as communication, teamwork, leadership)
   - General abilities
   - Methodologies (such as Agile, Scrum, CI/CD)
   - Domain knowledge (such as machine learning, data analysis)
   - Certifications (if mentioned)

   DO NOT include programming languages, frameworks, tools, or cloud platforms.
   For anything related to Agile or Scrum, just list "Agile" or "Scrum" without elaboration.
   For each word, the first letter should be uppercase, and the rest of the letters in the word should be lowercase.
   If none are mentioned, return an empty array.

3. "seniority" must be one of:
   "Junior", "Mid-Level", "Senior", "Lead", "Principal", or "Unknown".

4. "summary" must be a concise 3 to 5 sentence summary of the role.

Return ONLY valid JSON. No explanations.
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

        # Parse and return JSON safely
        try:
            return json.loads(content)
        except Exception:
            print("LLM returned invalid JSON:", content)
            return None

    except Exception as e:
        print("Extractor error:", e)
        return None
