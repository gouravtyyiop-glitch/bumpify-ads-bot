import asyncio
import logging
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes

from bot.utils import db
from bot.utils.helpers import safe_edit
from bot.utils.broadcaster import start_broadcast, stop_broadcast
from bot.utils.session_manager import get_pyrogram_client
from bot.config import WEB_APP_URL, LOGGER_BOT_TOKEN, LOGGER_BOT_USERNAME

logger = logging.getLogger(__name__)


def parse_message_link(link: str):
    link = (link or "").strip()

    m = re.search(r"t\.me/c/(\d+)/(?:\d+/)?(\d+)", link)
    if m:
        return int("-100" + m.group(1)), int(m.group(2))

    m = re.search(r"t\.me/([A-Za-z0-9_]+)/(\d+)", link)
    if m:
        return "@" + m.group(1), int(m.group(2))

    return None, None


async def _save_link_to_saved_messages(owner_id: int, link: str):
    accounts = await db.get_accounts(owner_id)
    from_chat_id, message_id = parse_message_link(link)

    if not from_chat_id or not message_id:
        logger.warning("Invalid ad message link: %s", link)
        return

    for acc in accounts:
        try:
            client = await get_pyrogram_client(acc["session"])
            async with client:
                await client.forward_messages(
                    chat_id="me",
                    from_chat_id=from_chat_id,
                    message_ids=message_id,
                )
                logger.info("Ad link saved to Saved Messages for %s", acc.get("phone"))
        except Exception as e:
            logger.warning("save_link_to_saved_messages failed [%s]: %s", acc.get("phone"), e)


async def set_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    await db.set_waiting_for_ad(user_id, True)

    try:
        await db.set_prompt_message(
            user_id,
            query.message.chat.id,
            query.message.message_id,
        )
    except Exception as e:
        logger.warning("set_prompt_message failed: %s", e)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Cancel", callback_data="dashboard")]
    ])

    await safe_edit(
        query,
        "<b>Set Ad Message</b>\n\n"
        "<blockquote>Send the Telegram message link now.\n\n"
        "Examples:\n"
        "<code>https://t.me/yourchannel/123</code>\n"
        "<code>https://t.me/c/1234567890/123</code>\n\n"
        "Premium emojis will stay preserved because the source message will be forwarded to each ad account's Saved Messages.\n\n"
        "Important: every ad account must have access to that channel/group.</blockquote>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )


async def handle_ad_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id

    if not await db.is_waiting_for_ad(user_id):
        return False

    await db.set_waiting_for_ad(user_id, False)

    msg = update.message
    text = (msg.text or msg.caption or "").strip()

    from_chat_id, message_id = parse_message_link(text)

    if not from_chat_id or not message_id:
        await msg.reply_text(
            "<b>❌ Invalid message link.</b>\n\n"
            "<blockquote>Send a valid Telegram message link like:\n"
            "<code>https://t.me/yourchannel/123</code>\n"
            "<code>https://t.me/c/1234567890/123</code></blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Set Again", callback_data="set_ad")],
                [InlineKeyboardButton("Dashboard", callback_data="dashboard")],
            ]),
        )
        return True

    accounts = await db.get_accounts(user_id)
    if not accounts:
        await msg.reply_text(
            "<b>❌ No accounts connected.</b>\n\n"
            "<blockquote>Add at least one Telegram account first.</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
            ]),
        )
        return True

    await db.set_ad_message_data(user_id, {
        "set": True,
        "type": "message_link",
        "link": text,
        "from_chat_id": str(from_chat_id),
        "message_id": message_id,
    })

    asyncio.create_task(_save_link_to_saved_messages(user_id, text))

    try:
        await msg.delete()
    except Exception:
        pass

    prompt = await db.get_prompt_message(user_id)
    if prompt:
        chat_id, msg_id = prompt
        text_dash, keyboard = await _build_dashboard_content_local(user_id)

        for method in ("edit_message_caption", "edit_message_text"):
            try:
                fn = getattr(context.bot, method)
                kwargs = {
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "reply_markup": keyboard,
                    "parse_mode": "HTML",
                }
                if method == "edit_message_caption":
                    kwargs["caption"] = text_dash
                else:
                    kwargs["text"] = text_dash

                await fn(**kwargs)
                return True
            except Exception:
                continue

    await context.bot.send_message(
        chat_id=msg.chat_id,
        text="<b>✅ Ad message link saved.</b>\n\n"
             "<blockquote>Forwarding source message to all ad accounts' Saved Messages...</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
        ]),
    )

    return True


