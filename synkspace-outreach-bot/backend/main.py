"""
SynkSpace Outreach Bot — FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import close_db, connect_db
from routes import campaigns, creators, emails


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection lifecycle."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="SynkSpace Outreach Bot",
    description="AI-powered creator outreach automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(creators.router)
app.include_router(campaigns.router)
app.include_router(emails.router)


@app.get("/")
async def root():
    return "SynkSpace Outreach Bot Running 🚀"


@app.get("/health")
async def health():
    return {"status": "healthy"}
