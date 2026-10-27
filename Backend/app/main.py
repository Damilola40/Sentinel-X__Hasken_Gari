from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import incidents_router, auth_router, users_router, dashboard_router, notification_router, sms_router
from app.database import Base, engine

# Base.metadata.create_all(bind=engine)
# no longer needed as alembic has been setup

app = FastAPI()

origins = ["*"]
# later streamline this just for your frontend domains

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")
app.include_router(sms_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "Hasken Gari API is running"
    }

