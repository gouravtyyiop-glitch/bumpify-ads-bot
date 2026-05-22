from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit
from bot.utils.broadcaster import start_broadcast, stop_broadcast


async def set_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()
    await db.set_waiting_for_ad(user_id, True)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="dashboard")]])
    await safe_edit(
        query,
        "✏️ <b>Set Ad Message</b>\n\n"
        "Send me the message you want to broadcast to all groups.\n\n"
        "Supports full formatting: <b>bold</b>, <i>italic</i>, <code>code</code>, blockquote, underline, strikethrough — everything Telegram supports.\n\n"
        "📝 Just type or paste your message now.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_ad_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
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

    preview = text[:300] + ("..." if len(text) > 300 else "")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Go to Dashboard", callback_data="dashboard")]
    ])
    await update.message.reply_text(
        f"✅ <b>Ad message saved!</b>\n\n"
        f"📝 Preview:\n<code>{preview}</code>\n\n"
        "You can now start broadcasting from the dashboard.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    return True


async def start_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    ad_text = await db.get_ad_text(user_id)
    if not ad_text:
        await query.answer(
            "⚠️ Ad message not set! Go to Set Ad Message first.",
            show_alert=True,
        )
        return

    accounts = await db.get_accounts(user_id)
    if not accounts:
        await query.answer(
            "⚠️ No accounts added! Add at least one account first.",
            show_alert=True,
        )
        return

    if await db.is_ads_running(user_id):
        await query.answer("Ads are already running!", show_alert=True)
        return

    await query.answer()
    await start_broadcast(user_id)

    interval = await db.get_interval(user_id)
    mins = interval // 60
    secs = interval % 60
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]])
    await safe_edit(
        query,
        f"▶️ <b>Ads Started!</b>\n\n"
        f"Broadcasting to all groups via <code>{len(accounts)}</code> account(s).\n"
        f"⏱ Interval: <code>{interval_label}</code>\n\n"
        "Use the dashboard to monitor or stop.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def stop_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    await stop_broadcast(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]])
    await safe_edit(
        query,
        "⏹ <b>Ads Stopped.</b>\n\nBroadcasting has been paused. Start again from the dashboard.",
        reply_markup=keyboard,
        parse_mode="HTML",
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
        [InlineKeyboardButton("🔁 Switch Again", callback_data="toggle_mode")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
    ])
    await safe_edit(
        query,
        f"✅ <b>Mode changed to {label}</b>\n\n"
        "• <b>Direct</b> — Sends the message fresh (default)\n"
        "• <b>Forward</b> — Forwards your last saved message\n\n"
        f"Current: <b>{label}</b>",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
