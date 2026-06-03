import re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit


def parse_target_link(link: str) -> dict | None:
    link = link.strip()
    if not link:
        return None

    m = re.search(r"t\.me/c/(\d+)/(\d+)", link)
    if m:
        return {
            "chat_id": int("-100" + m.group(1)),
            "topic_id": int(m.group(2)),
            "link": link,
            "title": f"Topic {m.group(2)}",
            "username": "",
        }

    m = re.search(r"t\.me/([A-Za-z0-9_]+)/(\d+)", link)
    if m:
        return {
            "chat_id": "@" + m.group(1),
            "topic_id": int(m.group(2)),
            "link": link,
            "title": f"Topic {m.group(2)}",
            "username": m.group(1),
        }

    m = re.search(r"t\.me/([A-Za-z0-9_]+)$", link)
    if m:
        return {
            "chat_id": "@" + m.group(1),
            "topic_id": None,
            "link": link,
            "title": m.group(1),
            "username": m.group(1),
        }

    return None


async def set_targets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    await db.set_waiting_for_targets(user_id, True)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="dashboard", api_kwargs={"style": "danger"})]
    ])

    await safe_edit(
        query,
        "<b>Set Target Links</b>\n\n"
        "<blockquote>Send group/forum links, one per line.\n\n"
        "Examples:\n"
        "https://t.me/DealerMarketPlace/16\n"
        "https://t.me/RareHandle/5737\n"
        "https://t.me/c/1234567890/55\n"
        "https://t.me/groupusername</blockquote>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )


async def handle_target_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id

    if not await db.is_waiting_for_targets(user_id):
        return False

    await db.set_waiting_for_targets(user_id, False)

    text = update.message.text or ""
    targets = []
    failed = []

    for line in text.replace(",", "\n").splitlines():
        line = line.strip()
        if not line:
            continue

        target = parse_target_link(line)
        if target:
            targets.append(target)
        else:
            failed.append(line)

    if not targets:
        await update.message.reply_text(
            "<b>❌ No valid target links found.</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Set Again", callback_data="set_targets", api_kwargs={"style": "primary"})],
                [InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})],
            ]),
        )
        return True

    await db.set_targets(user_id, targets)

    msg = f"<b>✅ Saved {len(targets)} target link(s).</b>"
    if failed:
        msg += "\n\n<b>Invalid skipped:</b>\n" + "\n".join(failed[:10])

    await update.message.reply_text(
        msg,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})]
        ]),
    )
    return True


async def view_targets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    targets = await db.get_targets(user_id)

    if not targets:
        text = "<b>No target links set.</b>"
    else:
        lines = [f"<b>Target Links: {len(targets)}</b>\n"]
        for i, t in enumerate(targets[:50], 1):
            link = t.get("link", "")
            title = t.get("title") or str(t.get("chat_id"))
            if link:
                lines.append(f"{i}. <a href='{link}'>{title}</a>")
            else:
                lines.append(f"{i}. <code>{t.get('chat_id')}</code>")

        if len(targets) > 50:
            lines.append(f"\n<i>... and {len(targets) - 50} more</i>")

        text = "\n".join(lines)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Set Target Links", callback_data="set_targets", api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("Clear Targets", callback_data="clear_targets", api_kwargs={"style": "danger"})],
        [InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})],
    ])

    await safe_edit(query, text, reply_markup=keyboard, parse_mode="HTML", context=context)


async def clear_targets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    await db.clear_targets(user_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})]
    ])

    await safe_edit(
        query,
        "<b>✅ Target links cleared.</b>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )