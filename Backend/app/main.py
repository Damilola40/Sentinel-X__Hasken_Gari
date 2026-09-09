from fastapi import FastAPI

from app.routers import incidents_router

app = FastAPI()

app.include_router(incidents_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Hasken Gari API is running"
    }