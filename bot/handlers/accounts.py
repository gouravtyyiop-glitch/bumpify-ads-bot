from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit


async def my_accounts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    accounts = await db.get_accounts(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="dashboard")]])

    if not accounts:
        await safe_edit(
            query,
            "👥 <b>My Accounts</b>\n\n❌ No accounts added yet.\nUse <b>Add Account</b> to get started.",
            reply_markup=keyboard, parse_mode="HTML", context=context,
        )
        return

    lines = ["👥 <b>My Accounts</b>\n"]
    for i, acc in enumerate(accounts, 1):
        lines.append(f"<code>{i}.</code> <b>{acc['name']}</b>\n   📱 <code>{acc['phone']}</code>")
    lines.append(f"\n📊 Total: <b>{len(accounts)} account(s)</b>")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Remove Account", callback_data="delete_account")],
        [InlineKeyboardButton("◀️ Back", callback_data="dashboard")],
    ])
    await safe_edit(query, "\n".join(lines), reply_markup=keyboard, parse_mode="HTML", context=context)


async def delete_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    accounts = await db.get_accounts(user_id)

    if not accounts:
        await safe_edit(
            query, "❌ No accounts to remove.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="dashboard")]]),
            parse_mode="HTML", context=context,
        )
        return

    buttons = [
        [InlineKeyboardButton(f"🗑 {acc['name']} ({acc['phone']})", callback_data=f"del_acc_{acc['phone']}")]
        for acc in accounts
    ]
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="my_accounts")])
    await safe_edit(
        query, "🗑 <b>Remove Account</b>\n\nSelect the account to remove:",
        reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML", context=context,
    )


async def confirm_delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str):
    query = update.callback_query
    user_id = update.effective_user.id
    await db.remove_account(user_id, phone)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back to Dashboard", callback_data="dashboard")]])
    await safe_edit(
        query, f"✅ Account <code>{phone}</code> removed successfully.",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )


async def analytics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    stats = await db.get_broadcast_stats(user_id)
    accounts = await db.get_accounts(user_id)
    running = await db.is_ads_running(user_id)
    interval = await db.get_interval(user_id)
    mins, secs = divmod(interval, 60)
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="dashboard")]])
    await safe_edit(
        query,
        "📈 <b>Analytics</b>\n\n"
        f"• <b>Total Broadcasts:</b> <code>{stats['total']}</code>\n"
        f"• <b>Successful:</b> <code>{stats['success']}</code>\n"
        f"• <b>Failed:</b> <code>{stats['failed']}</code>\n"
        f"• <b>Active Accounts:</b> <code>{len(accounts)}</code>\n"
        f"• <b>Interval:</b> <code>{interval_label}</code>\n"
        f"• <b>Status:</b> {'▶️ Running' if running else '⏸ Paused'}\n\n"
        "<i>Real-time analytics are sent to your tracking bot after each cycle.</i>",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )
