from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    dashboard,
    sla,
    backlog,
    teams,
    clients,
    services,
    analytics,
)

app = FastAPI(
    title="PulseOps API",
    description="IT Service Intelligence & Early-Warning Platform",
    version="0.1.0",
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(dashboard.router)
app.include_router(sla.router)
app.include_router(backlog.router)
app.include_router(teams.router)
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "project": "PulseOps",
        "message": "PulseOps API is running!",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "PulseOps API",
    }