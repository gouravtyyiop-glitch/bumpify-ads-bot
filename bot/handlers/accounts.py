from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db


async def my_accounts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    accounts = await db.get_accounts(user_id)

    if not accounts:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="dashboard")]])
        await query.edit_message_text(
            "👥 **My Accounts**\n\n❌ No accounts added yet.\nUse **Add Account** to get started.",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return

    lines = ["👥 **My Accounts**\n"]
    for i, acc in enumerate(accounts, 1):
        lines.append(f"`{i}.` **{acc['name']}**\n   📱 `{acc['phone']}`")

    lines.append(f"\n📊 Total: **{len(accounts)} account(s)**")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Remove Account", callback_data="delete_account")],
        [InlineKeyboardButton("◀️ Back", callback_data="dashboard")],
    ])
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def delete_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    accounts = await db.get_accounts(user_id)
    if not accounts:
        await query.answer("No accounts to delete.", show_alert=True)
        return

    buttons = []
    for acc in accounts:
        buttons.append([InlineKeyboardButton(
            f"🗑 {acc['name']} ({acc['phone']})",
            callback_data=f"del_acc_{acc['phone']}",
        )])
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="my_accounts")])

    await query.edit_message_text(
        "🗑 **Remove Account**\n\nSelect the account to remove:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def confirm_delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    await db.remove_account(user_id, phone)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back to Dashboard", callback_data="dashboard")]])
    await query.edit_message_text(
        f"✅ Account `{phone}` has been removed successfully.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def analytics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    stats = await db.get_broadcast_stats(user_id)
    accounts = await db.get_accounts(user_id)
    running = await db.is_ads_running(user_id)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="dashboard")]])
    await query.edit_message_text(
        "📈 **Analytics**\n\n"
        f"• **Total Broadcasts:** `{stats['total']}`\n"
        f"• **Successful:** `{stats['success']}`\n"
        f"• **Failed:** `{stats['failed']}`\n"
        f"• **Active Accounts:** `{len(accounts)}`\n"
        f"• **Status:** {'▶️ Running' if running else '⏸ Paused'}\n\n"
        "_Analytics are tracked in real-time via your tracking bot._",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
