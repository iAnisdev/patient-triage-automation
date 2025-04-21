def determine_triage(patient):
    urgent_symptoms = {"chest pain", "difficulty breathing", "unconscious"}
    if any(symptom.lower() in urgent_symptoms for symptom in patient.symptoms):
        return "urgent"
    return "routine"
