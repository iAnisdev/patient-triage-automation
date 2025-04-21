from fastapi import APIRouter, Request, HTTPException, Depends, Form, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.utils.auth import create_session_token, is_authenticated, get_current_user
from app.models.queue import QueueItem
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import random
from pydantic import BaseModel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# File paths
QUEUE_FILE = Path("app/data/queue.json")
APPOINTMENTS_FILE = Path("app/data/appointments.json")
PATIENTS_FILE = Path("app/data/patients.json")
DOCTORS_FILE = Path("app/data/doctors.json")

# Add time slots (every 30 minutes from 9 AM to 5 PM)
TIME_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30"
]

def load_queue_data():
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, "r") as f:
        return json.load(f)

def save_queue_data(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, default=str)

def load_json_data(file_path: str):
    path = Path(file_path)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_json_data(file_path: str, data):
    path = Path(file_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

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

class AppointmentSchedule(BaseModel):
    queue_item_id: str
    doctor_id: str
    date: str
    time: str

@router.get("/appointments/urgent", response_class=HTMLResponse)
async def urgent_cases(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    
    queue_data = load_queue_data()
    doctors = load_json_data(DOCTORS_FILE)
    
    # Convert string timestamps to datetime objects
    for item in queue_data:
        item["timestamp"] = datetime.fromisoformat(item["timestamp"])
        if "process_time" in item and item["process_time"]:
            item["process_time"] = datetime.fromisoformat(item["process_time"])
    
    return templates.TemplateResponse(
        "urgent.html",
        {
            "request": request,
            "queue_items": queue_data,
            "doctors": doctors,
            "time_slots": TIME_SLOTS
        }
    )

@router.post("/appointments/urgent/approve")
async def approve_urgent_case(schedule: AppointmentSchedule = Body(...)):
    # Load queue data
    queue_data = load_queue_data()
    queue_item = next((item for item in queue_data if item["id"] == schedule.queue_item_id), None)
    
    if not queue_item:
        return JSONResponse(
            status_code=404,
            content={"message": "Queue item not found"}
        )
    
    # Update queue item
    queue_item["status"] = "approved"
    queue_item["process_time"] = datetime.now().isoformat()
    save_queue_data(queue_data)
    
    # Create appointment
    appointment_data = {
        "id": str(len(load_json_data(APPOINTMENTS_FILE)) + 1),
        "patient_id": str(len(load_json_data(PATIENTS_FILE)) + 1),
        "doctor_id": schedule.doctor_id,
        "date": schedule.date,
        "time": schedule.time,
        "status": "scheduled",
        "symptoms": queue_item["symptoms"],
        "created_at": datetime.now().isoformat()
    }
    
    # Save appointment
    appointments = load_json_data(APPOINTMENTS_FILE)
    appointments.append(appointment_data)
    save_json_data(APPOINTMENTS_FILE, appointments)
    
    # Create patient record
    patient_data = {
        "id": appointment_data["patient_id"],
        "name": queue_item["patient_name"],
        "age": queue_item["age"]
    }
    
    # Save patient
    patients = load_json_data(PATIENTS_FILE)
    patients.append(patient_data)
    save_json_data(PATIENTS_FILE, patients)
    
    return JSONResponse(
        status_code=200,
        content={"message": "Appointment scheduled successfully"}
    )

@router.get("/appointments/list")
async def appointments_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    
    # Load all data
    appointments = load_json_data(APPOINTMENTS_FILE)
    patients = load_json_data(PATIENTS_FILE)
    doctors = load_json_data(DOCTORS_FILE)
    
    # Create lookup dictionaries
    patients_lookup = {str(p["id"]): p["name"] for p in patients}
    doctors_lookup = {str(d["id"]): d["name"] for d in doctors}
    
    # Get unique symptoms from all appointments
    all_symptoms = set()
    for appointment in appointments:
        all_symptoms.update(appointment["symptoms"])
    unique_symptoms = sorted(list(all_symptoms))
    
    # Combine appointment data with patient and doctor names
    combined_appointments = []
    for appointment in appointments:
        combined = appointment.copy()
        combined["patient_name"] = patients_lookup.get(str(appointment["patient_id"]), "Unknown")
        combined["doctor_name"] = doctors_lookup.get(str(appointment["doctor_id"]), "Unknown")
        combined_appointments.append(combined)
    
    # Sort appointments by date and time
    combined_appointments.sort(key=lambda x: (x["date"], x["time"]))
    
    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "appointments": combined_appointments,
            "patients": patients,
            "doctors": doctors,
            "symptoms": unique_symptoms
        }
    )

