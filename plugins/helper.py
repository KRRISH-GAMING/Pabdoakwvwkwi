import asyncio, re, random, aiohttp, requests, string
from datetime import *
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from pyrogram.errors.exceptions.bad_request_400 import *
from plugins.config import *
from plugins.database import *
from plugins.script import *

_clone_clients = {}
CLONE_ME = {}
TOKENS = {}
VERIFIED = {}

def set_client(bot_id: int, client):
    _clone_clients[int(bot_id)] = client

def get_client(bot_id: int):
    return _clone_clients.get(int(bot_id))

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

async def is_subscribedx(client, query):
    if REQUEST_TO_JOIN_MODE == True and JoinReqs().isActive():
        try:
            user = await JoinReqs().get_user(query.from_user.id)
            if user and user["user_id"] == query.from_user.id:
                return True
            else:
                try:
                    user_data = await client.get_chat_member(AUTH_CHANNEL, query.from_user.id)
                except UserNotParticipant:
                    pass
                except Exception as e:
                    logger.exception(e)
                else:
                    if user_data.status != enums.ChatMemberStatus.BANNED:
                        return True
        except Exception as e:
            logger.exception(e)
            return False
    else:
        try:
            user = await client.get_chat_member(AUTH_CHANNEL, query.from_user.id)
        except UserNotParticipant:
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if user.status != enums.ChatMemberStatus.BANNED:
                return True
        return False

async def broadcast_messagesx(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        return False, f"Error: {str(e)}"

def broadcast_progress_barx(done: int, total: int) -> str:
    try:
        progress = done / total if total > 0 else 0
        filled = int(progress * 20)
        empty = 20 - filled
        bar_str = "█" * filled + "░" * empty
        return f"[{bar_str}] {done}/{total}"
    except Exception as e:
        return f"[Error building bar: {e}] {done}/{total}"

async def get_me_safe(client):
    if client in CLONE_ME and CLONE_ME[client]:
        return CLONE_ME[client]

    while True:
        try:
            me = await client.get_me()
            CLONE_ME[client] = me
            return me
        except FloodWait as e:
            print(f"⏳ FloodWait: waiting {e.value}s for get_me()...")
            await asyncio.sleep(e.value)
        except Exception as ex:
            print(f"⚠️ get_me() failed: {ex}")
            return None

def parse_time(value: str) -> int:
    if not value:
        return 3600

    value = str(value).strip().lower()
    if value.endswith("s"):
        return int(value[:-1])
    elif value.endswith("m"):
        return int(value[:-1]) * 60
    elif value.endswith("h"):
        return int(value[:-1]) * 3600
    elif value.endswith("d"):
        return int(value[:-1]) * 86400
    else:
        return int(value) * 3600

async def is_subscribedy(client, user_id: int, bot_id: int):
    clone = await db.get_bot(bot_id)
    if not clone:
        return True

    fsub_data = clone.get("force_subscribe", [])
    if not fsub_data:
        return True

    for item in fsub_data:
        channel_id = int(item["channel"])

        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [
                enums.ChatMemberStatus.MEMBER,
                enums.ChatMemberStatus.ADMINISTRATOR,
                enums.ChatMemberStatus.OWNER
            ]:
                continue
            else:
                return False

        except UserNotParticipant:
            return False

        except Exception as e:
            print(f"⚠️ Clone is_subscribed Error {channel_id}: {e}")
            return False

    return True

async def get_verify_shorted_link(client, link):
    me = await get_me_safe(client)
    if not me:
        return

    clone = await db.get_bot(me.id)
    if not clone:
        return link

    shortlink_url = clone.get("at_shorten_link", None)
    shortlink_api = clone.get("at_shorten_api", None)

    if shortlink_url and shortlink_api:
        url = f"https://{shortlink_url}/api"
        params = {"api": shortlink_api, "url": link}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, ssl=False) as response:
                    text = await response.text()

                    try:
                        data = await response.json(content_type=None)
                    except Exception:
                        print(f"⚠️ API did not return JSON, got: {text[:200]}")
                        return link

                    if "shortenedUrl" in data:
                        return data["shortenedUrl"]
                    if "shortened" in data:
                        return data["shortened"]

                    print(f"⚠️ Unexpected JSON response: {data}")
                    return link
        except Exception as e:
            print(f"⚠️ Clone Shortener Error: {e}")
            print(traceback.format_exc())
            return link

    return link

async def check_token(client, userid, token):
    userid = int(userid)
    if userid in TOKENS:
        return token in TOKENS[userid] and TOKENS[userid][token] is False
    return False

async def get_token(client, userid, base_link):
    user = await client.get_users(userid)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{base_link}VERIFY-{user.id}-{token}"
    return await get_verify_shorted_link(client, link)

async def verify_user(client, userid, token):
    userid = int(userid)
    if userid in TOKENS and token in TOKENS[userid]:
        TOKENS[userid][token] = True

    me = await get_me_safe(client)
    if not me:
        return

    clone = await db.get_bot(me.id)
    if not clone:
        return

    validity_hours = parse_time(clone.get("at_validity", "24h"))
    VERIFIED[userid] = datetime.now() + timedelta(seconds=validity_hours)

    today = datetime.now().strftime("%Y-%m-%d")
    renew_log = clone.get("at_renew_log", {})
    renew_log[today] = renew_log.get(today, 0) + 1

    await db.update_bot(me.id, {"at_renew_log": renew_log})

