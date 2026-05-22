from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils.helpers import safe_edit

FAQ_TEXT = (
    "❓ <b>Frequently Asked Questions</b>\n\n"
    "<b>Q: How do I add a Telegram account?</b>\n"
    "Tap <b>Add Account</b> on the dashboard and log in with phone + OTP via the web panel.\n\n"
    "<b>Q: Why is my ad not sending?</b>\n"
    "Make sure you have set an ad message first. Go to <b>Set Ad Message</b> and send your text.\n\n"
    "<b>Q: Will it send to channels?</b>\n"
    "No. Bumpify only broadcasts to <b>groups</b> — channels are skipped automatically.\n\n"
    "<b>Q: What is Forward vs Direct mode?</b>\n"
    "<b>Direct</b> sends fresh each time. <b>Forward</b> forwards your last saved message.\n\n"
    "<b>Q: Is my account safe?</b>\n"
    "Yes. All sessions are encrypted with AES-256. Passwords are never stored.\n\n"
    "<b>Q: What does the tracking bot do?</b>\n"
    "It sends real-time analytics — success/failed counts after each broadcast cycle.\n\n"
    "<b>Q: Can I add unlimited accounts?</b>\n"
    "Yes — no limit.\n\n"
    "<b>Q: How do I set the broadcast interval?</b>\n"
    "Tap <b>Set Interval</b> on the dashboard and choose a preset or type custom seconds.\n\n"
    "<b>Q: Does formatting work in my ads?</b>\n"
    "Yes. Telegram supports bold, italic, code, blockquote, underline, strikethrough in messages."
)


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="home")]])
    await safe_edit(query, FAQ_TEXT, reply_markup=keyboard, parse_mode="HTML", context=context)


async def howto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "📖 <b>How To Use Bumpify</b>\n\n"
        "<b>Step 1</b> — Add your Telegram account\n"
        "Tap <b>Add Account</b> → web panel → enter phone &amp; OTP\n\n"
        "<b>Step 2</b> — Set your ad message\n"
        "Tap <b>Set Ad Message</b> → send the text you want to broadcast\n\n"
        "<b>Step 3</b> — Set interval\n"
        "Tap <b>Set Interval</b> → choose how often to repeat (e.g. 5 minutes)\n\n"
        "<b>Step 4</b> — Choose send mode\n"
        "<b>Direct</b> (default) or <b>Forward</b> — toggle from dashboard\n\n"
        "<b>Step 5</b> — Start the tracking bot\n"
        "Message your tracking bot so it can send you analytics\n\n"
        "<b>Step 6</b> — Start Ads\n"
        "Tap <b>Start Ads</b> — broadcasting begins across all your groups automatically"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="home")]])
    await safe_edit(query, text, reply_markup=keyboard, parse_mode="HTML", context=context)
