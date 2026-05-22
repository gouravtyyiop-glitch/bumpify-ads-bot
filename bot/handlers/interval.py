from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit


async def set_interval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    current = await db.get_interval(user_id)
    mins, secs = divmod(current, 60)
    current_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1 min", callback_data="interval_60"),
            InlineKeyboardButton("3 min", callback_data="interval_180"),
            InlineKeyboardButton("5 min", callback_data="interval_300"),
        ],
        [
            InlineKeyboardButton("10 min", callback_data="interval_600"),
            InlineKeyboardButton("15 min", callback_data="interval_900"),
            InlineKeyboardButton("30 min", callback_data="interval_1800"),
        ],
        [
            InlineKeyboardButton("1 hour", callback_data="interval_3600"),
            InlineKeyboardButton("2 hours", callback_data="interval_7200"),
            InlineKeyboardButton("✏️ Custom", callback_data="interval_custom"),
        ],
        [InlineKeyboardButton("◀️ Back", callback_data="dashboard")],
    ])
    await safe_edit(
        query,
        f"⏱ <b>Set Broadcast Interval</b>\n\n"
        f"Current: <code>{current_label}</code>\n\n"
        "Choose how often to repeat broadcasting across all groups.\n"
        "<i>Tap a preset or enter a custom value in seconds.</i>",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )


async def interval_preset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, seconds: int):
    query = update.callback_query
    user_id = update.effective_user.id
    await db.set_interval(user_id, seconds)
    mins, secs = divmod(seconds, 60)
    label = f"{mins}m {secs}s" if mins else f"{secs}s"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back to Dashboard", callback_data="dashboard")]])
    await safe_edit(
        query,
        f"✅ <b>Interval set to {label}</b>\n\n"
        "The bot will wait this long between each broadcast cycle.",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )


async def interval_custom_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await db.set_waiting_for_interval(user_id, True)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="set_interval")]])
    await safe_edit(
        query,
        "✏️ <b>Custom Interval</b>\n\n"
        "Send me the interval in <b>seconds</b>.\n\n"
        "Examples:\n"
        "• <code>120</code> = 2 minutes\n"
        "• <code>600</code> = 10 minutes\n"
        "• <code>3600</code> = 1 hour",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )


async def handle_interval_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if not await db.is_waiting_for_interval(user_id):
        return False

    await db.set_waiting_for_interval(user_id, False)
    text = (update.message.text or "").strip()

    try:
        seconds = int(text)
        if seconds < 10:
            await update.message.reply_text("❌ Minimum interval is 10 seconds.", parse_mode="HTML")
            return True
        if seconds > 86400:
            await update.message.reply_text("❌ Maximum interval is 24 hours (86400 seconds).", parse_mode="HTML")
            return True
    except ValueError:
        await update.message.reply_text("❌ Please send a valid number (seconds).", parse_mode="HTML")
        return True

    await db.set_interval(user_id, seconds)
    mins, secs = divmod(seconds, 60)
    label = f"{mins}m {secs}s" if mins else f"{secs}s"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]])
    await update.message.reply_text(
        f"✅ <b>Interval set to {label}</b>\n\nThe bot will repeat broadcasting every {label}.",
        parse_mode="HTML", reply_markup=keyboard,
    )
    return True
