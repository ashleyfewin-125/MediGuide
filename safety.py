EMERGENCY_KEYWORDS = [
    "chest pain", "breathing problem", "shortness of breath",
    "heart attack", "unconscious", "severe bleeding"
]

BLOCKED_KEYWORDS = [
    "dosage", "mg", "tablet", "medicine name", "prescribe",
    "antibiotic", "painkiller"
]

def is_emergency(text):
    return any(word in text for word in EMERGENCY_KEYWORDS)

def is_blocked(text):
    return any(word in text for word in BLOCKED_KEYWORDS)
