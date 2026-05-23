from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit
from bot.config import WEB_APP_URL


async def _build_dashboard_content(user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    accounts = await db.get_accounts(user_id)
    ad_data = await db.get_ad_message_data(user_id)
    running = await db.is_ads_running(user_id)
    mode = await db.get_broadcast_mode(user_id)
    interval = await db.get_interval(user_id)
    auto_reply = await db.is_auto_reply_enabled(user_id)

    ad_status = "Set" if ad_data else "Not Set"
    ad_type = f" ({ad_data['type']})" if ad_data else ""
    running_status = "Running" if running else "Paused"
    mode_label = "Forward" if mode == "forward" else "Direct"
    ar_label = "ON" if auto_reply else "OFF"
    mins, secs = divmod(interval, 60)
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    text = (
        "<b>Bumpify Dashboard</b>\n\n"
        f"Accounts: <code>{len(accounts)}</code>\n"
        f"Ad Message: <code>{ad_status}{ad_type}</code>\n"
        f"Send Mode: <code>{mode_label}</code>\n"
        f"Interval: <code>{interval_label}</code>\n"
        f"Status: <code>{running_status}</code>\n"
        f"Auto Reply: <code>{ar_label}</code>"
    )

    add_acc_btn = (
        InlineKeyboardButton("Add Account", web_app=WebAppInfo(url=WEB_APP_URL))
        if WEB_APP_URL
        else InlineKeyboardButton("Add Account", callback_data="add_account")
    )

    keyboard = InlineKeyboardMarkup([
        [add_acc_btn, InlineKeyboardButton("My Accounts", callback_data="my_accounts")],
        [InlineKeyboardButton("Set Ad Message", callback_data="set_ad"),
         InlineKeyboardButton("Send Mode", callback_data="toggle_mode")],
        [InlineKeyboardButton("Start Ads", callback_data="start_ads"),
         InlineKeyboardButton("Stop Ads", callback_data="stop_ads")],
        [InlineKeyboardButton("Set Interval", callback_data="set_interval"),
         InlineKeyboardButton("Analytics", callback_data="analytics")],
        [InlineKeyboardButton("Auto Reply", callback_data="auto_reply"),
         InlineKeyboardButton("Remove Account", callback_data="delete_account")],
        [InlineKeyboardButton("Home", callback_data="home")],
    ])
    return text, keyboard


async def dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    text, keyboard = await _build_dashboard_content(user_id)

    if query:
        await safe_edit(query, text, reply_markup=keyboard, parse_mode="HTML", context=context)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
