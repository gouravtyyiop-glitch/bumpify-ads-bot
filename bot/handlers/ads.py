from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.broadcaster import start_broadcast, stop_broadcast


async def set_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()
    await db.set_waiting_for_ad(user_id, True)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="dashboard")]])
    await query.edit_message_text(
        "✏️ **Set Ad Message**\n\n"
        "Send me the message you want to broadcast.\n\n"
        "Supports: **bold**, _italic_, `code`, >blockquote, and all Telegram formatting.\n\n"
        "📝 Your message will be saved and used for broadcasting.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def handle_ad_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await db.is_waiting_for_ad(user_id):
        return False

    msg = update.message
    text = msg.text or msg.caption or ""

    if not text:
        await update.message.reply_text("❌ Please send a text message for the ad.")
        return True

    await db.set_ad_message(user_id, text, [])
    await db.set_waiting_for_ad(user_id, False)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Go to Dashboard", callback_data="dashboard")]
    ])
    await update.message.reply_text(
        "✅ **Ad message saved!**\n\n"
        f"📝 Preview:\n\n{text}\n\n"
        "You can now start broadcasting from the dashboard.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    return True


async def start_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    ad_text = await db.get_ad_text(user_id)
    if not ad_text:
        await query.answer(
            "⚠️ Ad message not set! Please set your ad message first before starting.",
            show_alert=True,
        )
        return

    accounts = await db.get_accounts(user_id)
    if not accounts:
        await query.answer(
            "⚠️ No accounts added! Add at least one account before starting ads.",
            show_alert=True,
        )
        return

    if await db.is_ads_running(user_id):
        await query.answer("Ads are already running!", show_alert=True)
        return

    await start_broadcast(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]])
    await query.edit_message_text(
        "▶️ **Ads Started!**\n\n"
        f"Broadcasting to all groups via `{len(accounts)}` account(s).\n"
        "Use the dashboard to monitor or stop.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def stop_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    await stop_broadcast(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]])
    await query.edit_message_text(
        "⏹ **Ads Stopped.**\n\nBroadcasting has been paused. Start again from the dashboard.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def toggle_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    current = await db.get_broadcast_mode(user_id)
    new_mode = "forward" if current == "direct" else "direct"
    await db.set_broadcast_mode(user_id, new_mode)

    label = "📤 Forward Mode" if new_mode == "forward" else "📨 Direct Mode"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Switch Mode", callback_data="toggle_mode")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
    ])
    await query.edit_message_text(
        f"✅ **Send mode changed to {label}**\n\n"
        "• **Direct** — Sends the message directly (default)\n"
        "• **Forward** — Forwards your saved message\n\n"
        f"Current mode: **{label}**",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
