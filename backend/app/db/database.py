from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from backend.app.api.scrape import AsyncSession

DATABASE_URL = "postgresql+psycopg2://postgres:CrazySMG19%21@localhost:5432/job_insights"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def async_get_db():
    async with async_session() as session:
            yield session