@router.get("/booking")
async def booking_form(request: Request, prefilled_data: Optional[dict] = None):
    return templates.TemplateResponse(
        "booking.html",
        {
            "request": request,
            "hide_topbar": True,
            "prefilled_data": prefilled_data
        }
    )

URGENT_SYMPTOMS = {
    'chest pain',
    'shortness of breath',
    'unconscious',
    'severe bleeding',
    'difficulty breathing',
    'severe pain',
    'stroke symptoms',
    'heart attack symptoms'
}

def get_next_available_date():
    # Get today's date
    today = datetime.now().date()
    # Skip weekends
    while today.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
        today += timedelta(days=1)
    return today

@router.post("/booking")
async def submit_booking(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    symptoms: str = Form(...),
    is_rejected: bool = Form(False)  # New parameter to identify rejected cases
):
    # Process symptoms - split by comma and clean up
    symptoms_list = [s.strip().lower() for s in symptoms.split(',') if s.strip()]
    
    # For rejected cases, treat as non-urgent regardless of symptoms
    if is_rejected:
        has_urgent_symptoms = False
    else:
        # Check for urgent symptoms
        has_urgent_symptoms = any(symptom in URGENT_SYMPTOMS for symptom in symptoms_list)
    
    if has_urgent_symptoms:
        # Load existing queue data
        queue_data = load_queue_data()
        
        # Create queue item
        queue_item = {
            "id": str(len(queue_data) + 1),
            "patient_name": name,
            "age": age,
            "symptoms": symptoms_list,
            "urgency": "high",
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Add to queue
        queue_data.append(queue_item)
        save_queue_data(queue_data)
        
        return templates.TemplateResponse(
            "thanks.html",
            {
                "request": request,
                "hide_topbar": True,
                "message": "Urgent case received. Please wait for immediate assistance."
            }
        )
    else:
        # Load doctors data
        doctors = load_json_data(DOCTORS_FILE)
        if not doctors:
            return templates.TemplateResponse(
                "thanks.html",
                {
                    "request": request,
                    "hide_topbar": True,
                    "message": "Error: No doctors available. Please try again later."
                }
            )
        
        # Randomly select a doctor and time slot
        selected_doctor = random.choice(doctors)
        appointment_date = get_next_available_date()
        time_slot = random.choice(TIME_SLOTS)
        
        # Create appointment
        appointment_data = {
            "id": str(len(load_json_data(APPOINTMENTS_FILE)) + 1),
            "patient_id": str(len(load_json_data(PATIENTS_FILE)) + 1),
            "doctor_id": selected_doctor["id"],
            "date": appointment_date.strftime("%Y-%m-%d"),
            "time": time_slot,
            "status": "scheduled",
            "symptoms": symptoms_list,
            "created_at": datetime.now().isoformat()
        }
        
        # Save appointment
        appointments = load_json_data(APPOINTMENTS_FILE)
        appointments.append(appointment_data)
        save_json_data(APPOINTMENTS_FILE, appointments)
        
        # Create patient record
        patient_data = {
            "id": appointment_data["patient_id"],
            "name": name,
            "age": age
        }
        
        # Save patient
        patients = load_json_data(PATIENTS_FILE)
        patients.append(patient_data)
        save_json_data(PATIENTS_FILE, patients)
        
        message = f"Appointment scheduled with Dr. {selected_doctor['name']} on {appointment_date.strftime('%A, %B %d')} at {time_slot}"
        
        return templates.TemplateResponse(
            "thanks.html",
            {
                "request": request,
                "hide_topbar": True,
                "message": message
            }
        )

@router.get("/thanks")
async def thank_you(request: Request):
    return templates.TemplateResponse("thanks.html", {
        "request": request,
        "hide_topbar": True
    }) 