async def _build_dashboard_content_local(user_id: int):
    from bot.handlers.dashboard import _build_dashboard_content
    return await _build_dashboard_content(user_id)


async def remove_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    await db.clear_ad_message_data(user_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
    ])

    await safe_edit(
        query,
        "<b>Ad message removed.</b>\n\n"
        "<blockquote>Your ad has been cleared. Set a new message link from the dashboard.</blockquote>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )


async def start_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    ad_data = await db.get_ad_message_data(user_id)
    if not ad_data:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Set Ad Message", callback_data="set_ad")]
        ])
        await safe_edit(
            query,
            "<b>No ad message set.</b>\n\n"
            "<blockquote>Set your ad message link first.</blockquote>",
            reply_markup=keyboard,
            parse_mode="HTML",
            context=context,
        )
        return

    accounts = await db.get_accounts(user_id)
    if not accounts:
        add_btn = (
            InlineKeyboardButton("Add Account", web_app=WebAppInfo(url=WEB_APP_URL))
            if WEB_APP_URL
            else InlineKeyboardButton("Add Account", callback_data="add_account")
        )

        await safe_edit(
            query,
            "<b>No accounts connected.</b>\n\n"
            "<blockquote>Add at least one Telegram account before starting ads.</blockquote>",
            reply_markup=InlineKeyboardMarkup([[add_btn]]),
            parse_mode="HTML",
            context=context,
        )
        return

    targets = await db.get_targets(user_id)
    if not targets:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Set Target Links", callback_data="set_targets")],
            [InlineKeyboardButton("Dashboard", callback_data="dashboard")],
        ])
        await safe_edit(
            query,
            "<b>No target links set.</b>\n\n"
            "<blockquote>Add group/forum links first. Ads will only be sent to those links.</blockquote>",
            reply_markup=keyboard,
            parse_mode="HTML",
            context=context,
        )
        return

    if LOGGER_BOT_TOKEN and not await db.is_logger_started(user_id):
        note = f" @{LOGGER_BOT_USERNAME}" if LOGGER_BOT_USERNAME else ""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
        ])

        await safe_edit(
            query,
            f"<b>Start your Logger Bot first!</b>\n\n"
            f"<blockquote>Open your logger bot{note} and send /start before starting ads.</blockquote>",
            reply_markup=keyboard,
            parse_mode="HTML",
            context=context,
        )
        return

    if await db.is_ads_running(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
        ])
        await safe_edit(
            query,
            "<b>Ads are already running.</b>\n\nUse Stop Ads to stop the current broadcast.",
            reply_markup=keyboard,
            parse_mode="HTML",
            context=context,
        )
        return

    await start_broadcast(user_id)

    interval = await db.get_interval(user_id)
    mins, secs = divmod(interval, 60)
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
    ])

    await safe_edit(
        query,
        f"<b>🚀 Ads Started</b>\n\n"
        f"<blockquote>Broadcasting from Saved Messages via <b>{len(accounts)}</b> account(s).\n"
        f"Targets: <b>{len(targets)}</b>\n"
        f"Interval: <b>{interval_label}</b></blockquote>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )


async def stop_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Dashboard", callback_data="dashboard")]
    ])

    if not await db.is_ads_running(user_id):
        await safe_edit(
            query,
            "<b>No ads are currently running.</b>\n\n"
            "<blockquote>Start a broadcast first from the dashboard.</blockquote>",
            reply_markup=keyboard,
            parse_mode="HTML",
            context=context,
        )
        return

    await stop_broadcast(user_id)

    await safe_edit(
        query,
        "<b>Ads Stopped.</b>\n\n"
        "<blockquote>Broadcasting has been paused. Start again from the dashboard.</blockquote>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )
