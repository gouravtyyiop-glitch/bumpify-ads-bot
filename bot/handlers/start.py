from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
from bot.config import START_IMAGE_URL, START_CAPTION, TRACKING_BOT_USERNAME, WEB_APP_URL
from bot.utils import db


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user.id, {"user_id": user.id, "username": user.username, "name": user.full_name})

    tracking_msg = ""
    if TRACKING_BOT_USERNAME:
        tracking_msg = (
            f"\n\n⚠️ *Important:* Please start @{TRACKING_BOT_USERNAME} first before running ads.\n"
            "This bot tracks all your broadcast analytics."
        )

    caption = START_CAPTION + tracking_msg

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Open Dashboard", callback_data="dashboard")],
        [
            InlineKeyboardButton("📖 FAQ", callback_data="faq"),
            InlineKeyboardButton("📊 Updates", url="https://t.me/bumpify_updates") if not WEB_APP_URL else InlineKeyboardButton("🌐 Web Panel", web_app=WebAppInfo(url=WEB_APP_URL)),
        ],
        [InlineKeyboardButton("❓ How To Use", callback_data="howto")],
    ])

    try:
        if START_IMAGE_URL:
            await update.message.reply_photo(
                photo=START_IMAGE_URL,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
        else:
            await update.message.reply_text(
                caption,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
    except Exception:
        await update.message.reply_text(
            caption,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
