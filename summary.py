def generate_summary(history):
    keywords = set()

    common_terms = [
        "fever", "headache", "cough", "pain",
        "fatigue", "dizziness", "stomach"
    ]

    for msg in history:
        for term in common_terms:
            if term in msg:
                keywords.add(term.capitalize())

    if not keywords:
        return None

    summary = "🧾 *Symptom Summary:*\n"
    for k in keywords:
        summary += f"• {k}\n"

    summary += "\nNext step: Consult a doctor if symptoms persist."

    return summary
