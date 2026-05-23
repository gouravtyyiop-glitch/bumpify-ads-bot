import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.config import BOT_TOKEN
from bot.handlers.start import start_handler
from bot.handlers.dashboard import dashboard_handler
from bot.handlers.callbacks import callback_handler
from bot.utils import db
from tracking_bot.handlers import build_tracking_app
from web.app import run_web

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def message_handler(update, context):
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
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )
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
    return app


async def run_bot(app: Application):
    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query", "edited_message"],
    )
    logging.info("Main bot started")


async def run_tracking(app: Application):
    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )
    logging.info("Tracking bot started")


async def main():
    await db.connect()
    logging.info("MongoDB connected")

    main_app = build_main_app()
    tracking_app = build_tracking_app()
    web_runner = await run_web()

    await run_bot(main_app)
    await run_tracking(tracking_app)

    logging.info("All services running. Press Ctrl+C to stop.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await main_app.updater.stop()
        await main_app.stop()
        await main_app.shutdown()
        await tracking_app.updater.stop()
        await tracking_app.stop()
        await tracking_app.shutdown()
        await web_runner.cleanup()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
