from imports import *
from plugins.config import *
from plugins.script import *

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.premium = self.db.premium_users
        self.bot = self.db.clone_bots
        self.media = self.db.media_files
        self.batches = self.db.batches
        self.scheduled_deletes = self.db.scheduled_deletes

    # ---------------- USERS ----------------
    def new_user(self, id, name):
        return dict(id=id, name=name)

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    # ---------------- PREMIUM ----------------
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

    async def remove_premium_user(self, user_id: int):
        await self.premium.delete_one({"id": int(user_id)})

    async def get_premium_user(self, user_id: int):
        return await self.premium.find_one({"id": int(user_id)})

    async def is_premium(self, user_id: int, required_plan: str = "normal"):
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

    async def list_premium_users(self):
        cursor = self.premium.find({"expiry_time": {"$gt": datetime.utcnow()}})
        return [user async for user in cursor]

    # ---------------- CLONE ----------------
    async def add_clone_bot(self, bot_id, user_id, first_name, username, bot_token):
        add = {
            "bot_id": bot_id,
            "user_id": user_id,
            "name": first_name,
            "username": username,
            "token": bot_token,
            # Start Message
            "start_text": script.START_TXT,
            "start_photo": None,
            "caption": None,
            "button": [],
            # Channel Message
            "word_filter": False,
            "media_filter": False,
            "random_caption": False,
            "header": None,
            "footer": None,
            # Force Subscribe
            "force_subscribe": [],
            # Access Token
            "access_token": False,
            "at_shorten_link": None,
            "at_shorten_api": None,
            "at_validity": "24h",
            "at_renew_log": {},
            "at_tutorial": None,
            # Auto Post
            "auto_post": False,
            "ap_channel": None,
            "ap_image": None,
            "ap_sleep": "1h",
            "ap_mode": "single",
            # Premium User
            "premium_user": [],
            "pu_upi": None,
            # Auto Delete
            "auto_delete": False,
            "ad_time": "1h",
            "ad_msg": script.AD_TXT,
            # Forward Protect
            "forward_protect": False,
            # Moderators
            "moderators": [],
            # Status
            "banned_users": [],
            # Activate/Deactivate
            "active": True,
            "last_active": int(pytime.time())
        }
        await self.bot.insert_one(add)

    async def is_clone_exist(self, user_id):
        clone = await self.bot.find_one({"user_id": int(user_id)})
        return bool(clone)

    async def get_clone(self, bot_id):
        clone = await self.bot.find_one({"bot_id": int(bot_id)})
        return clone

    async def get_clones_by_user(self, user_id):
        clones = []
        user_id_int = int(user_id)
        cursor = self.bot.find({
            "$or": [
                {"user_id": {"$in": [user_id_int, str(user_id_int)]}},
                {"moderators": {"$in": [user_id_int, str(user_id_int)]}}
            ]
        })
        async for clone in cursor:
            if clone.get("active", True):
                clones.append(clone)
        return clones

    async def get_all_clone(self):
        return self.bot.find({})

    async def update_clone(self, bot_id, user_data: dict, raw=False):
        if raw:
            await self.bot.update_one({"bot_id": int(bot_id)}, user_data, upsert=True)
        else:
            await self.bot.update_one({"bot_id": int(bot_id)}, {"$set": user_data}, upsert=True)

    async def delete_clone(self, bot_id):
        await self.bot.delete_one({"bot_id": int(bot_id)})

    async def delete_clone_by_id(self, db_id):
        await self.bot.delete_one({"_id": ObjectId(db_id)})

    async def ban_user(self, bot_id, user_id):
        await self.bot.update_one({"bot_id": int(bot_id)}, {"$addToSet": {"banned_users": int(user_id)}})

    async def unban_user(self, bot_id, user_id):
        await self.bot.update_one({"bot_id": int(bot_id)}, {"$pull": {"banned_users": int(user_id)}})

    async def get_banned_users(self, bot_id):
        clone = await self.bot.find_one({"bot_id": int(bot_id)})
        return clone.get("banned_users", []) if clone else []

    async def is_user_banned(self, bot_id: int, user_id: int) -> bool:
        data = await self.bot.find_one({"bot_id": int(bot_id), "banned_users": int(user_id)}, {"_id": 1})
        return bool(data)

    # ---------------- MEDIA ----------------
    async def add_media(self, bot_id: int, file_id: str, caption: str, media_type: str, date):
        await self.media.update_one(
            {"bot_id": bot_id, "file_id": file_id},
            {"$setOnInsert": {
                "bot_id": bot_id,
                "file_id": file_id,
                "caption": caption or "",
                "media_type": media_type,
                "date": date,
                "posted": False
            }},
            upsert=True
        )

    async def is_media_exist(self, bot_id: int, file_id: str):
        media = await self.media.find_one({"bot_id": bot_id, "file_id": file_id})
        return bool(media)

    async def pop_random_unposted_media(self, bot_id: int):
        pipeline = [
            {"$match": {"bot_id": bot_id, "posted": False}},
            {"$sample": {"size": 1}}
        ]
        items = await self.media.aggregate(pipeline).to_list(length=1)
        if not items:
            return None

        item = items[0]
        await self.media.update_one(
            {"_id": item["_id"], "posted": False},
            {"$set": {"posted": True}}
        )
        return item

    async def mark_media_posted(self, bot_id: int, file_id: str):
        await self.media.update_one(
            {"bot_id": bot_id, "file_id": file_id},
            {"$set": {"posted": True}}
        )

    async def unmark_media_posted(self, bot_id: int, file_id: str):
        await self.media.update_one(
            {"bot_id": bot_id, "file_id": file_id},
            {"$set": {"posted": False}}
        )

    async def add_file(self, bot_id, file_id, file_name=None, file_size=None, caption=None, media_type="text"):
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
        return result.inserted_id

    async def get_file(self, db_file_id):
        try:
            return await self.media.find_one({"_id": ObjectId(db_file_id)})
        except:
            return None

    async def get_file_by_file_id(self, file_id: str, bot_id: int = None):
        query = {"file_id": file_id}
        if bot_id:
            query["bot_id"] = int(bot_id)
        return await self.media.find_one(query)

    async def get_all_clone_media(self, bot_id: int):
        return self.media.find({"bot_id": bot_id})

    async def get_all_media(self):
        return self.media.find({})

    async def delete_all_clone_media(self, bot_id: int):
        result = await self.media.delete_many({"bot_id": bot_id})
        return result.deleted_count

    async def delete_all_media(self):
        result = await self.media.delete_many({})
        return result.deleted_count

    async def reset_clone_posts(self, bot_id: int):
        result = await self.media.update_many(
            {"bot_id": bot_id},
            {"$set": {"posted": False}}
        )
        return result.modified_count

    # ---------------- BATCH ----------------
    async def add_batch(self, bot_id, file_ids: list, is_auto_post: bool = False):
        data = {
            "bot_id": int(bot_id),
            "file_ids": file_ids,
            "date": datetime.utcnow(),
            "is_auto_post": is_auto_post
        }
        result = await self.batches.insert_one(data)
        return str(result.inserted_id)

    async def get_batch(self, batch_id):
        return await self.batches.find_one({"_id": ObjectId(batch_id)})

    async def mark_all_batches_auto_post(self, bot_id: int):
        result = await self.batches.update_many(
            {"bot_id": int(bot_id)},
            {"$set": {"is_auto_post": True}}
        )
        return result.modified_count

    # ---------------- SCHEDULED DELETES ----------------
    async def add_scheduled_delete(self, chat_id, message_ids: list, notice_id, delete_at, reload_url=None):
        data = {
            "chat_id": chat_id,
            "message_ids": message_ids,
            "notice_id": notice_id,
            "delete_at": delete_at,
            "reload_url": reload_url
        }
        await self.scheduled_deletes.insert_one(data)

    async def get_all_scheduled_deletes(self):
        return await self.scheduled_deletes.find().to_list(length=None)

    async def delete_scheduled_deletes(self, message_ids: list):
        await self.scheduled_deletes.delete_many({"message_ids": {"$in": message_ids}})

db = Database(DB_URI, DB_NAME)

class CloneDatabase:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]

    # ---------------- USERS ----------------
    async def add_user(self, bot_id, user_id):
        user = {"user_id": int(user_id)}
        await self.db[str(bot_id)].insert_one(user)
    
    async def is_user_exist(self, bot_id, id):
        user = await self.db[str(bot_id)].find_one({"user_id": int(id)})
        return bool(user)

    async def get_all_users(self, bot_id):
        return self.db[str(bot_id)].find({})

    async def delete_user(self, bot_id, user_id):
        await self.db[str(bot_id)].delete_many({"user_id": int(user_id)})

    async def total_users_count(self, bot_id):
        count = await self.db[str(bot_id)].count_documents({})
        return count

    # ---------------- SETTING ----------------
    async def get_user(self, user_id):
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

    async def update_user_info(self, user_id, value:dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = { "$set": value }
        await self.db.users.update_one(myquery, newvalues)

clonedb = CloneDatabase(CLONE_DB_URI, CDB_NAME)
