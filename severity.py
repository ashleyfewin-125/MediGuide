def get_severity(text):
    text = text.lower()

    red_flags = [
        "chest pain", "hard","bad","breathing", "unconscious",
        "severe", "sudden", "worst", "numbness"
    ]

    moderate_flags = [
        "pain", "fever", "headache", "dizzy",
        "vomiting", "swelling"
    ]

    if any(word in text for word in red_flags):
        return "🔴 Severity: Seek medical care urgently"

    if any(word in text for word in moderate_flags):
        return "🟡 Severity: Monitor and consult a doctor if it persists"

    return "🟢 Severity: Mild"
