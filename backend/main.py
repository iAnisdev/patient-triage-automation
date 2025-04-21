from fastapi import FastAPI
from app.routes import triage, health

app = FastAPI()

app.include_router(health.router, prefix="/health")
app.include_router(triage.router, prefix="/triage")
