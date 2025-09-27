# database.py
import motor.motor_asyncio
import logging
import time
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Any, Dict, List, Optional
from plugins.config import *
from plugins.script import script
from pymongo import InsertOne, UpdateOne, DeleteOne

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SimpleTTLCache:
    """Tiny in-memory TTL cache. Not distributed — used for hot, short-lived reads."""
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def set(self, key: str, value: Any, ttl: int = 60):
        self._store[key] = value
        self._expiry[key] = time.time() + ttl

    def get(self, key: str):
        exp = self._expiry.get(key)
        if exp is None:
            return None
        if time.time() > exp:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return None
        return self._store.get(key)

    def delete(self, key: str):
        self._store.pop(key, None)
        self._expiry.pop(key, None)


class Database:
    def __init__(self, uri: str, database_name: str,
                 max_pool_size: int = 100,
                 min_pool_size: int = 5,
                 server_selection_timeout_ms: int = 5000):
        # tuned connection pool + timeouts
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            uri,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            serverSelectionTimeoutMS=server_selection_timeout_ms,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000
        )
        self.db = self._client[database_name]
        # collections
        self.col = self.db.users
        self.premium = self.db.premium_users
        self.bot = self.db.clone_bots
        self.settings = self.db.bot_settings
        self.media = self.db.media_files
        self.batches = self.db.batches

        # small in-memory cache for hot reads (bot settings, banned lists etc.)
        self._cache = SimpleTTLCache()

    # ---------------- Indexes ----------------
    async def ensure_indexes(self):
        """Create recommended indexes. Call once on startup."""
        logger.info("Ensuring database indexes...")
        try:
            await self.col.create_index("id", unique=True, background=True)
            await self.premium.create_index("id", unique=True, background=True)
            await self.premium.create_index("expiry_time", background=True)
            await self.bot.create_index("bot_id", unique=True, background=True)
            await self.bot.create_index("user_id", background=True)
            await self.bot.create_index("moderators", background=True)
            await self.bot.create_index("last_active", background=True)

            # ✅ Partial index prevents duplicate null values
            await self.media.create_index(
                [("bot_id", 1), ("file_id", 1)],
                unique=True,
                background=True,
                partialFilterExpression={"file_id": {"$exists": True, "$ne": None}}
            )
            await self.media.create_index("posted", background=True)
            await self.media.create_index("date", background=True)

            await self.batches.create_index("bot_id", background=True)
            logger.info("Indexes ensured.")
        except Exception as e:
            logger.exception("Error ensuring indexes: %s", e)

    # ---------------- USERS ----------------
    def new_user(self, id: int, name: str) -> dict:
        return {"id": int(id), "name": name}

    async def add_user(self, id: int, name: str):
        user = self.new_user(id, name)
        try:
            await self.col.insert_one(user)
        except Exception:
            # Ignore duplicates or insertion errors
            pass

    async def is_user_exist(self, id: int) -> bool:
        # faster existence check with count_documents limit=1
        try:
            return await self.col.count_documents({"id": int(id)}, limit=1) > 0
        except Exception:
            return False

    async def total_users_count(self) -> int:
        return await self.col.count_documents({})

    async def get_all_users(self, limit: Optional[int] = None):
        cursor = self.col.find({}, projection={"_id": 1, "id": 1, "name": 1})
        # return cursor to be iterated by caller; if caller wants list, they should call to_list
        if limit:
            return await cursor.to_list(length=limit)
        return cursor

    async def delete_user(self, user_id: int):
        await self.col.delete_many({"id": int(user_id)})

    # ---------------- PREMIUM USERS ----------------
    async def add_premium_user(self, user_id: int, days: int, plan_type: str = "normal"):
        expiry_time = datetime.utcnow() + timedelta(days=days)
        await self.premium.update_one(
            {"id": int(user_id)},
            {"$set": {
                "id": int(user_id),
                "plan_type": plan_type,
                "expiry_time": expiry_time
            }},
            upsert=True
        )
        # refresh cache for this user if present
        self._cache.delete(f"premium:{user_id}")

    async def remove_premium_user(self, user_id: int):
        await self.premium.delete_one({"id": int(user_id)})
        self._cache.delete(f"premium:{user_id}")

    async def get_premium_user(self, user_id: int) -> Optional[dict]:
        # cache short-lived premium lookups
        key = f"premium:{user_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        user = await self.premium.find_one({"id": int(user_id)})
        if user:
            self._cache.set(key, user, ttl=30)
        return user

    async def is_premium(self, user_id: int, required_plan: str = "normal") -> bool:
        user = await self.get_premium_user(user_id)
        if not user:
            return False

        expiry = user.get("expiry_time")
        if not expiry or expiry < datetime.utcnow():
            return False

        if required_plan == "ultra":
            return user.get("plan_type") in ["ultra", "vip"]
        elif required_plan == "vip":
            return user.get("plan_type") == "vip"

        return True

    async def list_premium_users(self, limit: Optional[int] = None) -> List[dict]:
        cursor = self.premium.find({"expiry_time": {"$gt": datetime.utcnow()}}, projection={"_id": 1, "id": 1, "plan_type": 1, "expiry_time": 1})
        return await cursor.to_list(length=limit or 1000)

    # ---------------- CLONE ----------------
    async def add_clone_bot(self, bot_id, user_id, first_name, username, bot_token):
        bot_id_int = int(bot_id)
        existing_clone = await self.bot.find_one({"bot_id": bot_id_int}, projection={"bot_id": 1})
        reset_common = {
            'user_id': int(user_id),
            'name': first_name,
            'username': username,
            'token': bot_token,
            # Start Message
            'wlc': script.START_TXT,
            'pics': None,
            'caption': None,
            'button': [],
            # Channel Message
            'word_filter': False,
            'media_filter': False,
            'random_captiom': False,
            'header': None,
            'footer': None,
            # Force Subscribe
            'force_subscribe': [],
            # Access Token
            'access_token': False,
            'shorten_link': None,
            'shorten_api': None,
            'access_token_validity': '24h',
            'access_token_renew_log': {},
            'access_token_tutorial': None,
            # Auto Post
            'auto_post': False,
            'auto_post_channel': None,
            'auto_post_image': None,
            'auto_post_sleep': '1h',
            'auto_post_mode': 'single',
            # Premium User
            'premium_upi': None,
            'premium_user': [],
            # Auto Delete
            'auto_delete': False,
            'auto_delete_time': '1h',
            'auto_delete_msg': script.AD_TXT,
            # Forward Protect
            'forward_protect': False,
            # Moderators
            'moderators': [],
            # Activate/Deactivate
            'active': True,
            'last_active': int(time.time())
        }

        if existing_clone:
            # maintain existing status fields but reset config
            await self.bot.update_one({'bot_id': bot_id_int}, {'$set': reset_common})
        else:
            add = {
                'is_bot': True,
                'bot_id': bot_id_int,
                **reset_common,
                # Status
                'users_count': 0,
                'banned_users': [],
                'storage_used': 0,
                'storage_limit': 536870912,  # 512 MB default
            }
            await self.bot.insert_one(add)

        # invalidate cached bot info
        self._cache.delete(f"bot:{bot_id_int}")

    async def is_clone_exist(self, user_id: int) -> bool:
        # check quickly with indexed field
        return await self.bot.count_documents({"user_id": int(user_id)}, limit=1) > 0

    async def get_clones_by_user(self, user_id: int) -> List[dict]:
        user_id_int = int(user_id)
        cursor = self.bot.find({
            "$or": [
                {"user_id": {"$in": [user_id_int, str(user_id_int)]}},
                {"moderators": {"$in": [user_id_int, str(user_id_int)]}}
            ]
        }, projection={"_id": 1, "bot_id": 1, "user_id": 1, "name": 1, "active": 1})
        raw = await cursor.to_list(length=1000)
        # filter active clones
        return [c for c in raw if c.get("active", True)]

    async def get_clone_by_id(self, bot_id: int) -> Optional[dict]:
        key = f"bot:{bot_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        bot_data = await self.bot.find_one({"bot_id": int(bot_id)})
        if bot_data:
            self._cache.set(key, bot_data, ttl=30)
        return bot_data

    async def update_clone(self, bot_id: int, user_data: dict, raw: bool = False):
        if raw:
            await self.bot.update_one({'bot_id': int(bot_id)}, user_data, upsert=True)
        else:
            await self.bot.update_one({'bot_id': int(bot_id)}, {'$set': user_data}, upsert=True)
        self._cache.delete(f"bot:{int(bot_id)}")

    async def delete_clone(self, bot_id: int):
        await self.bot.delete_one({'bot_id': int(bot_id)})
        self._cache.delete(f"bot:{int(bot_id)}")

    async def delete_clone_by_id(self, db_id: str):
        await self.bot.delete_one({'_id': ObjectId(db_id)})

    async def get_bot(self, bot_id: int) -> Optional[dict]:
        return await self.get_clone_by_id(bot_id)

    async def update_bot(self, bot_id: int, bot_data: dict):
        await self.update_clone(bot_id, bot_data)

    async def get_all_bots(self, limit: Optional[int] = None):
        cursor = self.bot.find({}, projection={"_id": 1, "bot_id": 1, "user_id": 1, "active": 1})
        if limit:
            return await cursor.to_list(length=limit)
        return cursor

    async def increment_users_count(self, bot_id: int, amount: int = 1):
        await self.bot.update_one({'bot_id': int(bot_id)}, {'$inc': {'users_count': int(amount)}})
        self._cache.delete(f"bot:{int(bot_id)}")

    async def add_storage_used(self, bot_id: int, size: int):
        await self.bot.update_one({'bot_id': int(bot_id)}, {'$inc': {'storage_used': int(size)}})
        self._cache.delete(f"bot:{int(bot_id)}")

    async def ban_user(self, bot_id: int, user_id: int):
        await self.bot.update_one({'bot_id': int(bot_id)}, {'$addToSet': {'banned_users': int(user_id)}})
        self._cache.delete(f"bot:{int(bot_id)}")

    async def unban_user(self, bot_id: int, user_id: int):
        await self.bot.update_one({'bot_id': int(bot_id)}, {'$pull': {'banned_users': int(user_id)}})
        self._cache.delete(f"bot:{int(bot_id)}")

    async def get_banned_users(self, bot_id: int) -> List[int]:
        # return from cache if present
        key = f"banned:{bot_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        clone = await self.bot.find_one({'bot_id': int(bot_id)}, projection={"banned_users": 1})
        banned = clone.get("banned_users", []) if clone else []
        self._cache.set(key, banned, ttl=30)
        return banned

    # ---------------- MEDIA ----------------
    async def add_media(self, bot_id: int, file_id: str, caption: str, media_type: str, date: datetime):
        try:
            await self.media.update_one(
                {"bot_id": int(bot_id), "file_id": file_id},
                {"$setOnInsert": {
                    "bot_id": int(bot_id),
                    "file_id": file_id,
                    "caption": caption or "",
                    "media_type": media_type,
                    "date": date,
                    "posted": False
                }},
                upsert=True
            )
        except Exception:
            # unique constraint or other race — ignore safely
            pass

    async def is_media_exist(self, bot_id: int, file_id: str) -> bool:
        return await self.media.count_documents({"bot_id": int(bot_id), "file_id": file_id}, limit=1) > 0

    async def pop_random_unposted_media(self, bot_id: int) -> Optional[dict]:
        # Use aggregation sample; small race handled by update filter
        pipeline = [
            {"$match": {"bot_id": int(bot_id), "posted": False}},
            {"$sample": {"size": 1}}
        ]
        items = await self.media.aggregate(pipeline).to_list(length=1)
        if not items:
            return None
        item = items[0]
        # mark posted only if still unposted (atomic)
        res = await self.media.update_one({"_id": item["_id"], "posted": False}, {"$set": {"posted": True}})
        if res.modified_count == 0:
            # someone else took it; return None so caller can retry
            return None
        return item

    async def mark_media_posted(self, bot_id: int, file_id: str):
        await self.media.update_one({"bot_id": int(bot_id), "file_id": file_id}, {"$set": {"posted": True}})

    async def unmark_media_posted(self, bot_id: int, file_id: str):
        await self.media.update_one({"bot_id": int(bot_id), "file_id": file_id}, {"$set": {"posted": False}})

    async def add_file(self, bot_id: int, file_id: str, file_name: Optional[str] = None,
                       file_size: Optional[int] = None, caption: Optional[str] = None, media_type: str = "text"):
        data = {
            "bot_id": int(bot_id),
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "caption": caption,
            "media_type": media_type,
            "date": datetime.utcnow()
        }
        result = await self.media.insert_one(data)
        return str(result.inserted_id)

    async def get_file(self, db_file_id: str) -> Optional[dict]:
        try:
            return await self.media.find_one({"_id": ObjectId(db_file_id)})
        except Exception:
            return None

    async def get_file_by_file_id(self, file_id: str, bot_id: int = None) -> Optional[dict]:
        query = {"file_id": file_id}
        if bot_id:
            query["bot_id"] = int(bot_id)
        return await self.media.find_one(query, projection={"_id": 1, "file_id": 1, "bot_id": 1, "file_name": 1, "file_size": 1, "date": 1})

    async def get_all_clone_media(self, bot_id: int, limit: Optional[int] = None):
        cursor = self.media.find({"bot_id": int(bot_id)}, projection={"_id": 1, "file_id": 1, "posted": 1, "date": 1})
        if limit:
            return await cursor.to_list(length=limit)
        return cursor

    async def get_all_media(self, limit: Optional[int] = None):
        cursor = self.media.find({}, projection={"_id": 1, "file_id": 1, "bot_id": 1})
        if limit:
            return await cursor.to_list(length=limit)
        return cursor

    async def delete_all_clone_media(self, bot_id: int) -> int:
        result = await self.media.delete_many({"bot_id": int(bot_id)})
        return result.deleted_count

    async def delete_all_media(self) -> int:
        result = await self.media.delete_many({})
        return result.deleted_count

    async def reset_clone_posts(self, bot_id: int) -> int:
        result = await self.media.update_many({"bot_id": int(bot_id)}, {"$set": {"posted": False}})
        return result.modified_count

    # ---------------- BATCH ----------------
    async def add_batch(self, bot_id: int, file_ids: List[str], is_auto_post: bool = False) -> str:
        data = {
            "bot_id": int(bot_id),
            "file_ids": file_ids,
            "date": datetime.utcnow(),
            "is_auto_post": is_auto_post
        }
        result = await self.batches.insert_one(data)
        return str(result.inserted_id)

    async def get_batch(self, batch_id: str) -> Optional[dict]:
        try:
            return await self.batches.find_one({"_id": ObjectId(batch_id)})
        except Exception:
            return None

    async def mark_all_batches_auto_post(self, bot_id: int) -> int:
        result = await self.batches.update_many({"bot_id": int(bot_id)}, {"$set": {"is_auto_post": True}})
        return result.modified_count

    # ---------------- BULK HELPERS ----------------
    async def bulk_insert_media(self, docs: List[dict], ordered: bool = False):
        if not docs:
            return
        requests = [InsertOne(doc) for doc in docs]
        try:
            await self.media.bulk_write(requests, ordered=ordered)
        except Exception:
            # ignore individual duplicate key errors/time issues
            pass

    async def bulk_update_bot_stats(self, ops: List[dict], ordered: bool = False):
        """
        ops: list of dicts like {"filter": {...}, "update": {...}}
        """
        if not ops:
            return
        requests = [UpdateOne(op["filter"], op["update"], upsert=op.get("upsert", False)) for op in ops]
        try:
            await self.bot.bulk_write(requests, ordered=ordered)
        except Exception:
            logger.exception("Bulk bot stats update failed")

    # ---------------- CLEANUP / MAINTENANCE ----------------
    async def cleanup_expired_premiums(self):
        """Remove expired premium docs to keep collection small."""
        result = await self.premium.delete_many({"expiry_time": {"$lt": datetime.utcnow()}})
        return result.deleted_count

    async def cleanup_old_media(self, older_than_days: int = 90):
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        result = await self.media.delete_many({"date": {"$lt": cutoff}})
        return result.deleted_count

    # ---------------- SHUTDOWN / UTIL ----------------
    async def close(self):
        try:
            self._client.close()
        except Exception:
            pass


