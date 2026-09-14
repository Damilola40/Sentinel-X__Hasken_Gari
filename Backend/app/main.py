from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from app.routers import incidents_router, auth_router, users_router
import time
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(incidents_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

while True:
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="hasken_gari",
            user="postgres",
            password="mehmet123",
            cursor_factory=RealDictCursor
        )
        cursor = connection.cursor()
        print(f"Successfully connected to PostgreSQL database.")
        break
    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")
        time.sleep(2)

@app.get("/")
def root():
    return {
        "message": "Hasken Gari API is running"
    }