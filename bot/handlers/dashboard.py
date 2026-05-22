from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
from bot.utils import db
from bot.config import WEB_APP_URL


async def dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    accounts = await db.get_accounts(user_id)
    ad_text = await db.get_ad_text(user_id)
    running = await db.is_ads_running(user_id)
    mode = await db.get_broadcast_mode(user_id)

    ad_status = "✅ Set" if ad_text else "❌ Not Set"
    running_status = "▶️ Running" if running else "⏸ Paused"
    mode_label = "📤 Forward" if mode == "forward" else "📨 Direct"

    text = (
        "**📊 Bumpify DASHBOARD**\n\n"
        f"• **Accounts:** `{len(accounts)}`\n"
        f"• **Ad Message:** {ad_status}\n"
        f"• **Send Mode:** {mode_label}\n"
        f"• **Status:** {running_status}\n\n"
        "_Choose an action below to continue_"
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
        [InlineKeyboardButton("🗑 Delete Account", callback_data="delete_account"), InlineKeyboardButton("📈 Analytics", callback_data="analytics")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq"), InlineKeyboardButton("🏠 Home", callback_data="home")],
    ])

    if query:
        await query.answer()
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
