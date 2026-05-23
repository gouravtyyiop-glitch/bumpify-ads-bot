import asyncio
import logging
import traceback
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.config import BOT_TOKEN, TRACKING_BOT_TOKEN
from bot.handlers.start import start_handler
from bot.handlers.dashboard import dashboard_handler
from bot.handlers.callbacks import callback_handler
from bot.utils import db
from web.app import run_web

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def error_handler(update: object, context):
    logger.error("Handler exception:\n%s", traceback.format_exc())


async def message_handler(update: Update, context):
    if not update.message:
        return
    from bot.handlers.interval import handle_interval_text
    if await handle_interval_text(update, context):
        return
    from bot.handlers.auto_reply import handle_auto_reply_text
    if await handle_auto_reply_text(update, context):
        return
    from bot.handlers.ads import handle_ad_message
    await handle_ad_message(update, context)


def build_main_app() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("dashboard", dashboard_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(
        (
            filters.TEXT
            | filters.PHOTO
            | filters.VIDEO
            | filters.Document.ALL
            | filters.AUDIO
            | filters.ANIMATION
            | filters.Sticker.ALL
            | filters.VOICE
            | filters.VIDEO_NOTE
        ) & ~filters.COMMAND,
        message_handler,
    ))
    app.add_error_handler(error_handler)
    return app


async def _start_tracking(tracking_app: Application):
    try:
        await tracking_app.initialize()
        await tracking_app.bot.delete_webhook(drop_pending_updates=True)
        await tracking_app.start()
        await tracking_app.updater.start_polling(
            allowed_updates=["message", "callback_query"],
            read_timeout=10,
            write_timeout=10,
            connect_timeout=10,
            pool_timeout=10,
        )
        logger.info("Tracking bot started")
        return True
    except Exception as e:
        logger.warning("Tracking bot failed to start (check TRACKING_BOT_TOKEN): %s", e)
        return False


async def _stop_tracking(tracking_app: Application, started: bool):
    if not started:
        return
    try:
        await tracking_app.updater.stop()
        await tracking_app.stop()
        await tracking_app.shutdown()
    except Exception:
        pass


async def main():
    await db.connect()
    logger.info("MongoDB connected")

    main_app = build_main_app()
    web_runner = await run_web()

    tracking_app = None
    tracking_started = False
    if TRACKING_BOT_TOKEN:
        from tracking_bot.handlers import build_tracking_app
        tracking_app = build_tracking_app()

    async with main_app:
        await main_app.bot.delete_webhook(drop_pending_updates=True)
        await main_app.start()
        await main_app.updater.start_polling(
            allowed_updates=["message", "callback_query", "edited_message"],
            read_timeout=10,
            write_timeout=10,
            connect_timeout=10,
            pool_timeout=10,
        )
        logger.info("Main bot started")

        if tracking_app:
            tracking_started = await _start_tracking(tracking_app)

        logger.info("All services running.")

        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            from bot.utils.auto_reply_manager import stop_all_auto_replies
            await stop_all_auto_replies()
            await main_app.updater.stop()
            await main_app.stop()
            if tracking_app:
                await _stop_tracking(tracking_app, tracking_started)
            await web_runner.cleanup()
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