async def check_verification(client, userid):
    userid = int(userid)
    expiry = VERIFIED.get(userid)
    if not expiry:
        return False
    if datetime.now() > expiry:
        del VERIFIED[userid]
        return False
    return True

async def auto_delete_messagex(client, msg_to_delete, notice_msg, time, reload_url):
    try:
        await asyncio.sleep(time)

        try:
            await msg_to_delete.delete()
        except FloodWait as e:
            print(f"⚠️ FloodWait {e.value}s while deleting, sleeping...")
            await asyncio.sleep(e.value)
            await msg_to_delete.delete()
        except UserIsBlocked:
            print("⚠️ User blocked while deleting.")
            return
        except Exception as e:
            print(f"⚠️ Clone Could not delete message: {e}")

        if notice_msg:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("♻️ Get Again", url=reload_url)]]
            ) if reload_url else None
            try:
                await notice_msg.edit_text("✅ Your File/Video is successfully deleted!", reply_markup=keyboard)
            except Exception as e:
                print(f"⚠️ Clone Could not edit notice_msg: {e}")
                try:
                    await client.send_message(
                        notice_msg.chat.id,
                        "✅ Your File/Video is successfully deleted!",
                        reply_markup=keyboard
                    )
                except Exception as e2:
                    print(f"⚠️ Clone Could not send fallback message: {e2}")
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Clone Auto Delete Error:\n\n<code>{e}</code>\n\nKindly check this message to get assistance."
        )
        print(f"⚠️ Clone Auto Delete Error: {e}")
        print(traceback.format_exc())

async def auto_delete_messagey(client, msg_to_delete, notice_msg, time, reload_url):
    try:
        await asyncio.sleep(time)

        for msg in msg_to_delete:
            if msg:
                try:
                    await msg.delete()
                except FloodWait as e:
                    print(f"⚠️ FloodWait {e.value}s while deleting, sleeping...")
                    await asyncio.sleep(e.value)
                    await msg.delete()
                except UserIsBlocked:
                    print("⚠️ User blocked while deleting.")
                    return
                except Exception as e:
                    print(f"⚠️ Clone Could not delete message: {e}")

        if notice_msg:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("♻️ Get Again", url=reload_url)]]
            ) if reload_url else None
            try:
                await notice_msg.edit_text("✅ Your File/Video is successfully deleted!", reply_markup=keyboard)
            except Exception as e:
                print(f"⚠️ Clone Could not edit notice_msg: {e}")
                try:
                    await client.send_message(
                        notice_msg.chat.id,
                        "✅ Your File/Video is successfully deleted!",
                        reply_markup=keyboard
                    )
                except Exception as e2:
                    print(f"⚠️ Clone Could not send fallback message: {e2}")
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Clone Auto Delete Error:\n\n<code>{e}</code>\n\nKindly check this message to get assistance."
        )
        print(f"⚠️ Clone Auto Delete Error: {e}")
        print(traceback.format_exc())

def random_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def get_short_link(user, link):
    base_site = user["base_site"]
    api_key = user["shortener_api"]
    response = requests.get(f"https://{base_site}/api?api={api_key}&url={link}")
    data = response.json()
    if data["status"] == "success" or rget.status_code == 200:
        return data["shortenedUrl"]

async def is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER
        ]
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        print(f"⚠️ Bot is not admin in chat {chat_id}, cannot check admin status.")
        return False
    except Exception as e:
        print(f"⚠️ is_admin() failed for user {user_id} in chat {chat_id}: {e}")
        return False

def mask_partial(word):
    if len(word) <= 2:
        return word[0] + "*"
    mid = len(word) // 2
    return word[:1] + "*" + word[2:]

def clean_text(text: str) -> str:
    cleaned = text
    for word in script.BAD_WORDS:
        cleaned = re.sub(
            re.escape(word), 
            mask_partial(word), 
            cleaned, 
            flags=re.IGNORECASE
        )
    return cleaned

def batch_progress_bar(done, total, length=20):
    if total == 0:
        return "[░" * length + "] 0%"
    
    percent = int((done / total) * 100)
    filled = int((done / total) * length)
    empty = length - filled
    bar = "▓" * filled + "░" * empty

    percent_str = f"{percent}%"
    bar_list = list(bar)
    start_pos = max((length - len(percent_str)) // 2, 0)
    for i, c in enumerate(percent_str):
        if start_pos + i < length:
            bar_list[start_pos + i] = c
    return f"[{''.join(bar_list)}]"

async def broadcast_messagesy(bot_id, user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(bot_id, user_id, message)
    except InputUserDeactivated:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Error"
    except Exception:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Error"

def broadcast_progress_bary(done: int, total: int) -> str:
    try:
        progress = done / total if total > 0 else 0
        filled = int(progress * 20)
        empty = 20 - filled
        bar_str = "█" * filled + "░" * empty
        return f"[{bar_str}] {done}/{total}"
    except Exception as e:
        return f"[Error building bar: {e}] {done}/{total}"
