import asyncio
import io
import logging
import httpx
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, ChatWriteForbidden, UserBannedInChannel, SessionRevoked, AuthKeyUnregistered
from bot.utils.session_manager import get_pyrogram_client
from bot.utils import db
import telegram
from bot.config import BOT_TOKEN

logger = logging.getLogger(__name__)

_active_tasks: dict[int, asyncio.Task] = {}
_dl_semaphore = asyncio.Semaphore(8)
_acc_semaphore = asyncio.Semaphore(10)


async def send_logs(owner_id: int, text: str):
    from bot.config import LOGGER_BOT_TOKEN
    if not LOGGER_BOT_TOKEN:
        return
    try:
        bot = telegram.Bot(token=LOGGER_BOT_TOKEN)
        await bot.send_message(chat_id=owner_id, text=text, parse_mode="HTML")
    except Exception as e:
        logger.warning("send_logs failed: %s", e)


async def _download_file(file_id: str) -> bytes | None:
    async with _dl_semaphore:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
                    params={"file_id": file_id},
                )
                path = r.json()["result"]["file_path"]
                r2 = await client.get(
                    f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}"
                )
                return r2.content
        except Exception as e:
            logger.warning("download_file failed [%s]: %s", file_id, e)
            return None


async def _send_ad_via_pyrogram(client: Client, chat_id: int, ad_data: dict):
    msg_type = ad_data.get("type")
    caption = ad_data.get("caption", "") or ""

    if msg_type == "text":
        await client.send_message(chat_id, ad_data["text"], parse_mode=ParseMode.HTML)

    elif msg_type == "forward":
        msgs = await client.get_messages("me", limit=1)
        if msgs and msgs[0] and msgs[0].id:
            await client.forward_messages(chat_id, "me", msgs[0].id)
        else:
            raise ValueError("No message in Saved Messages to forward")

    elif msg_type == "photo":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download photo")
        await client.send_photo(chat_id, io.BytesIO(data),
                                caption=caption, parse_mode=ParseMode.HTML)

    elif msg_type == "video":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download video")
        await client.send_video(chat_id, io.BytesIO(data),
                                caption=caption, parse_mode=ParseMode.HTML)

    elif msg_type == "document":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download document")
        await client.send_document(chat_id, io.BytesIO(data),
                                   caption=caption, parse_mode=ParseMode.HTML)

    elif msg_type == "audio":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download audio")
        await client.send_audio(chat_id, io.BytesIO(data),
                                caption=caption, parse_mode=ParseMode.HTML)

    elif msg_type == "animation":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download animation")
        await client.send_animation(chat_id, io.BytesIO(data),
                                    caption=caption, parse_mode=ParseMode.HTML)

    elif msg_type == "sticker":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download sticker")
        await client.send_sticker(chat_id, io.BytesIO(data))

    elif msg_type == "voice":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download voice")
        await client.send_voice(chat_id, io.BytesIO(data),
                                caption=caption, parse_mode=ParseMode.HTML)

    elif msg_type == "video_note":
        data = await _download_file(ad_data["file_id"])
        if not data:
            raise ValueError("Could not download video note")
        await client.send_video_note(chat_id, io.BytesIO(data))

    else:
        txt = caption or ad_data.get("text", "")
        if txt:
            await client.send_message(chat_id, txt, parse_mode=ParseMode.HTML)


def _group_link(group) -> str:
    username = getattr(group, "username", None)
    gid = str(group.id)
    if username:
        return f"https://t.me/{username}"
    if gid.startswith("-100"):
        return f"https://t.me/c/{gid[4:]}"
    return ""


