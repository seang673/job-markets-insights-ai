from fastapi import FastAPI
from app.api.scrape import router as scrape_router
from app.api.similar import router as similar_router
from app.routes import jobs

app = FastAPI()

app.include_router(scrape_router, prefix="/api")  #Register the scrape router with a prefix
app.include_router(similar_router, prefix="/api")  #Register the similar router with a prefix

app.include_router(jobs.router)

@app.get("/health")
def health():
    return {"status": "ok"}


