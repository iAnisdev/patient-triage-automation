from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()

# File paths
QUEUE_FILE = Path("app/data/queue.json")
APPOINTMENTS_FILE = Path("app/data/appointments.json")

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
    
    return {
        "urgent_pending": urgent_pending,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "scheduled_appointments": scheduled_appointments
    }

# API routes will be added here 