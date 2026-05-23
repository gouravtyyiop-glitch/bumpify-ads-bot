from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TRACKING_BOT_TOKEN


async def tracking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Bumpify Tracking Bot</b>\n\n"
        "You are now registered to receive broadcast analytics.\n\n"
        "After each broadcast cycle you will receive a report per account with:\n"
        "  - Success / failed counts\n"
        "  - Each group name, username, link and ID\n"
        "  - Next cycle countdown\n\n"
        "Keep this chat open to receive real-time updates.",
        parse_mode="HTML",
    )


def build_tracking_app() -> Application:
    app = Application.builder().token(TRACKING_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", tracking_start))
    return app
