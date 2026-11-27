from fastapi import FastAPI
from src.api.routers import dashboard, sla, backlog, teams
from src.api.routers import dashboard, sla, backlog, teams, clients
from src.api.routers import dashboard, sla, backlog, teams, clients, services, analytics
app = FastAPI(
    title="PulseOps API",
    description="IT Service Intelligence & Early-Warning Platform",
    version="0.1.0",
)

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
