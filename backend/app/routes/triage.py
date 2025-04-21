from fastapi import APIRouter
from app.models.patient import PatientRequest
from app.services.triage_engine import determine_triage

router = APIRouter()

@router.post("/")
def triage_patient(payload: PatientRequest):
    result = determine_triage(payload)
    return {"urgency": result}
