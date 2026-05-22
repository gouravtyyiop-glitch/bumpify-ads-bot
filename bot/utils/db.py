from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import MONGODB_URL, DATABASE_NAME

_client = None
_db = None


def get_db():
    return _db


async def connect():
    global _client, _db
    _client = AsyncIOMotorClient(MONGODB_URL)
    _db = _client[DATABASE_NAME]
    await _db.users.create_index("user_id", unique=True)
    await _db.accounts.create_index([("owner_id", 1), ("phone", 1)])
    await _db.broadcast_logs.create_index("owner_id")


async def close():
    if _client:
        _client.close()


async def get_user(user_id: int) -> dict | None:
    return await get_db().users.find_one({"user_id": user_id})


async def upsert_user(user_id: int, data: dict):
    await get_db().users.update_one(
        {"user_id": user_id}, {"$set": data}, upsert=True
    )


async def set_ad_text(user_id: int, text: str):
    await upsert_user(user_id, {"ad_text": text, "ad_text_entities": []})


async def set_ad_message(user_id: int, text: str, entities: list):
    await upsert_user(user_id, {"ad_text": text, "ad_entities": entities})


async def get_ad_text(user_id: int) -> str | None:
    user = await get_user(user_id)
    return user.get("ad_text") if user else None


async def set_broadcast_mode(user_id: int, mode: str):
    await upsert_user(user_id, {"broadcast_mode": mode})


async def get_broadcast_mode(user_id: int) -> str:
    user = await get_user(user_id)
    if user:
        return user.get("broadcast_mode", "direct")
    return "direct"


async def set_ads_running(user_id: int, running: bool):
    await upsert_user(user_id, {"ads_running": running})


async def is_ads_running(user_id: int) -> bool:
    user = await get_user(user_id)
    return user.get("ads_running", False) if user else False


async def set_waiting_for_ad(user_id: int, value: bool):
    await upsert_user(user_id, {"waiting_for_ad": value})


async def is_waiting_for_ad(user_id: int) -> bool:
    user = await get_user(user_id)
    return user.get("waiting_for_ad", False) if user else False


async def add_account(owner_id: int, phone: str, session_encrypted: str, name: str):
    await get_db().accounts.update_one(
        {"owner_id": owner_id, "phone": phone},
        {"$set": {"session": session_encrypted, "name": name, "active": True}},
        upsert=True,
    )


async def get_accounts(owner_id: int) -> list:
    cursor = get_db().accounts.find({"owner_id": owner_id, "active": True})
    return await cursor.to_list(length=None)


async def remove_account(owner_id: int, phone: str):
    await get_db().accounts.update_one(
        {"owner_id": owner_id, "phone": phone}, {"$set": {"active": False}}
    )


async def log_broadcast(owner_id: int, account: str, group: str, success: bool, error: str = ""):
    await get_db().broadcast_logs.insert_one(
        {
            "owner_id": owner_id,
            "account": account,
            "group": group,
            "success": success,
            "error": error,
        }
    )


async def get_broadcast_stats(owner_id: int) -> dict:
    total = await get_db().broadcast_logs.count_documents({"owner_id": owner_id})
    success = await get_db().broadcast_logs.count_documents({"owner_id": owner_id, "success": True})
    failed = total - success
    return {"total": total, "success": success, "failed": failed}
