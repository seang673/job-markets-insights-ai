from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter

from app.db.database import async_get_db
from app.db import models
router = APIRouter()

# Factors to convert a salary quoted in a given period into an annual figure.
_PERIOD_FACTORS = {"YEAR": 1, "MONTH": 12, "WEEK": 52, "DAY": 260, "HOUR": 2080}

# Sanity bounds (annual USD) to drop obviously-bad parses, e.g. an hourly rate
# mislabeled as yearly, or a stray "0".
_MIN_ANNUAL = 1_000
_MAX_ANNUAL = 2_000_000


def _annualized_usd_midpoint(job):
    """Return one annualized USD salary point for a job, or None if unusable.

    Uses the midpoint of the advertised min/max range, normalized to a yearly
    figure. Non-USD postings are skipped (missing currency is treated as USD)
    so the distribution stays on one scale.
    """
    currency = (job.salary_currency or "USD").strip().upper()
    if currency != "USD":
        return None

    values = [v for v in (job.job_min_salary, job.job_max_salary) if v]
    if not values:
        return None
    midpoint = sum(values) / len(values)

    period = (job.salary_period or "YEAR").strip().upper()
    annual = midpoint * _PERIOD_FACTORS.get(period, 1)

    if not (_MIN_ANNUAL < annual < _MAX_ANNUAL):
        return None
    return round(annual, 2)

@router.get("/insights/overview")
async def get_insights_overview(
    role: Optional[str] = None,
    seniority: Optional[str] = None,
    db: AsyncSession = Depends(async_get_db),
):
    # Build base query. Both filters are optional and compose: omitting `role`
    # aggregates across roles, omitting `seniority` aggregates across levels.
    query = select(models.JobPosting)

    if role:
        query = query.where(models.JobPosting.role == role)

    if seniority:
        query = query.where(models.JobPosting.seniority == seniority)

    # Execute async query
    result = await db.execute(query)
    jobs = result.scalars().all()

    total_jobs = len(jobs)

    skill_counter = Counter()
    tech_counter = Counter()
    seniority_counter = Counter()

    # Box-plot grouping is adaptive: when a single role is in view, compare
    # salaries across seniority levels; otherwise compare across roles.
    group_by = "seniority" if role else "role"
    salary_data = []

    for job in jobs:
        if job.skills_extracted:
            skills = [s.strip() for s in job.skills_extracted.split(',') if s.strip()]
            skill_counter.update(skills)

        if job.tech_stack:
            techs = [t.strip() for t in job.tech_stack.split(',') if t.strip()]
            tech_counter.update(techs)

        if job.seniority:
            seniority_counter.update([job.seniority.strip()])

        annual = _annualized_usd_midpoint(job)
        if annual is not None:
            group = (getattr(job, group_by) or "").strip() or "Unknown"
            salary_data.append({"group": group, "salary": annual})

    top_skills = [
        {"name": name, "count": count}
        for name, count in skill_counter.most_common(10)
    ]

    top_tech_stack = [
        {"name": name, "count": count}
        for name, count in tech_counter.most_common(10)
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
        "salary_data": salary_data,
        "salary_group_by": group_by,
        "role": role or "all",
        "seniority": seniority or "all",
    }