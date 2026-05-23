import asyncio
import io
import logging
import httpx
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatWriteForbidden, UserBannedInChannel
from bot.utils.session_manager import get_pyrogram_client
from bot.utils import db
import telegram
from bot.config import BOT_TOKEN

logger = logging.getLogger(__name__)

_active_tasks: dict[int, asyncio.Task] = {}


async def send_tracking(owner_id: int, text: str):
    from bot.config import TRACKING_BOT_TOKEN
    if not TRACKING_BOT_TOKEN:
        return
    try:
        bot = telegram.Bot(token=TRACKING_BOT_TOKEN)
        await bot.send_message(chat_id=owner_id, text=text, parse_mode="HTML")
    except Exception as e:
        logger.warning("send_tracking failed: %s", e)


async def _download_file(file_id: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
                                 params={"file_id": file_id})
            path = r.json()["result"]["file_path"]
            r2 = await client.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}")
            return r2.content
    except Exception as e:
        logger.warning("download_file failed [%s]: %s", file_id, e)
        return None


async def _send_ad_via_pyrogram(client: Client, chat_id: int, ad_data: dict):
    msg_type = ad_data.get("type")
    caption = ad_data.get("caption", "") or ""

    if msg_type == "text":
        await client.send_message(chat_id, ad_data["text"])

    elif msg_type == "forward":
        saved = await client.get_messages("me", limit=1)
        if saved and saved[0]:
            await client.forward_messages(chat_id, "me", saved[0].id)
        else:
            raise ValueError("No message in Saved Messages to forward")

    elif msg_type == "photo":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_photo(chat_id, io.BytesIO(data), caption=caption)
        else:
            raise ValueError("Could not download photo")

    elif msg_type == "video":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_video(chat_id, io.BytesIO(data), caption=caption)
        else:
            raise ValueError("Could not download video")

    elif msg_type == "document":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_document(chat_id, io.BytesIO(data), caption=caption)
        else:
            raise ValueError("Could not download document")

    elif msg_type == "audio":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_audio(chat_id, io.BytesIO(data), caption=caption)
        else:
            raise ValueError("Could not download audio")

    elif msg_type == "animation":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_animation(chat_id, io.BytesIO(data), caption=caption)
        else:
            raise ValueError("Could not download animation")

    elif msg_type == "sticker":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_sticker(chat_id, io.BytesIO(data))
        else:
            raise ValueError("Could not download sticker")

    elif msg_type == "voice":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_voice(chat_id, io.BytesIO(data), caption=caption)
        else:
            raise ValueError("Could not download voice")

    elif msg_type == "video_note":
        data = await _download_file(ad_data["file_id"])
        if data:
            await client.send_video_note(chat_id, io.BytesIO(data))
        else:
            raise ValueError("Could not download video note")

    else:
        await client.send_message(chat_id, caption or "Ad message")


def _group_link(group) -> str:
    username = getattr(group, "username", None)
    group_id = group.id
    if username:
        return f"https://t.me/{username}"
    if str(group_id).startswith("-100"):
        return f"https://t.me/c/{str(group_id)[4:]}"
    return ""


