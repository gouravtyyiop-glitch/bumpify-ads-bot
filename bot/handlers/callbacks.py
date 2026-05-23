import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
from bot.utils.helpers import safe_edit
from bot.config import START_CAPTION, TRACKING_BOT_USERNAME, WEB_APP_URL

logger = logging.getLogger(__name__)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        logger.warning("query.answer failed: %s", e)

    data = query.data
    logger.info("CALLBACK: %s from %s", data, update.effective_user.id)

    try:
        if data == "dashboard":
            from bot.handlers.dashboard import dashboard_handler
            await dashboard_handler(update, context)

        elif data == "my_accounts":
            from bot.handlers.accounts import my_accounts_handler
            await my_accounts_handler(update, context)

        elif data == "delete_account":
            from bot.handlers.accounts import delete_account_handler
            await delete_account_handler(update, context)

        elif data.startswith("del_acc_"):
            from bot.handlers.accounts import confirm_delete_handler
            await confirm_delete_handler(update, context, data[len("del_acc_"):])

        elif data == "analytics":
            from bot.handlers.accounts import analytics_handler
            await analytics_handler(update, context)

        elif data == "set_ad":
            from bot.handlers.ads import set_ad_handler
            await set_ad_handler(update, context)

        elif data == "start_ads":
            from bot.handlers.ads import start_ads_handler
            await start_ads_handler(update, context)

        elif data == "stop_ads":
            from bot.handlers.ads import stop_ads_handler
            await stop_ads_handler(update, context)

        elif data == "toggle_mode":
            from bot.handlers.ads import toggle_mode_handler
            await toggle_mode_handler(update, context)

        elif data == "set_interval":
            from bot.handlers.interval import set_interval_handler
            await set_interval_handler(update, context)

        elif data.startswith("interval_"):
            val = data[len("interval_"):]
            if val == "custom":
                from bot.handlers.interval import interval_custom_handler
                await interval_custom_handler(update, context)
            else:
                from bot.handlers.interval import interval_preset_handler
                await interval_preset_handler(update, context, int(val))

        elif data == "faq":
            from bot.handlers.faq import faq_handler
            await faq_handler(update, context)

        elif data == "howto":
            from bot.handlers.faq import howto_handler
            await howto_handler(update, context)

        elif data == "home":
            await _home_handler(update, context)

        elif data == "add_account":
            await _add_account_fallback(update, context)

        elif data == "auto_reply":
            from bot.handlers.auto_reply import auto_reply_handler
            await auto_reply_handler(update, context)

        elif data == "toggle_auto_reply":
            from bot.handlers.auto_reply import toggle_auto_reply_handler
            await toggle_auto_reply_handler(update, context)

        elif data == "set_auto_reply_text":
            from bot.handlers.auto_reply import set_auto_reply_text_handler
            await set_auto_reply_text_handler(update, context)

    except Exception as e:
        logger.error("callback_handler error [%s]: %s", data, e, exc_info=True)
        try:
            await safe_edit(
                query,
                "<b>Something went wrong.</b>\nPlease try again.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Home", callback_data="home")]]),
                parse_mode="HTML",
                context=context,
            )
        except Exception:
            pass


async def _home_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = START_CAPTION
    if TRACKING_BOT_USERNAME:
        caption += (
            f"\n\n<b>Important:</b> Start @{TRACKING_BOT_USERNAME} first before running ads "
            "so it can send you broadcast analytics."
        )
    second_row = [InlineKeyboardButton("FAQ", callback_data="faq")]
    if WEB_APP_URL:
        second_row.append(InlineKeyboardButton("Web Panel", web_app=WebAppInfo(url=WEB_APP_URL)))
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Dashboard", callback_data="dashboard")],
        second_row,
        [InlineKeyboardButton("How To Use", callback_data="howto")],
    ])
    await safe_edit(query, caption, reply_markup=keyboard, parse_mode="HTML", context=context)


async def _add_account_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="dashboard")]])
    await safe_edit(
        query,
        "<b>Add Account</b>\n\n"
        "Set <code>WEB_APP_URL</code> in your environment to enable the web panel for adding accounts.",
        reply_markup=keyboard,
        parse_mode="HTML",
        context=context,
    )
