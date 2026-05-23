import asyncio
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit
from bot.utils.broadcaster import start_broadcast, stop_broadcast, _send_ad_via_pyrogram
from bot.utils.session_manager import get_pyrogram_client

logger = logging.getLogger(__name__)


async def _save_ad_to_saved_messages(owner_id: int, ad_data: dict):
    accounts = await db.get_accounts(owner_id)
    for acc in accounts:
        try:
            client = await get_pyrogram_client(acc["session"])
            async with client:
                await _send_ad_via_pyrogram(client, "me", ad_data)
        except Exception as e:
            logger.warning("save_to_saved_messages failed [%s]: %s", acc["phone"], e)
    await db.set_broadcast_mode(owner_id, "forward")


async def set_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await db.set_waiting_for_ad(user_id, True)
    await db.set_prompt_message(user_id, query.message.chat_id, query.message.message_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="dashboard", api_kwargs={"style": "danger"})]])
    await safe_edit(
        query,
        "<b>Set Ad Message</b>\n\n"
        "<blockquote>Forward any message from your Saved Messages, or send any message directly.\n"
        "Supports text, photos, videos, documents, audio, stickers — everything Telegram supports.\n"
        "Full formatting is preserved: bold, italic, code, blockquote, strikethrough, underline.</blockquote>\n\n"
        "Your message will be deleted automatically after saving.",
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

    ad_data = None
    if msg.photo:
        ad_data = {
            "type": "photo",
            "file_id": msg.photo[-1].file_id,
            "file_unique_id": msg.photo[-1].file_unique_id,
            "caption": msg.caption_html or msg.caption or "",
        }
    elif msg.video:
        ad_data = {
            "type": "video",
            "file_id": msg.video.file_id,
            "file_unique_id": msg.video.file_unique_id,
            "caption": msg.caption_html or msg.caption or "",
        }
    elif msg.document:
        ad_data = {
            "type": "document",
            "file_id": msg.document.file_id,
            "file_unique_id": msg.document.file_unique_id,
            "caption": msg.caption_html or msg.caption or "",
        }
    elif msg.audio:
        ad_data = {
            "type": "audio",
            "file_id": msg.audio.file_id,
            "file_unique_id": msg.audio.file_unique_id,
            "caption": msg.caption_html or msg.caption or "",
        }
    elif msg.animation:
        ad_data = {
            "type": "animation",
            "file_id": msg.animation.file_id,
            "file_unique_id": msg.animation.file_unique_id,
            "caption": msg.caption_html or msg.caption or "",
        }
    elif msg.sticker:
        ad_data = {
            "type": "sticker",
            "file_id": msg.sticker.file_id,
            "file_unique_id": msg.sticker.file_unique_id,
        }
    elif msg.voice:
        ad_data = {
            "type": "voice",
            "file_id": msg.voice.file_id,
            "file_unique_id": msg.voice.file_unique_id,
            "caption": msg.caption_html or msg.caption or "",
        }
    elif msg.video_note:
        ad_data = {
            "type": "video_note",
            "file_id": msg.video_note.file_id,
            "file_unique_id": msg.video_note.file_unique_id,
        }
    elif msg.text:
        ad_data = {
            "type": "text",
            "text": msg.text_html if msg.text_html else msg.text,
        }
    else:
        await db.set_waiting_for_ad(user_id, True)
        await update.message.reply_text("Unsupported message type. Please try again.")
        return True

    if msg.forward_date:
        ad_data["forwarded"] = True

    await db.set_ad_message_data(user_id, ad_data)
    asyncio.create_task(_save_ad_to_saved_messages(user_id, ad_data))

    try:
        await msg.delete()
    except Exception:
        pass

    prompt = await db.get_prompt_message(user_id)
    if prompt:
        chat_id, msg_id = prompt
        text, keyboard = await _build_dashboard_content_local(user_id)
        for method in ("edit_message_caption", "edit_message_text"):
            try:
                fn = getattr(context.bot, method)
                kwargs = {"chat_id": chat_id, "message_id": msg_id,
                          "reply_markup": keyboard, "parse_mode": "HTML"}
                if method == "edit_message_caption":
                    kwargs["caption"] = text
                else:
                    kwargs["text"] = text
                await fn(**kwargs)
                return True
            except Exception:
                continue

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})]])
    await context.bot.send_message(
        chat_id=msg.chat_id,
        text="<b>Ad message saved.</b>",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    return True


async def _build_dashboard_content_local(user_id: int):
    from bot.handlers.dashboard import _build_dashboard_content
    return await _build_dashboard_content(user_id)


async def start_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    ad_data = await db.get_ad_message_data(user_id)
    if not ad_data:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Set Ad Message", callback_data="set_ad", api_kwargs={"style": "primary"})]])
        await safe_edit(
            query,
            "<b>No ad message set.</b>\n\n"
            "<blockquote>Go to Set Ad Message first and send the message you want to broadcast.</blockquote>",
            reply_markup=keyboard, parse_mode="HTML", context=context,
        )
        return

    accounts = await db.get_accounts(user_id)
    if not accounts:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Add Account", callback_data="add_account", api_kwargs={"style": "primary"})]])
        await safe_edit(
            query,
            "<b>No accounts connected.</b>\n\n"
            "<blockquote>Add at least one Telegram account before starting ads.</blockquote>",
            reply_markup=keyboard, parse_mode="HTML", context=context,
        )
        return

    if await db.is_ads_running(user_id):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})]])
        await safe_edit(
            query,
            "<b>Ads are already running.</b>\n\nUse Stop Ads to stop the current broadcast.",
            reply_markup=keyboard, parse_mode="HTML", context=context,
        )
        return

    await start_broadcast(user_id)
    interval = await db.get_interval(user_id)
    mins, secs = divmod(interval, 60)
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})]])
    await safe_edit(
        query,
        f"<b>Ads Started</b>\n\n"
        f"<blockquote>Broadcasting to all groups via <b>{len(accounts)}</b> active account(s).\n"
        f"Interval: <b>{interval_label}</b></blockquote>",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )


async def stop_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await stop_broadcast(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})]])
    await safe_edit(
        query,
        "<b>Ads Stopped.</b>\n\n<blockquote>Broadcasting has been paused. Start again from the dashboard.</blockquote>",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )


async def toggle_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    current = await db.get_broadcast_mode(user_id)
    new_mode = "forward" if current == "direct" else "direct"
    await db.set_broadcast_mode(user_id, new_mode)
    mode_label = "Forward (from Saved Messages)" if new_mode == "forward" else "Direct (send stored content)"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Switch Again", callback_data="toggle_mode")],
        [InlineKeyboardButton("Dashboard", callback_data="dashboard", api_kwargs={"style": "success"})],
    ])
    await safe_edit(
        query,
        f"<b>Mode: {mode_label}</b>\n\n"
        "<blockquote><b>Direct</b> — sends the stored message content directly each time.\n"
        "<b>Forward</b> — forwards the latest message from each account's Saved Messages.</blockquote>",
        reply_markup=keyboard, parse_mode="HTML", context=context,
    )
