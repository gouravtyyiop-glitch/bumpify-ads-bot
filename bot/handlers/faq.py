from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


FAQ_TEXT = (
    "❓ **Frequently Asked Questions**\n\n"
    "**Q: How do I add a Telegram account?**\n"
    "> Tap **Add Account** on the dashboard and use the web panel to log in with your phone number and OTP.\n\n"
    "**Q: Why is my ad not sending?**\n"
    "> Make sure you have set an ad message first. Go to **Set Ad Message** and send your text.\n\n"
    "**Q: Will it send to channels too?**\n"
    "> No. Bumpify only broadcasts to **groups** — channels are skipped automatically.\n\n"
    "**Q: What is Forward vs Direct mode?**\n"
    "> **Direct** sends the message fresh each time.\n"
    "> **Forward** forwards your saved message (shows 'Forwarded from' tag).\n\n"
    "**Q: Is my account safe?**\n"
    "> Yes. All sessions are encrypted with AES-256 before storage. We never store your password.\n\n"
    "**Q: What does the tracking bot do?**\n"
    "> It receives real-time analytics — success/failed counts after each broadcast cycle.\n\n"
    "**Q: Can I add unlimited accounts?**\n"
    "> Yes! There is no limit on how many accounts you can add.\n\n"
    "**Q: How do I stop ads?**\n"
    "> Tap **Stop Ads** on the dashboard. Broadcasting stops immediately.\n\n"
    "**Q: Does formatting work in my ads?**\n"
    "> Yes. Bumpify supports full Markdown: **bold**, _italic_, `code`, >blockquote, __underline__, ~~strikethrough~~."
)


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="home")]])
    await query.edit_message_text(FAQ_TEXT, parse_mode="Markdown", reply_markup=keyboard)


async def howto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📖 **How To Use Bumpify**\n\n"
        "**Step 1** — Add your Telegram account\n"
        "> Tap **Add Account** → use the web panel → enter phone & OTP\n\n"
        "**Step 2** — Set your ad message\n"
        "> Tap **Set Ad Message** → send the text you want to broadcast\n\n"
        "**Step 3** — Choose send mode\n"
        "> **Direct** (default) or **Forward** — toggle from dashboard\n\n"
        "**Step 4** — Start the tracking bot\n"
        "> Message the tracking bot so it can send you analytics\n\n"
        "**Step 5** — Start Ads\n"
        "> Tap **Start Ads** — broadcasting begins across all your groups\n\n"
        "**Step 6** — Monitor\n"
        "> Check **Analytics** for success/fail counts in real time"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="home")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
