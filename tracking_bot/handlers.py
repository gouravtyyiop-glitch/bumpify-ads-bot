from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TRACKING_BOT_TOKEN


async def tracking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **Bumpify Tracking Bot**\n\n"
        "✅ You are now registered to receive broadcast analytics.\n\n"
        "Every time your accounts broadcast messages, you'll get a report here with:\n"
        "• ✅ Success count\n"
        "• ❌ Failed count\n"
        "• 📱 Accounts used\n\n"
        "_Keep this bot open to receive real-time updates._",
        parse_mode="Markdown",
    )


def build_tracking_app() -> Application:
    app = Application.builder().token(TRACKING_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", tracking_start))
    return app
