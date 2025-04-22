from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routes import web, health, triage, api
import os

app = FastAPI()

# Add session middleware with a secret key
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Include routers
app.include_router(api.router, prefix="/api")
app.include_router(web.router)
app.include_router(health.router, prefix="/health")
app.include_router(triage.router, prefix="/triage")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
