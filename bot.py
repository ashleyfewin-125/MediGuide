from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

from config import BOT_TOKEN, OLLAMA_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT
from safety import is_emergency, is_blocked
from symptoms import handle_symptoms
from summary import generate_summary

# ================== SEVERITY FORMATTER ==================

def format_severity(context):
    severity = context.user_data.get("triage_severity", "")

    if "mild" in severity:
        return "🟢 *Severity: Mild*\n_Mostly manageable with home care_"

    if "moderate" in severity:
        return "🟡 *Severity: Moderate*\n_Consult a doctor if it persists_"

    if "severe" in severity:
        return "🔴 *Severity: Severe*\n_Seek medical attention urgently_"

    return "⚪ *Severity: General Guidance*"

# ================== KEYBOARDS ==================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🩺 Describe Symptoms"],
        ["🏠 Home Care Tips", "🚨 When to See a Doctor"],
        ["🏥 Find Doctor / Hospital"],
        ["ℹ️ Disclaimer"]
    ],
    resize_keyboard=True
)

followup_keyboard = ReplyKeyboardMarkup(
    [
        ["🧾 Show Summary", "🏥 Find Hospital"],
        ["🔄 New Symptom"]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

triage_severity_keyboard = ReplyKeyboardMarkup(
    [["🟢 Mild", "🟡 Moderate", "🔴 Severe"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

triage_duration_keyboard = ReplyKeyboardMarkup(
    [["< 24 hours", "1–3 days", "> 3 days"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ================== START ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["history"] = []
    context.user_data["triage_stage"] = None

    await update.message.reply_text(
        "👋 Welcome to *MediGuide Bot*\n\n"
        "I provide *general medical information only*.\n"
        "❌ No diagnosis\n"
        "❌ No prescriptions\n\n"
        "Please describe your symptom.",
        reply_markup=main_keyboard,
        parse_mode="Markdown"
    )

# ================== MESSAGE HANDLER ==================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # ---------- UI BUTTONS ----------
    if "describe symptoms" in text:
        await update.message.reply_text(
            "🩺 Please describe your symptoms.\n\n"
            "Examples:\n• elbow pain\n• headache and fever"
        )
        return

    if "home care" in text:
        await update.message.reply_text(
            "🏠 *General Home Care Tips*\n"
            "• Drink enough water\n"
            "• Take adequate rest\n"
            "• Avoid self-medication",
            parse_mode="Markdown"
        )
        return

    if "when to see a doctor" in text:
        await update.message.reply_text(
            "🚨 *Consult a doctor if:*\n"
            "• Symptoms worsen\n"
            "• Pain persists\n"
            "• New symptoms appear",
            parse_mode="Markdown"
        )
        return

    if "disclaimer" in text:
        await update.message.reply_text(
            "ℹ️ Educational purpose only.\nAlways consult a qualified doctor."
        )
        return

    if "new symptom" in text:
        context.user_data.clear()
        context.user_data["history"] = []
        context.user_data["triage_stage"] = None
        await update.message.reply_text(
            "🔄 Previous case cleared.\nPlease describe your new symptom.",
            reply_markup=main_keyboard
        )
        return

    if "show summary" in text:
        summary = generate_summary(context.user_data.get("history", []))
        await update.message.reply_text(summary or "🧾 No symptoms recorded yet.")
        return

    # ---------- MEMORY ----------
    context.user_data.setdefault("history", []).append(text)
    context.user_data["history"] = context.user_data["history"][-5:]

    # ---------- SAFETY ----------
    if is_emergency(text):
        await update.message.reply_text(
            "🚨 This may be a medical emergency.\nPlease go to the nearest hospital immediately."
        )
        return

    if is_blocked(text):
        await update.message.reply_text(
            "❌ I cannot provide medicine names or dosages.\nPlease consult a doctor."
        )
        return

    # ---------- TRIAGE ----------
    symptom_keywords = ["pain", "fever", "headache", "cough", "dizziness", "fatigue"]

    if context.user_data.get("triage_stage") is None:
        if any(word in text for word in symptom_keywords):
            context.user_data["triage_stage"] = "severity"
            context.user_data["triage_symptom"] = text
            await update.message.reply_text(
                "❓ How severe is the symptom?",
                reply_markup=triage_severity_keyboard
            )
            return

    if context.user_data.get("triage_stage") == "severity":
        if "mild" in text or "moderate" in text or "severe" in text:
            context.user_data["triage_severity"] = text
            context.user_data["triage_stage"] = "duration"
            await update.message.reply_text(
                "❓ How long has this been present?",
                reply_markup=triage_duration_keyboard
            )
            return

    if context.user_data.get("triage_stage") == "duration":
        context.user_data["triage_stage"] = None
        text = context.user_data["triage_symptom"]

    # ---------- RESPONSE ----------
    severity = format_severity(context)

    symptom_reply = handle_symptoms(text)
    if symptom_reply:
        await update.message.reply_text(
            severity + "\n\n" + symptom_reply,
            reply_markup=followup_keyboard,
            parse_mode="Markdown"
        )
        return

    # ---------- OLLAMA AI ----------
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": SYSTEM_PROMPT + "\nUser: " + text,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 120
                }
            },
            timeout=60
        )
        reply = response.json().get("response", "").strip()

    except Exception as e:
        print("Ollama error:", e)
        reply = (
            "ℹ️ General Health Information\n\n"
            "This appears to be a non-emergency concern.\n"
            "Please monitor your symptoms and consult a doctor if they persist.\n\n"
            "⚠️ Educational purpose only."
        )

    await update.message.reply_text(
        severity + "\n\n" + reply,
        reply_markup=followup_keyboard,
        parse_mode="Markdown"
    )

# ================== RUN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 MediGuide Bot (Ollama Local) is running...")
app.run_polling()
