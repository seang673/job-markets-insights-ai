from fastapi import FastAPI
from app.api.scrape import router as scrape_router
from app.api.similar import router as similar_router
from app.api.insights import router as insights_router
from fastapi.middleware.cors import CORSMiddleware
from app.routes import jobs
from dotenv import load_dotenv

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()

app.include_router(scrape_router, prefix="/api")  #Register the scrape router with a prefix
app.include_router(similar_router, prefix="/api")  #Register the similar router with a prefix

app.include_router(jobs.router)
app.include_router(insights_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}


