from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter

from app.db.database import async_get_db
from app.db import models
router = APIRouter()

@router.get("/insights/overview")
async def get_insights_overview(
    role: Optional[str] = None,
    db: AsyncSession = Depends(async_get_db)
):
    # Build base query
    query = select(models.JobPosting)

    if role:
        query = query.where(models.JobPosting.role == role)

    # Execute async query
    result = await db.execute(query)
    jobs = result.scalars().all()

    total_jobs = len(jobs)

    skill_counter = Counter()
    tech_counter = Counter()
    seniority_counter = Counter()

    for job in jobs:
        if job.skills_extracted:
            skills = [s.strip() for s in job.skills_extracted.split(',') if s.strip()]
            skill_counter.update(skills)

        if job.tech_stack:
            techs = [t.strip() for t in job.tech_stack.split(',') if t.strip()]
            tech_counter.update(techs)

        if job.seniority:
            seniority_counter.update([job.seniority.strip()])

    top_skills = [
        {"name": name, "count": count}
        for name, count in skill_counter.most_common(20)
    ]

    top_tech_stack = [
        {"name": name, "count": count}
        for name, count in tech_counter.most_common(20)
    ]

    seniority_distribution = [
        {"level": level, "count": count}
        for level, count in seniority_counter.most_common()
    ]

    return {
        "total_jobs": total_jobs,
        "top_skills": top_skills,
        "top_tech_stack": top_tech_stack,
        "seniority_distribution": seniority_distribution,
        "role": role or "all"
    }