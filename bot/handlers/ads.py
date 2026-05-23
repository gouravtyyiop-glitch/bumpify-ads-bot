import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.utils import db
from bot.utils.helpers import safe_edit
from bot.utils.broadcaster import start_broadcast, stop_broadcast

logger = logging.getLogger(__name__)

_AD_MSG_TYPES = ("text", "photo", "video", "document", "audio", "animation",
                 "sticker", "voice", "video_note")


async def set_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await db.set_waiting_for_ad(user_id, True)
    await db.set_prompt_message(user_id, query.message.chat_id, query.message.message_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="dashboard")]])
    await safe_edit(
        query,
        "<b>Set Ad Message</b>\n\n"
        "Forward any message from your Saved Messages, or send any message directly.\n\n"
        "Supports text, photos, videos, documents, audio, stickers — everything.\n\n"
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
        ad_data = {"type": "photo", "file_id": msg.photo[-1].file_id,
                   "file_unique_id": msg.photo[-1].file_unique_id,
                   "caption": msg.caption or ""}
    elif msg.video:
        ad_data = {"type": "video", "file_id": msg.video.file_id,
                   "file_unique_id": msg.video.file_unique_id,
                   "caption": msg.caption or ""}
    elif msg.document:
        ad_data = {"type": "document", "file_id": msg.document.file_id,
                   "file_unique_id": msg.document.file_unique_id,
                   "caption": msg.caption or ""}
    elif msg.audio:
        ad_data = {"type": "audio", "file_id": msg.audio.file_id,
                   "file_unique_id": msg.audio.file_unique_id,
                   "caption": msg.caption or ""}
    elif msg.animation:
        ad_data = {"type": "animation", "file_id": msg.animation.file_id,
                   "file_unique_id": msg.animation.file_unique_id,
                   "caption": msg.caption or ""}
    elif msg.sticker:
        ad_data = {"type": "sticker", "file_id": msg.sticker.file_id,
                   "file_unique_id": msg.sticker.file_unique_id}
    elif msg.voice:
        ad_data = {"type": "voice", "file_id": msg.voice.file_id,
                   "file_unique_id": msg.voice.file_unique_id,
                   "caption": msg.caption or ""}
    elif msg.video_note:
        ad_data = {"type": "video_note", "file_id": msg.video_note.file_id,
                   "file_unique_id": msg.video_note.file_unique_id}
    elif msg.text:
        ad_data = {"type": "text", "text": msg.text}
    else:
        await msg.reply_text("Unsupported message type. Please try again.")
        await db.set_waiting_for_ad(user_id, True)
        return True

    if msg.forward_date and msg.forward_from and msg.forward_from.id == user_id:
        ad_data["from_saved"] = True

    await db.set_ad_message_data(user_id, ad_data)

    try:
        await msg.delete()
    except Exception:
        pass

    prompt = await db.get_prompt_message(user_id)
    if prompt:
        chat_id, msg_id = prompt
        text, keyboard = await _build_dashboard_text_and_keyboard(user_id)
        try:
            await context.bot.edit_message_caption(
                chat_id=chat_id, message_id=msg_id,
                caption=text, reply_markup=keyboard, parse_mode="HTML",
            )
            return True
        except Exception:
            pass
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id,
                text=text, reply_markup=keyboard, parse_mode="HTML",
            )
            return True
        except Exception:
            pass

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard")]])
    await context.bot.send_message(
        chat_id=msg.chat_id,
        text="<b>Ad message saved.</b>",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    return True


async def _build_dashboard_text_and_keyboard(user_id: int):
    from bot.handlers.dashboard import _build_dashboard_content
    return await _build_dashboard_content(user_id)


async def start_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    ad_data = await db.get_ad_message_data(user_id)
    if not ad_data:
        await query.answer("Ad message not set. Go to Set Ad Message first.", show_alert=True)
        return

    accounts = await db.get_accounts(user_id)
    if not accounts:
        await query.answer("No accounts added. Add at least one account first.", show_alert=True)
        return

    if await db.is_ads_running(user_id):
        await query.answer("Ads are already running!", show_alert=True)
        return

    await start_broadcast(user_id)
    interval = await db.get_interval(user_id)
    mins, secs = divmod(interval, 60)
    interval_label = f"{mins}m {secs}s" if mins else f"{secs}s"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard")]])
    await safe_edit(
        query,
        f"<b>Ads Started</b>\n\n"
        f"Broadcasting to all groups via <code>{len(accounts)}</code> account(s).\n"
        f"Interval: <code>{interval_label}</code>",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )


async def stop_ads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await stop_broadcast(user_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Dashboard", callback_data="dashboard")]])
    await safe_edit(
        query,
        "<b>Ads Stopped.</b>\n\nBroadcasting has been paused.",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )


async def toggle_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    current = await db.get_broadcast_mode(user_id)
    new_mode = "forward" if current == "direct" else "direct"
    await db.set_broadcast_mode(user_id, new_mode)
    mode_label = "Forward (from Saved Messages)" if new_mode == "forward" else "Direct (send content directly)"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Switch Again", callback_data="toggle_mode")],
        [InlineKeyboardButton("Dashboard", callback_data="dashboard")],
    ])
    await safe_edit(
        query,
        f"<b>Mode: {mode_label}</b>\n\n"
        "<b>Direct</b> — sends the stored message directly each time.\n"
        "<b>Forward</b> — forwards the latest message from each account's Saved Messages.",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )
