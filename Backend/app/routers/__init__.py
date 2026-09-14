"""Expose the API routers for registration in the FastAPI application."""

# Import the router instances so callers can register every route from this package.
from app.routers.incidents import incidents_router

from app.routers.auth import auth_router

from app.routers.users import users_router
