def handle_symptoms(text):
    text = text.lower()

    if "fever" in text:
        return (
            "🌡️ *Fever – General Information*\n\n"
            "Possible causes include infections, dehydration, or inflammation.\n\n"
            "🏠 *General Care:*\n"
            "• Drink plenty of fluids\n"
            "• Take adequate rest\n"
            "• Monitor body temperature\n\n"
            "🚨 *See a doctor if:*\n"
            "• Fever lasts more than 2–3 days\n"
            "• Fever is very high\n"
            "• There are other severe symptoms\n"
        )

    if "headache" in text:
        return (
            "🤕 *Headache – General Information*\n\n"
            "Possible causes include stress, dehydration, lack of sleep, or eye strain.\n\n"
            "🏠 *General Care:*\n"
            "• Rest in a quiet, dark place\n"
            "• Stay hydrated\n"
            "• Reduce screen time\n\n"
            "🚨 *See a doctor if:*\n"
            "• Headache is severe or sudden\n"
            "• Vision problems occur\n"
        )

    if "cough" in text or "cold" in text:
        return (
            "🤧 *Cough / Cold – General Information*\n\n"
            "Often caused by viral infections or allergies.\n\n"
            "🏠 *General Care:*\n"
            "• Warm fluids\n"
            "• Adequate rest\n"
            "• Avoid cold air and smoke\n\n"
            "🚨 *See a doctor if:*\n"
            "• Symptoms persist beyond a week\n"
            "• Breathing difficulty occurs\n"
        )

    if "stomach" in text or "abdominal pain" in text:
        return (
            "🍽️ *Stomach Pain – General Information*\n\n"
            "Possible causes include indigestion, gas, or food-related issues.\n\n"
            "🏠 *General Care:*\n"
            "• Eat light food\n"
            "• Avoid spicy or oily food\n"
            "• Stay hydrated\n\n"
            "🚨 *See a doctor if:*\n"
            "• Pain is severe or persistent\n"
            "• Vomiting or fever occurs\n"
        )

    if "tired" in text or "fatigue" in text:
        return (
            "😴 *Fatigue – General Information*\n\n"
            "Possible causes include lack of sleep, stress, or poor nutrition.\n\n"
            "🏠 *General Care:*\n"
            "• Ensure proper sleep\n"
            "• Eat balanced meals\n"
            "• Reduce stress\n\n"
            "🚨 *See a doctor if:*\n"
            "• Fatigue lasts for weeks\n"
            "• Other symptoms appear\n"
        )

    return None
