import logging
logger = logging.getLogger(__name__)


async def safe_edit(query, text: str, reply_markup=None, parse_mode: str = "HTML", context=None):
    kwargs = {"parse_mode": parse_mode}
    if reply_markup:
        kwargs["reply_markup"] = reply_markup

    msg = query.message

    if msg.text:
        try:
            await query.edit_message_text(text, **kwargs)
            return
        except Exception as e:
            logger.warning("edit_message_text failed: %s", e)

    try:
        await msg.delete()
    except Exception as e:
        logger.warning("delete failed: %s", e)

    try:
        if context:
            await context.bot.send_message(chat_id=msg.chat_id, text=text, **kwargs)
        else:
            await msg.reply_text(text, quote=False, **kwargs)
    except Exception as e:
        logger.error("safe_edit fallback failed: %s", e)
