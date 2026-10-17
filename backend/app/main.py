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

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
