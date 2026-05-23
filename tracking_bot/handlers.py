from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import LOGGER_BOT_TOKEN


async def logger_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Bumpify Logger Bot</b>\n\n"
        "You are now registered to receive broadcast logs.\n\n"
        "After each broadcast cycle you will receive a log per account with:\n"
        "  - Success / failed counts\n"
        "  - Each group name, username, link and ID\n"
        "  - Next cycle countdown\n\n"
        "Keep this chat open to receive real-time logs.",
        parse_mode="HTML",
    )


def build_logger_app() -> Application:
    app = Application.builder().token(LOGGER_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", logger_start))
    return app
