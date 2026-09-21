from fastapi import APIRouter, HTTPException, status, Response, Depends

# Put all incident routes under the same URL and API tag.
dashboard_router = APIRouter(
    prefix = "/dashboard",
    tags = ["Dashboard"]
)