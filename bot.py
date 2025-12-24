from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

from config import BOT_TOKEN, OLLAMA_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT
from safety import is_emergency, is_blocked
from symptoms import handle_symptoms

# ---------- BUTTON KEYBOARD ----------
keyboard = ReplyKeyboardMarkup(
    [
        ["🩺 Describe Symptoms"],
        ["🏠 Home Care Tips", "🚨 When to See a Doctor"],
        ["🏥 Find Doctor / Hospital"],
        ["ℹ️ Disclaimer"]
    ],
    resize_keyboard=True
)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *MediGuide Bot*\n\n"
        "I provide *general medical information only*.\n"
        "❌ No diagnosis\n"
        "❌ No prescriptions\n\n"
        "Choose an option below or describe your symptoms.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ---------- MESSAGE HANDLER ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # ---------- MEMORY ----------
    history = context.user_data.get("history", [])
    history.append(text)
    context.user_data["history"] = history[-5:]

    # ---------- CITY HANDLER ----------
    if context.user_data.get("awaiting_city"):
        city = update.message.text.strip()
        context.user_data["awaiting_city"] = False

        maps_link = f"https://www.google.com/maps/search/hospitals+near+{city.replace(' ', '+')}"

        await update.message.reply_text(
            f"🏥 *Hospitals & Doctors near {city}*\n\n"
            f"{maps_link}\n\n"
            "Please verify ratings and consult qualified professionals.",
            parse_mode="Markdown"
        )
        return

    # ---------- FIND DOCTOR ----------
    if "find doctor" in text or "hospital" in text:
        await update.message.reply_text(
            "🏥 Please tell me your *city name*.\n\n"
            "Example:\n"
            "• Chennai\n"
            "• Bangalore\n"
            "• Coimbatore",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_city"] = True
        return

    # ---------- DISCLAIMER ----------
    if "disclaimer" in text:
        await update.message.reply_text(
            "ℹ️ *Medical Disclaimer*\n\n"
            "This bot provides educational health information only.\n"
            "It does NOT diagnose diseases or prescribe medicines.\n"
            "Always consult a qualified medical professional.",
            parse_mode="Markdown"
        )
        return

    # ---------- DESCRIBE SYMPTOMS ----------
    if "describe symptoms" in text:
        await update.message.reply_text(
            "🩺 Please describe your symptoms clearly.\n\n"
            "Example:\n"
            "- I have headache and fever\n"
            "- I feel tired all day"
        )
        return

    # ---------- HOME CARE ----------
    if "home care" in text:
        await update.message.reply_text(
            "🏠 *General Home Care Tips*\n\n"
            "• Drink enough water\n"
            "• Get adequate rest\n"
            "• Eat balanced food\n"
            "• Avoid self-medication",
            parse_mode="Markdown"
        )
        return

    # ---------- WHEN TO SEE DOCTOR ----------
    if "when to see a doctor" in text:
        await update.message.reply_text(
            "🚨 *Consult a Doctor Immediately If:*\n\n"
            "• Symptoms are severe or worsening\n"
            "• Fever lasts more than 2–3 days\n"
            "• Chest pain or breathing difficulty occurs",
            parse_mode="Markdown"
        )
        return

    # ---------- SAFETY ----------
    if is_emergency(text):
        await update.message.reply_text(
            "🚨 This may be a medical emergency.\n"
            "Please go to the nearest hospital immediately."
        )
        return

    if is_blocked(text):
        await update.message.reply_text(
            "❌ I cannot provide medicine names or dosages.\n"
            "Please consult a doctor."
        )
        return

    # ---------- RULE-BASED SYMPTOMS ----------
    symptom_reply = handle_symptoms(text)
    if symptom_reply:
        await update.message.reply_text(symptom_reply)
        return

    # ---------- AI FALLBACK (STRICT FORMAT) ----------
    prompt = (
        SYSTEM_PROMPT +
        "\nConversation so far:\n" +
        "\n".join(context.user_data["history"]) +
        "\nUser health concern:\n" + text +
        "\nRespond strictly using the required format."
    )

    response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "max_tokens": 90
        }
    }
)


    reply = response.json()["response"]
    await update.message.reply_text(reply)

# ---------- RUN ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 MediGuide Bot is running...")
app.run_polling()
