from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes_auth import router as auth_router

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
    allow_origins=["*"],  # Adjust for production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ACM NITK Membership Management System API",
        "documentation": "/docs",
    }
