from fastapi import FastAPI
from app.api.scrape import router as scrape_router

app = FastAPI()

app.include_router(scrape_router, prefix="/api")  #Register the scrape router with a prefix

@app.get("/health")
def health():
    return {"status": "ok"}
