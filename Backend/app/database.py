from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
#import psycopg2
#from psycopg2.extras import RealDictCursor
#import time
from . config import settings

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 
"""while True:
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
        time.sleep(2)"""