# singletons for import convenience
db = Database(DB_URI, DB_NAME)


# ---------- Clone Database (per-bot collections) ----------
class CloneDatabase:
    def __init__(self, uri: str, database_name: str,
                 max_pool_size: int = 50, min_pool_size: int = 1):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            uri,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            serverSelectionTimeoutMS=5000
        )
        self.db = self._client[database_name]
        # small cache
        self._cache = SimpleTTLCache()

    async def add_user(self, bot_id: int, user_id: int):
        user = {'user_id': int(user_id)}
        try:
            await self.db[str(bot_id)].insert_one(user)
        except Exception:
            pass

    async def is_user_exist(self, bot_id: int, id: int) -> bool:
        return await self.db[str(bot_id)].count_documents({'user_id': int(id)}, limit=1) > 0

    async def total_users_count(self, bot_id: int) -> int:
        return await self.db[str(bot_id)].count_documents({})

    async def get_all_users(self, bot_id: int, limit: Optional[int] = None):
        cursor = self.db[str(bot_id)].find({}, projection={"_id": 1, "user_id": 1})
        if limit:
            return await cursor.to_list(length=limit)
        return cursor

    async def delete_user(self, bot_id: int, user_id: int):
        await self.db[str(bot_id)].delete_many({'user_id': int(user_id)})

    async def get_user(self, user_id: int):
        # personal settings stored under "users" collection inside the cloned DB
        user_id = int(user_id)
        user = await self.db.users.find_one({"user_id": user_id})
        if not user:
            res = {
                "user_id": user_id,
                "shortener_api": None,
                "base_site": None,
            }
            await self.db.users.insert_one(res)
            user = await self.db.users.find_one({"user_id": user_id})
        return user

    async def update_user_info(self, user_id: int, value: dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        await self.db.users.update_one(myquery, newvalues)


clonedb = CloneDatabase(CLONE_DB_URI, CDB_NAME)


# ---------- JoinReqs helper ----------
class JoinReqs:
    def __init__(self):
        if DB_URI:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
            self.db = self.client["JoinReqs"]
            self.col = self.db[str(AUTH_CHANNEL)]
        else:
            self.client = None
            self.db = None
            self.col = None

    def isActive(self):
        return self.client is not None

    async def add_user(self, user_id: int, first_name: str, username: str, date: datetime):
        try:
            await self.col.insert_one({"_id": int(user_id), "user_id": int(user_id),
                                      "first_name": first_name, "username": username, "date": date})
        except Exception:
            pass

    async def get_user(self, user_id: int):
        return await self.col.find_one({"user_id": int(user_id)})

    async def get_all_users(self):
        return await self.col.find().to_list(None)

    async def delete_user(self, user_id: int):
        await self.col.delete_one({"user_id": int(user_id)})

    async def delete_all_users(self):
        await self.col.delete_many({})

    async def get_all_users_count(self):
        return await self.col.count_documents({})


# instantiate a JoinReqs helper
joinreqs = JoinReqs()