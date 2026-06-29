import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

load_dotenv()

# Connection string is read from the environment (backend/.env, gitignored) so
# credentials never live in source. Example:
#   DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/job_insights
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to backend/.env, e.g.\n"
        "DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/job_insights"
    )

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