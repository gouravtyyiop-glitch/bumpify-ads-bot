from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit
from bot.config import WEB_APP_URL


async def dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    accounts = await db.get_accounts(user_id)
    ad_text = await db.get_ad_text(user_id)
    running = await db.is_ads_running(user_id)
    mode = await db.get_broadcast_mode(user_id)
    interval = await db.get_interval(user_id)

    ad_status = "✅ Set" if ad_text else "❌ Not Set"
    running_status = "▶️ Running" if running else "⏸ Paused"
    mode_label = "📤 Forward" if mode == "forward" else "📨 Direct"
    mins, secs = divmod(interval, 60)
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    text = (
        "<b>📊 Bumpify DASHBOARD</b>\n\n"
        f"• <b>Accounts:</b> <code>{len(accounts)}</code>\n"
        f"• <b>Ad Message:</b> {ad_status}\n"
        f"• <b>Send Mode:</b> {mode_label}\n"
        f"• <b>Interval:</b> <code>{interval_label}</code>\n"
        f"• <b>Status:</b> {running_status}\n\n"
        "<i>Choose an action below to continue</i>"
    )

    add_acc_btn = (
        InlineKeyboardButton("➕ Add Account", web_app=WebAppInfo(url=WEB_APP_URL))
        if WEB_APP_URL
        else InlineKeyboardButton("➕ Add Account", callback_data="add_account")
    )

    keyboard = InlineKeyboardMarkup([
        [add_acc_btn, InlineKeyboardButton("👥 My Accounts", callback_data="my_accounts")],
        [InlineKeyboardButton("✏️ Set Ad Message", callback_data="set_ad"), InlineKeyboardButton("🔁 Send Mode", callback_data="toggle_mode")],
        [InlineKeyboardButton("▶️ Start Ads", callback_data="start_ads"), InlineKeyboardButton("⏹ Stop Ads", callback_data="stop_ads")],
        [InlineKeyboardButton("⏱ Set Interval", callback_data="set_interval"), InlineKeyboardButton("📈 Analytics", callback_data="analytics")],
        [InlineKeyboardButton("🗑 Delete Account", callback_data="delete_account"), InlineKeyboardButton("❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton("🏠 Home", callback_data="home")],
    ])

    if query:
        await safe_edit(query, text, reply_markup=keyboard, parse_mode="HTML", context=context)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
