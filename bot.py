import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8639768132:AAHo--8SGRle1sAZteABY6tCfXVA6SMYiK0"
ADMIN_ID = 6609131999

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Generate Script", callback_data="script")],
        [InlineKeyboardButton("💰 Buy Premium", callback_data="buy")],
        [InlineKeyboardButton("📊 Check Status", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 Welcome to AI Bot\n\nChoose an option:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    users = load_users()

    if user_id not in users:
        users[user_id] = {"used_free": False, "paid": False, "expiry": 0}

    user = users[user_id]

    if user["paid"] and time.time() > user["expiry"]:
        user["paid"] = False

    if query.data == "script":
        if not user["used_free"]:
            user["used_free"] = True
            save_users(users)
            await query.message.reply_text("Send topic like: motivation")
        elif not user["paid"]:
            await query.message.reply_text("❌ Free trial over!\nBuy premium ₹99/week")
        else:
            await query.message.reply_text("Send topic:")

    elif query.data == "buy":
        await query.message.reply_text(
            "💰 Pay ₹99/week\nUPI: yourupi@upi\n\nSend UTR after payment"
        )

    elif query.data == "status":
        if user["paid"]:
            days = int((user["expiry"] - time.time()) / 86400)
            await query.message.reply_text(f"✅ Premium Active\nDays left: {days}")
        else:
            await query.message.reply_text("❌ No active plan")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.message.from_user.id)

    user = users.get(user_id)

    if user["paid"] and time.time() > user["expiry"]:
        user["paid"] = False

    if not user["used_free"]:
        user["used_free"] = True
    elif not user["paid"]:
        await update.message.reply_text("❌ Pay ₹99/week to continue")
        return

    topic = update.message.text

    script = f"🔥 Viral Script on {topic}\n\nHook: This will shock you!\nMain: {topic} is powerful!\nCTA: Follow for more!"
    await update.message.reply_text(script)

    save_users(users)

async def handle_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text.upper().startswith("UTR"):
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"User: {user_id}\nUTR: {text}"
        )
        await update.message.reply_text("⏳ Waiting for approval")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    user_id = context.args[0]
    users = load_users()

    users[user_id]["paid"] = True
    users[user_id]["expiry"] = time.time() + (7 * 24 * 60 * 60)

    save_users(users)

    await context.bot.send_message(
        chat_id=int(user_id),
        text="✅ Premium Activated for 7 days"
    )

    await update.message.reply_text("Approved!")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^UTR"), handle_utr))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CommandHandler("approve", approve))

app.run_polling()
