import logging
logger = logging.getLogger(__name__)


async def safe_edit(query, text: str, reply_markup=None, parse_mode: str = "HTML", context=None):
    kw = {"parse_mode": parse_mode}
    if reply_markup:
        kw["reply_markup"] = reply_markup

    msg = query.message

    if msg.text:
        try:
            await query.edit_message_text(text, **kw)
            return
        except Exception as e:
            logger.warning("edit_message_text failed: %s", e)
    else:
        try:
            await query.edit_message_caption(caption=text, **kw)
            return
        except Exception as e:
            logger.warning("edit_message_caption failed: %s", e)

    try:
        await msg.reply_text(text, quote=False, **kw)
    except Exception as e:
        logger.error("safe_edit reply_text fallback failed: %s", e)
