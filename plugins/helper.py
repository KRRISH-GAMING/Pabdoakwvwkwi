from imports import *
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

def remove_client(bot_id: int):
    _clone_clients.pop(int(bot_id), None)

async def safe_action(coro_func, *args, **kwargs):
    while True:
        try:
            return await coro_func(*args, **kwargs)
        except FloodWait as e:
            print(f"⏱ FloodWait: sleeping {e.value} seconds")
            await asyncio.sleep(e.value)
        except UserIsBlocked:
            print(f"⚠️ User blocked the bot. Skipping reply...")
            return
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
                raise
            try:
                await coro_func(
                    LOG_CHANNEL,
                    f"⚠️ Error in safe_action:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                )
            except Exception as inner_e:
                print(f"⚠️ Failed logging: {inner_e}")
            print(f"⚠️ Error in safe_action: {e}")
            print(traceback.format_exc())
            return None

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

def generate_upi_qr(upi_id: str, name: str, amount: float) -> BytesIO:
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    bio.name = "upi_qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

async def fetch_fampay_payments():
    try:
        IMAP_HOST = "imap.gmail.com"
        IMAP_USER = "krrishraj237@gmail.com"
        IMAP_PASS = "ewcz wblx fdgv unpp"

        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(IMAP_USER, IMAP_PASS)

        mail.select("inbox")

        status, email_ids = mail.search(None, '(UNSEEN FROM "no-reply@famapp.in")')

        if status != "OK" or not email_ids or not email_ids[0]:
            return []

        email_list = email_ids[0].split()

        latest_5_emails = email_list[-5:]

        transactions = []
        kolkata_tz = pytz.timezone("Asia/Kolkata")

        for email_id in latest_5_emails:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK" or not msg_data:
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            email_date = msg["Date"]

            try:
                email_datetime = datetime.strptime(email_date, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError as ve:
                continue

            email_datetime = email_datetime.astimezone(kolkata_tz)

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            if not body:
                continue

            amount_match = re.search(r"₹\s?([\d,.]+)", body)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
            else:
                amount = None

            txn_match = re.search(r"transaction id\s*[:\-]?\s*(\w+)", body, re.I)
            txn_id = txn_match.group(1) if txn_match else None

            if not amount or not txn_id:
                continue

            txn = {
                "date": email_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "txn_id": txn_id
            }
            transactions.append(txn)

            mail.store(email_id, '+FLAGS', '\\Seen')

        mail.logout()
        return transactions

    except Exception as e:
        await safe_action(
            client.send_message,
            LOG_CHANNEL,
            f"⚠️ IMAP Error:\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ IMAP Error: {e}")
        print(traceback.format_exc())
        return []

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

def broadcast_progress_bar(done: int, total: int) -> str:
    try:
        progress = done / total if total > 0 else 0
        filled = int(progress * 20)
        empty = 20 - filled
        bar_str = "█" * filled + "░" * empty
        return f"[{bar_str}] {done}/{total}"
    except Exception as e:
        return f"[Error building bar: {e}] {done}/{total}"

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

async def is_subscribedy(client, user_id: int, bot_id: int):
    clone = await db.get_clone(bot_id)
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
            try:
                is_pending = False
                async for req in client.get_chat_join_requests(channel_id):
                    if req.from_user.id == user_id:
                        is_pending = True
                        break

                if is_pending:
                    continue
                else:
                    return False
            except Exception as e:
                print(f"⚠️ Error fetching join requests for {channel_id}: {e}")
                return False

        except Exception as e:
            print(f"⚠️ Clone is_subscribed Error {channel_id}: {e}")
            return False

    return True

def random_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def get_verify_shorted_link(client, link):
    me = await get_me_safe(client)
    if not me:
        return

    clone = await db.get_clone(me.id)
    if not clone:
        return link

    shortlink_url = clone.get("at_shorten_link", None)
    shortlink_api = clone.get("at_shorten_api", None)

    if shortlink_url and shortlink_api:
        url = f"https://{shortlink_url}/api"
        params = {"api": shortlink_api, "url": link}
        try:
            async with ClientSession() as session:
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

    clone = await db.get_clone(me.id)
    if not clone:
        return

    validity_hours = parse_time(clone.get("at_validity", "24h"))
    VERIFIED[userid] = datetime.now() + timedelta(seconds=validity_hours)

    today = datetime.now().strftime("%Y-%m-%d")
    renew_log = clone.get("at_renew_log", {})
    renew_log[today] = renew_log.get(today, 0) + 1

    await db.update_clone(me.id, {"at_renew_log": renew_log})

async def check_verification(client, userid):
    userid = int(userid)
    expiry = VERIFIED.get(userid)
    if not expiry:
        return False
    if datetime.now() > expiry:
        del VERIFIED[userid]
        return False
    return True

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

async def auto_delete_message(client, msg_to_delete, notice_msg, delay_time, reload_url):
    try:
        if delay_time > 0:
            await asyncio.sleep(delay_time)

        for msg in msg_to_delete:
            if msg:
                try:
                    await safe_action(msg.delete)
                except FloodWait as e:
                    print(f"⚠️ FloodWait {e.value}s while deleting, sleeping...")
                    await asyncio.sleep(e.value)
                    await safe_action(msg.delete)
                except UserIsBlocked:
                    print("⚠️ User blocked while deleting.")
                    return
                except Exception as e:
                    print(f"⚠️ Clone Could not delete message: {e}")

        if notice_msg:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ Get Again", url=reload_url)]]) if reload_url else None
            try:
                await safe_action(notice_msg.edit_text, "✅ Your File/Video is successfully deleted!", reply_markup=keyboard)
            except Exception as e:
                print(f"⚠️ Could not edit notice_msg: {e}")
                try:
                    await safe_action(client.send_message, notice_msg.chat.id, "✅ Your File/Video is successfully deleted!", reply_markup=keyboard)
                except Exception as e2:
                    print(f"⚠️ Could not send fallback message: {e2}")

    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Auto Delete Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Auto Delete Error: {e}")
        print(traceback.format_exc())

"""async def schedule_delete(client, db: Database, chat_id, message_ids, notice_id, delay_time, reload_url):
    delete_at = datetime.now(timezone.utc) + timedelta(seconds=delay_time)

    await db.add_scheduled_delete(chat_id, message_ids, notice_id, delete_at, reload_url)

    msgs_to_delete = await client.get_messages(chat_id, message_ids)
    notice_msg = await client.get_messages(chat_id, notice_id)

    await auto_delete_message(client, msgs_to_delete, notice_msg, delay_time, reload_url)

    await db.delete_scheduled_deletes(message_ids)"""

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

async def get_short_link(user, link):
    base_site = user["base_site"]
    api_key = user["shortener_api"]
    response = requests.get(f"https://{base_site}/api?api={api_key}&url={link}")
    data = response.json()
    if data["status"] == "success" or rget.status_code == 200:
        return data["shortenedUrl"]
