from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.utils.auth import create_session_token, is_authenticated, get_current_user
from app.models.queue import QueueItem
import json
from datetime import datetime
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Path to queue.json
QUEUE_FILE = Path("app/data/queue.json")

def load_queue_data():
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, "r") as f:
        return json.load(f)

def save_queue_data(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, default=str)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    # Simple hardcoded admin check
    if username == "admin" and password == "admin":
        response = RedirectResponse(url="/", status_code=303)
        token = create_session_token(username)
        response.set_cookie(key="session", value=token, httponly=True)
        return response
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"},
        status_code=401
    )

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("session")
    return response

@router.get("/appointments/urgent", response_class=HTMLResponse)
async def urgent_cases(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    
    queue_data = load_queue_data()
    # Convert string timestamps to datetime objects
    for item in queue_data:
        item["timestamp"] = datetime.fromisoformat(item["timestamp"])
        if "process_time" in item and item["process_time"]:
            item["process_time"] = datetime.fromisoformat(item["process_time"])
    
    return templates.TemplateResponse(
        "urgent.html", 
        {"request": request, "queue_items": queue_data}
    )

@router.post("/appointments/urgent/{item_id}/{action}")
async def handle_urgent_action(item_id: str, action: str):
    if action not in ["approve", "reject"]:
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid action"}
        )
    
    queue_data = load_queue_data()
    item = next((item for item in queue_data if item["id"] == item_id), None)
    
    if not item:
        return JSONResponse(
            status_code=404,
            content={"message": "Item not found"}
        )
    
    # Update item status and add process time
    status_map = {
        "approve": "approved",
        "reject": "rejected"
    }
    item["status"] = status_map[action]
    item["process_time"] = datetime.now().isoformat()
    save_queue_data(queue_data)
    
    return JSONResponse(
        status_code=200,
        content={"message": f"Item {action}d successfully"}
    )

@router.get("/appointments/list", response_class=HTMLResponse)
async def appointments_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("appointments.html", {"request": request}) 