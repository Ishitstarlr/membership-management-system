from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes_auth import router as auth_router
from .routes_members import router as members_router
from .routes_teams import router as teams_router
from .routes_stats import router as stats_router

# Create all tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ACM NITK Membership Management System",
    description="Backend API for managing club members, teams, and analytics.",
    version="1.0.0",
)

import os
cors_origins_env = os.getenv("CORS_ORIGINS")
cors_origins = (
    [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    if cors_origins_env
    else [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(auth_router)
app.include_router(members_router)
app.include_router(teams_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ACM NITK Membership Management System API",
        "documentation": "/docs",
    }
