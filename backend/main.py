from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import triage, health, web

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(web.router)
app.include_router(health.router, prefix="/health")
app.include_router(triage.router, prefix="/triage")
