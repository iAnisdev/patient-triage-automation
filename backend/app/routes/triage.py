from fastapi import APIRouter, Request
from app.models.patient import PatientRequest
from app.models.dialogflow import DialogflowWebhookRequest
from app.services.triage_engine import determine_triage

router = APIRouter()

@router.post("/")
def triage_patient(payload: PatientRequest):
    result = determine_triage(payload)
    return {"urgency": result}


@router.post("/webhook")
async def triage_webhook(payload: DialogflowWebhookRequest):
    params = payload.queryResult.parameters

    name = params.get("name", "Anonymous")
    age = int(params.get("age", 30))
    symptoms = params.get("symptoms", [])

    patient = PatientRequest(name=name, age=age, symptoms=symptoms)
    result = determine_triage(patient)

    return {
        "fulfillmentText": f"Triage complete. Case is marked as {result}."
    }
