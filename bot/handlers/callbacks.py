from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.handlers.dashboard import dashboard_handler
from bot.handlers.accounts import (
    my_accounts_handler,
    delete_account_handler,
    confirm_delete_handler,
    analytics_handler,
)
from bot.handlers.ads import (
    set_ad_handler,
    start_ads_handler,
    stop_ads_handler,
    toggle_mode_handler,
)
from bot.handlers.faq import faq_handler, howto_handler
from bot.handlers.start import start_handler
from bot.config import START_IMAGE_URL, START_CAPTION, TRACKING_BOT_USERNAME, WEB_APP_URL
from telegram import WebAppInfo


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "dashboard":
        await dashboard_handler(update, context)
    elif data == "my_accounts":
        await my_accounts_handler(update, context)
    elif data == "delete_account":
        await delete_account_handler(update, context)
    elif data.startswith("del_acc_"):
        phone = data[len("del_acc_"):]
        await confirm_delete_handler(update, context, phone)
    elif data == "analytics":
        await analytics_handler(update, context)
    elif data == "set_ad":
        await set_ad_handler(update, context)
    elif data == "start_ads":
        await start_ads_handler(update, context)
    elif data == "stop_ads":
        await stop_ads_handler(update, context)
    elif data == "toggle_mode":
        await toggle_mode_handler(update, context)
    elif data == "faq":
        await faq_handler(update, context)
    elif data == "howto":
        await howto_handler(update, context)
    elif data == "home":
        await _home_handler(update, context)
    elif data == "add_account":
        await _add_account_fallback(update, context)


async def _home_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tracking_msg = ""
    if TRACKING_BOT_USERNAME:
        tracking_msg = (
            f"\n\n⚠️ *Important:* Please start @{TRACKING_BOT_USERNAME} first before running ads."
        )

    caption = START_CAPTION + tracking_msg
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Open Dashboard", callback_data="dashboard")],
        [
            InlineKeyboardButton("📖 FAQ", callback_data="faq"),
            InlineKeyboardButton("🌐 Web Panel", web_app=WebAppInfo(url=WEB_APP_URL)) if WEB_APP_URL else InlineKeyboardButton("📊 Updates", callback_data="noop"),
        ],
        [InlineKeyboardButton("❓ How To Use", callback_data="howto")],
    ])
    await query.edit_message_text(caption, parse_mode="Markdown", reply_markup=keyboard)


async def _add_account_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="dashboard")]])
    await query.edit_message_text(
        "➕ **Add Account**\n\n"
        "To add a Telegram account, please set up the **WEB_APP_URL** environment variable.\n\n"
        "The web panel allows you to log in with phone + OTP securely.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