async def broadcast_for_user(owner_id: int):
    accounts = await db.get_accounts(owner_id)
    if not accounts:
        return

    ad_data = await db.get_ad_message_data(owner_id)
    mode = await db.get_broadcast_mode(owner_id)
    if mode == "forward":
        effective_ad = {"type": "forward"}
    else:
        effective_ad = ad_data or {"type": "text", "text": ""}

    account_reports = []

    for acc_num, acc in enumerate(accounts, 1):
        if not await db.is_ads_running(owner_id):
            break

        acc_success = 0
        acc_failed = 0
        group_details = []

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
                    group_id = group.id
                    group_title = group.title or str(group_id)
                    group_username = getattr(group, "username", None) or ""
                    group_link = _group_link(group)

                    try:
                        await _send_ad_via_pyrogram(client, group_id, effective_ad)
                        await db.log_broadcast(
                            owner_id, acc["phone"], acc_num,
                            group_id, group_title, group_username, True
                        )
                        acc_success += 1
                        group_details.append({
                            "title": group_title,
                            "username": group_username,
                            "link": group_link,
                            "id": group_id,
                            "ok": True,
                        })
                        await asyncio.sleep(3)

                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        try:
                            await _send_ad_via_pyrogram(client, group_id, effective_ad)
                            await db.log_broadcast(
                                owner_id, acc["phone"], acc_num,
                                group_id, group_title, group_username, True
                            )
                            acc_success += 1
                            group_details.append({
                                "title": group_title, "username": group_username,
                                "link": group_link, "id": group_id, "ok": True,
                            })
                        except Exception as ex:
                            await db.log_broadcast(
                                owner_id, acc["phone"], acc_num,
                                group_id, group_title, group_username, False, str(ex)
                            )
                            acc_failed += 1
                            group_details.append({
                                "title": group_title, "username": group_username,
                                "link": group_link, "id": group_id, "ok": False,
                                "err": str(ex)[:60],
                            })

                    except (ChatWriteForbidden, UserBannedInChannel) as e:
                        await db.log_broadcast(
                            owner_id, acc["phone"], acc_num,
                            group_id, group_title, group_username, False, str(e)
                        )
                        acc_failed += 1
                        group_details.append({
                            "title": group_title, "username": group_username,
                            "link": group_link, "id": group_id, "ok": False,
                            "err": "No write permission",
                        })

                    except Exception as e:
                        await db.log_broadcast(
                            owner_id, acc["phone"], acc_num,
                            group_id, group_title, group_username, False, str(e)
                        )
                        acc_failed += 1
                        group_details.append({
                            "title": group_title, "username": group_username,
                            "link": group_link, "id": group_id, "ok": False,
                            "err": str(e)[:60],
                        })

        except Exception as e:
            logger.error("Account %s error: %s", acc["phone"], e)
            await send_tracking(
                owner_id,
                f"<b>Account #{acc_num} Error</b>\n"
                f"Phone: <code>{acc['phone']}</code>\n"
                f"Error: {str(e)[:200]}",
            )
            continue

        account_reports.append({
            "num": acc_num,
            "phone": acc["phone"],
            "name": acc.get("name", acc["phone"]),
            "success": acc_success,
            "failed": acc_failed,
            "groups": group_details,
        })

    interval = await db.get_interval(owner_id)
    mins, secs = divmod(interval, 60)
    time_str = f"{mins}m {secs}s" if mins else f"{secs}s"

    for report in account_reports:
        lines = [
            f"<b>Account #{report['num']} — {report['name']}</b>",
            f"Phone: <code>{report['phone']}</code>",
            f"Sent: <code>{report['success']}</code>  |  Failed: <code>{report['failed']}</code>",
            f"Groups total: <code>{len(report['groups'])}</code>",
            "",
        ]
        for g in report["groups"]:
            status = "✓" if g["ok"] else "✗"
            name = g["title"][:40]
            link = g["link"]
            username_str = f"@{g['username']}" if g["username"] else ""
            id_str = str(g["id"])
            if link:
                lines.append(f"{status} <a href='{link}'>{name}</a> {username_str} [<code>{id_str}</code>]")
            else:
                lines.append(f"{status} {name} {username_str} [<code>{id_str}</code>]")
            if not g["ok"] and g.get("err"):
                lines.append(f"   <i>{g['err']}</i>")

        lines.append(f"\nNext cycle: <code>{time_str}</code>")
        msg = "\n".join(lines)

        if len(msg) > 4000:
            msg = msg[:3900] + "\n... (truncated)"

        await send_tracking(owner_id, msg)


async def start_broadcast(owner_id: int):
    await db.set_ads_running(owner_id, True)

    async def run():
        while await db.is_ads_running(owner_id):
            interval = await db.get_interval(owner_id)
            await broadcast_for_user(owner_id)
            await asyncio.sleep(interval)

    task = asyncio.create_task(run())
    _active_tasks[owner_id] = task


async def stop_broadcast(owner_id: int):
    await db.set_ads_running(owner_id, False)
    task = _active_tasks.pop(owner_id, None)
    if task and not task.done():
        task.cancel()
