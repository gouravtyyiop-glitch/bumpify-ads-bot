from telegram import InlineKeyboardMarkup


async def safe_edit(query, text: str, reply_markup: InlineKeyboardMarkup = None, parse_mode: str = "Markdown"):
    kwargs = {"parse_mode": parse_mode}
    if reply_markup:
        kwargs["reply_markup"] = reply_markup
    try:
        await query.edit_message_text(text, **kwargs)
        return
    except Exception:
        pass
    try:
        await query.edit_message_caption(caption=text, **kwargs)
        return
    except Exception:
        pass
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.message.chat.send_message(text, **kwargs)