async def _process_account(owner_id: int, acc_num: int, acc: dict, effective_ad: dict) -> dict:
    report = {
        "num": acc_num,
        "phone": acc["phone"],
        "name": acc.get("name", acc["phone"]),
        "success": 0,
        "failed": 0,
        "groups": [],
        "error": None,
    }

    async with _acc_semaphore:
        try:
            client = await get_pyrogram_client(acc["session"])
            async with client:
                groups = []
                async for dialog in client.get_dialogs():
                    if dialog.chat.type.name in ("GROUP", "SUPERGROUP"):
                        groups.append(dialog.chat)

                group_sem = asyncio.Semaphore(3)

                async def send_to_group(group):
                    gid = group.id
                    gtitle = group.title or str(gid)
                    gusername = getattr(group, "username", None) or ""
                    glink = _group_link(group)

                    async with group_sem:
                        if not await db.is_ads_running(owner_id):
                            return
                        try:
                            await _send_ad_via_pyrogram(client, gid, effective_ad)
                            await db.log_broadcast(
                                owner_id, acc["phone"], acc_num,
                                gid, gtitle, gusername, True
                            )
                            report["success"] += 1
                            report["groups"].append({
                                "title": gtitle, "username": gusername,
                                "link": glink, "id": gid, "ok": True,
                            })
                            await asyncio.sleep(2)

                        except FloodWait as e:
                            await asyncio.sleep(min(e.value, 60))
                            try:
                                await _send_ad_via_pyrogram(client, gid, effective_ad)
                                await db.log_broadcast(
                                    owner_id, acc["phone"], acc_num,
                                    gid, gtitle, gusername, True
                                )
                                report["success"] += 1
                                report["groups"].append({
                                    "title": gtitle, "username": gusername,
                                    "link": glink, "id": gid, "ok": True,
                                })
                            except Exception as ex2:
                                await db.log_broadcast(
                                    owner_id, acc["phone"], acc_num,
                                    gid, gtitle, gusername, False, str(ex2)
                                )
                                report["failed"] += 1
                                report["groups"].append({
                                    "title": gtitle, "username": gusername,
                                    "link": glink, "id": gid, "ok": False,
                                    "err": str(ex2)[:60],
                                })

                        except (ChatWriteForbidden, UserBannedInChannel) as e:
                            await db.log_broadcast(
                                owner_id, acc["phone"], acc_num,
                                gid, gtitle, gusername, False, "No write permission"
                            )
                            report["failed"] += 1
                            report["groups"].append({
                                "title": gtitle, "username": gusername,
                                "link": glink, "id": gid, "ok": False,
                                "err": "No write permission",
                            })

                        except Exception as e:
                            await db.log_broadcast(
                                owner_id, acc["phone"], acc_num,
                                gid, gtitle, gusername, False, str(e)
                            )
                            report["failed"] += 1
                            report["groups"].append({
                                "title": gtitle, "username": gusername,
                                "link": glink, "id": gid, "ok": False,
                                "err": str(e)[:60],
                            })

                await asyncio.gather(*[send_to_group(g) for g in groups], return_exceptions=True)

        except (SessionRevoked, AuthKeyUnregistered) as e:
            report["error"] = "Session expired — account removed"
            await db.remove_account(owner_id, acc["phone"])
            await send_logs(
                owner_id,
                f"<b>Account #{acc_num} Session Expired</b>\n"
                f"Phone: <code>{acc['phone']}</code>\n"
                "The account has been automatically removed. Please re-add it.",
            )
        except Exception as e:
            report["error"] = str(e)[:200]
            await send_logs(
                owner_id,
                f"<b>Account #{acc_num} Error</b>\n"
                f"Phone: <code>{acc['phone']}</code>\n"
                f"Error: {str(e)[:200]}",
            )

    return report


async def broadcast_for_user(owner_id: int):
    accounts = await db.get_accounts(owner_id)
    if not accounts:
        return

    ad_data = await db.get_ad_message_data(owner_id)
    mode = await db.get_broadcast_mode(owner_id)
    effective_ad = {"type": "forward"} if mode == "forward" else (ad_data or {"type": "text", "text": ""})

    tasks = [
        _process_account(owner_id, i + 1, acc, effective_ad)
        for i, acc in enumerate(accounts)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    interval = await db.get_interval(owner_id)
    mins, secs = divmod(interval, 60)
    time_str = f"{mins}m {secs}s" if mins else f"{secs}s"

    for result in results:
        if isinstance(result, Exception):
            continue
        report = result

        if report.get("error") and not report["groups"]:
            continue

        lines = [
            f"<b>Account #{report['num']} — {report['name']}</b>",
            f"<code>{report['phone']}</code>",
            f"",
            f"Sent: <b>{report['success']}</b>  |  Failed: <b>{report['failed']}</b>  |  Total: <b>{len(report['groups'])}</b>",
            f"",
        ]

        shown = 0
        for g in report["groups"]:
            if shown >= 50:
                remaining = len(report["groups"]) - shown
                lines.append(f"<i>... and {remaining} more groups</i>")
                break
            mark = "✓" if g["ok"] else "✗"
            name = g["title"][:35]
            uname = f"@{g['username']}" if g["username"] else ""
            gid_str = str(g["id"])
            if g["link"]:
                lines.append(f"{mark} <a href='{g['link']}'>{name}</a> {uname} <code>{gid_str}</code>")
            else:
                lines.append(f"{mark} {name} {uname} <code>{gid_str}</code>")
            if not g["ok"] and g.get("err"):
                lines.append(f"   <i>{g['err']}</i>")
            shown += 1

        lines.append(f"\nNext cycle: <code>{time_str}</code>")
        msg = "\n".join(lines)
        if len(msg) > 4096:
            msg = msg[:4000] + "\n<i>... truncated</i>"

        await send_logs(owner_id, msg)


async def start_broadcast(owner_id: int):
    await db.set_ads_running(owner_id, True)

    async def run():
        while await db.is_ads_running(owner_id):
            interval = await db.get_interval(owner_id)
            await broadcast_for_user(owner_id)
            if await db.is_ads_running(owner_id):
                await asyncio.sleep(interval)

    task = asyncio.create_task(run())
    _active_tasks[owner_id] = task


async def stop_broadcast(owner_id: int):
    await db.set_ads_running(owner_id, False)
    task = _active_tasks.pop(owner_id, None)
    if task and not task.done():
        task.cancel()
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=2)
        except Exception:
            pass
