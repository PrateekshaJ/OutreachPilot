"""
FastAPI entry point for SynkSpace Outreach Bot backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import campaigns, creators, emails


app = FastAPI(
    title="SynkSpace Outreach Bot",
    description="AI-powered creator outreach and campaign automation backend",
    version="1.0.0",
)


# CORS setup for React frontend
origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(creators.router)
app.include_router(campaigns.router)
app.include_router(emails.router)


@app.get("/")
async def root():
    return {
        "message": "SynkSpace Outreach Bot API running 🚀"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": settings.mongodb_db,
    }