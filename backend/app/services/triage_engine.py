def determine_triage(patient):
    if not patient.symptoms or len(patient.symptoms) == 0:
        return "ambiguous"

    urgent_keywords = {"chest pain", "difficulty breathing", "unconscious"}
    lower_symptoms = {s.lower() for s in patient.symptoms}

    if lower_symptoms & urgent_keywords:
        return "urgent"

    if "fever" in lower_symptoms and patient.age >= 65:
        return "urgent"

    if "headache" in lower_symptoms and len(lower_symptoms) == 1:
        return "routine"

    return "routine"
