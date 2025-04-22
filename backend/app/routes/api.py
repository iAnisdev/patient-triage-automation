from fastapi import APIRouter
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()

# File paths
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/app → backend
DATA_DIR = BASE_DIR / "data"

QUEUE_FILE = DATA_DIR / "queue.json"
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"
DOCTORS_FILE = DATA_DIR / "doctors.json"
PATIENTS_FILE = DATA_DIR / "patients.json"


def load_json_data(file_path: Path):
    if not file_path.exists():
        return []
    with open(file_path, "r") as f:
        return json.load(f)

@router.get("/stats")
async def get_stats():
    # Load queue data for urgent cases
    queue_data = load_json_data(QUEUE_FILE)
    urgent_pending = len([item for item in queue_data if item["status"] == "pending"])
    
    # Load appointments data
    appointments = load_json_data(APPOINTMENTS_FILE)
    total_appointments = len(appointments)
    completed_appointments = len([apt for apt in appointments if apt["status"] == "completed"])
    scheduled_appointments = len([apt for apt in appointments if apt["status"] == "scheduled"])
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    today_appointments = len([apt for apt in appointments if apt["date"] == today])
    
    # Get appointments scheduled for today (created today)
    today_created = datetime.now().strftime("%Y-%m-%d")
    scheduled_today = len([apt for apt in appointments 
                          if apt["created_at"].startswith(today_created) 
                          and apt["status"] == "scheduled"])
    
    # Load doctors and patients data
    doctors = load_json_data(DOCTORS_FILE)
    patients = load_json_data(PATIENTS_FILE)
    
    return {
        "urgent_pending": urgent_pending,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "scheduled_appointments": scheduled_appointments,
        "today_appointments": today_appointments,
        "scheduled_today": scheduled_today,
        "total_doctors": len(doctors),
        "total_patients": len(patients)
    }

# API routes will be added here 