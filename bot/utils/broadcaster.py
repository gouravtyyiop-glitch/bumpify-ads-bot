import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatWriteForbidden, UserBannedInChannel
from bot.utils.session_manager import get_pyrogram_client
from bot.utils import db
from bot.config import ENCRYPTION_KEY, TRACKING_BOT_TOKEN
import telegram


_active_tasks: dict[int, asyncio.Task] = {}


async def send_tracking(owner_id: int, text: str):
    if not TRACKING_BOT_TOKEN:
        return
    try:
        bot = telegram.Bot(token=TRACKING_BOT_TOKEN)
        await bot.send_message(chat_id=owner_id, text=text, parse_mode="Markdown")
    except Exception:
        pass


async def broadcast_for_user(owner_id: int, ad_text: str, mode: str, tracking_chat_id: int):
    accounts = await db.get_accounts(owner_id)
    if not accounts:
        return

    total_success = 0
    total_failed = 0

    for acc in accounts:
        if not await db.is_ads_running(owner_id):
            break
        try:
            client = await get_pyrogram_client(acc["session"])
            async with client:
                groups = []
                async for dialog in client.get_dialogs():
                    if dialog.chat.type.name in ("GROUP", "SUPERGROUP"):
                        groups.append(dialog.chat)

                for group in groups:
                    if not await db.is_ads_running(owner_id):
                        break
                    try:
                        if mode == "forward":
                            saved = await client.get_messages("me", limit=1)
                            if saved:
                                await client.forward_messages(
                                    chat_id=group.id,
                                    from_chat_id="me",
                                    message_ids=saved[0].id,
                                )
                            else:
                                await client.send_message(group.id, ad_text)
                        else:
                            await client.send_message(group.id, ad_text)

                        await db.log_broadcast(owner_id, acc["phone"], str(group.id), True)
                        total_success += 1
                        await asyncio.sleep(2)

                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        try:
                            await client.send_message(group.id, ad_text)
                            await db.log_broadcast(owner_id, acc["phone"], str(group.id), True)
                            total_success += 1
                        except Exception as ex:
                            await db.log_broadcast(owner_id, acc["phone"], str(group.id), False, str(ex))
                            total_failed += 1

                    except (ChatWriteForbidden, UserBannedInChannel) as e:
                        await db.log_broadcast(owner_id, acc["phone"], str(group.id), False, str(e))
                        total_failed += 1

                    except Exception as e:
                        await db.log_broadcast(owner_id, acc["phone"], str(group.id), False, str(e))
                        total_failed += 1

        except Exception as e:
            await send_tracking(
                tracking_chat_id,
                f"⚠️ *Account Error*\n📱 `{acc['phone']}`\n❌ {str(e)[:200]}",
            )

    await send_tracking(
        tracking_chat_id,
        f"📊 *Broadcast Cycle Complete*\n"
        f"✅ Success: `{total_success}`\n"
        f"❌ Failed: `{total_failed}`\n"
        f"📱 Accounts Used: `{len(accounts)}`",
    )


async def start_broadcast(owner_id: int, interval: int = 300):
    await db.set_ads_running(owner_id, True)

    async def run():
        while await db.is_ads_running(owner_id):
            ad_text = await db.get_ad_text(owner_id)
            mode = await db.get_broadcast_mode(owner_id)
            if ad_text:
                await broadcast_for_user(owner_id, ad_text, mode, owner_id)
            await asyncio.sleep(interval)

    task = asyncio.create_task(run())
    _active_tasks[owner_id] = task


async def stop_broadcast(owner_id: int):
    await db.set_ads_running(owner_id, False)
    task = _active_tasks.get(owner_id)
    if task and not task.done():
        task.cancel()
    _active_tasks.pop(owner_id, None)
