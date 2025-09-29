import logging, asyncio, re, base64, random, string, time, traceback
from datetime import *
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from pyrogram.errors.exceptions.bad_request_400 import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SHORTEN_STATE = {}

START_TIME = time.time()

@Client.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = [int(m) for m in clone.get("moderators", [])]
        start_text = clone.get("wlc", script.START_TXT) 
        start_pic = clone.get("pics", None)
        caption = clone.get("caption", None)
        buttons_data = clone.get("button", [])
        fsub_data = clone.get("force_subscribe", [])
        access_token = clone.get("access_token", False)
        tutorial_url = clone.get("at_tutorial", None)
        premium = [int(p["user_id"]) if isinstance(p, dict) else int(p) for p in clone.get("premium_user", [])]
        premium_upi = clone.get("premium_upi", None)
        auto_delete = clone.get("auto_delete", False)
        auto_delete_time = str(clone.get("ad_time", "1h"))
        auto_delete_time2 = parse_time(clone.get("ad_time", "1h"))
        auto_delete_msg = clone.get('ad_msg', script.AD_TXT)
        forward_protect = clone.get("forward_protect", False)

        num_str = "".join(filter(str.isdigit, auto_delete_time)) or "0"
        unit_char = "".join(filter(str.isalpha, auto_delete_time)) or "h"

        try:
            number = int(num_str)
        except:
            number = 0

        unit_map = {"d": "day(s)", "h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
        unit = unit_map.get(unit_char.lower(), "hour(s)")

        user_id = message.from_user.id
        mention=message.from_user.mention

        # --- Track new users ---
        if not await clonedb.is_user_exist(me.id, user_id):
            await clonedb.add_user(me.id, user_id)
            await db.increment_users_count(me.id)

        # --- Fsub Handler ---
        if not await is_subscribedy(client, user_id, me.id) and user_id != owner_id and user_id not in moderators and user_id not in premium:
            try:
                new_fsub_data = []
                buttons = []
                updated = False

                clone_client = get_client(me.id)
                if not clone_client:
                    await safe_action(client.send_message, user_id, "⚠️ Clone bot not running. Start it first!")
                    return

                for item in fsub_data:
                    ch_id = int(item["channel"])
                    mode = item.get("mode", "normal")
                    limit = item.get("limit", 0)
                    joined = item.get("joined", 0)
                    users_counted = item.get("users_counted", [])

                    if not item.get("link"):
                        try:
                            code = random_code()
                            if mode == "request":
                                invite = await clone_client.create_chat_invite_link(ch_id, creates_join_request=True, name=f"fsub-{code}")
                            else:
                                invite = await clone_client.create_chat_invite_link(ch_id)
                            item["link"] = invite.invite_link
                            item["invite_code"] = code
                            updated = True
                        except Exception as e:
                            print(f"⚠️ Clone Error creating invite for {ch_id}: {e}")

                    if limit != 0 and joined >= limit:
                        continue

                    if user_id not in users_counted:
                        already_member = False
                        try:
                            member = await clone_client.get_chat_member(ch_id, user_id)
                            if member.status in [
                                enums.ChatMemberStatus.MEMBER,
                                enums.ChatMemberStatus.ADMINISTRATOR,
                                enums.ChatMemberStatus.OWNER
                            ]:
                                already_member = True
                        except UserNotParticipant:
                            already_member = False
                        except Exception as e:
                            print(f"⚠️ Error checking member in request mode: {e}")
                            already_member = False

                        if not already_member and item.get("link"):
                            buttons.append([InlineKeyboardButton("🔔 Join Channel", url=item["link"])])
                    new_fsub_data.append(item)
                    continue

                if updated:
                    await db.update_clone(me.id, {"force_subscribe": new_fsub_data})

                if buttons:
                    if len(message.command) > 1:
                        start_arg = message.command[1]
                        try:
                            kk, file_id = start_arg.split("_", 1)
                            buttons.append([
                                InlineKeyboardButton("♻️ Try Again", callback_data=f"checksub#{kk}#{file_id}")
                            ])
                        except:
                            buttons.append([
                                InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{me.username}?start={start_arg}")
                            ])

                    await safe_action(client.send_message,
                        user_id,
                        "🚨 You must join the channel(s) first to use this bot.",
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    return
            except UserIsBlocked:
                print(f"⚠️ User {user_id} blocked the bot. Skipping fsub...")
                return
            except Exception as e:
                if "INPUT_USER_DEACTIVATED" in str(e):
                    print(f"⚠️ User {user_id} account is deleted. Skipping batch...")
                    return
                else:
                    await safe_action(client.send_message,
                        LOG_CHANNEL,
                        f"⚠️ Clone Fsub Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                    )
                    print(f"⚠️ Clone Fsub Handler Error: {e}")
                    print(traceback.format_exc())

        # --- Start Handler ---
        if len(message.command) == 1:
            buttons = [[
                InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
                InlineKeyboardButton('😊 About', callback_data='about')
                ],[
                InlineKeyboardButton('🤖 Create Your Own Clone', url=f'https://t.me/{BOT_USERNAME}?start')
                ],[
                InlineKeyboardButton('🔒 Close', callback_data='close')
            ]]

            if start_pic:
                return await safe_action(message.reply_photo,
                    photo=start_pic,
                    caption=start_text.format(user=mention, bot=client.me.mention),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            return await safe_action(message.reply_text,
                start_text.format(user=mention, bot=client.me.mention),
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        data = message.command[1]
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""

        # --- Verification Handler ---
        if data.startswith("VERIFY-"):
            parts = data.split("-", 2)
            if len(parts) != 3:
                return await safe_action(message.reply_text, "❌ Invalid or expired link!", protect_content=forward_protect)

            user_id, token = parts[1], parts[2]
            if str(message.from_user.id) != user_id:
                return await safe_action(message.reply_text, "❌ Invalid or expired link!", protect_content=forward_protect)

            if await check_token(client, user_id, token):
                await verify_user(client, user_id, token)
                return await safe_action(message.reply_text,
                    f"Hey {message.from_user.mention}, **verification** successful! ✅",
                    protect_content=forward_protect
                )
            else:
                return await safe_action(message.reply_text, "❌ Invalid or expired link!", protect_content=forward_protect)

        # --- Single File Handler ---
        if data.startswith("SINGLE-"):
            try:
                encoded = data.replace("SINGLE-", "", 1)
                decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("ascii")
                pre, decode_file_id = decoded.split("_", 1)

                if access_token and user_id != owner_id and user_id not in moderators and user_id not in premium and not await check_verification(client, user_id):
                    verify_url = await get_token(client, user_id, f"https://t.me/{me.username}?start=")
                    btn = [[InlineKeyboardButton("✅ Verify", url=verify_url)]]

                    if premium_upi:
                        btn.append([InlineKeyboardButton("🛡 Remove Ads", callback_data='remove_ads')])

                    if tutorial_url:
                        btn.append([InlineKeyboardButton("ℹ️ Tutorial", url=tutorial_url)])

                    btn.append([InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{me.username}?start=SINGLE-{encoded}")])

                    return await safe_action(message.reply_text,
                        "🚫 You are not **verified**! Kindly **verify** to continue.",
                        protect_content=forward_protect,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )

                file = await db.get_file(decode_file_id)
                if not file:
                    return await safe_action(message.reply, "❌ File not found in database.")

                file_id = file.get("file_id")
                file_name = file.get("file_name") or "None"
                file_size = file.get("file_size")
                media_type = file.get("media_type", "document")
                original_caption = file.get("caption") or ""

                if file_size and isinstance(file_size, int):
                    await db.add_storage_used(me.id, file_size)

                f_caption = original_caption
                if caption:
                    try:
                        f_caption = caption.format(
                            file_name=file_name,
                            file_size=get_size(file_size) if file_size else "N/A",
                            caption=original_caption
                        )
                    except:
                        f_caption = original_caption

                if not f_caption.strip():
                    f_caption = "None"

                sent_msg = None
                if file_id:
                    sent_msg = await safe_action(client.send_cached_media,
                        chat_id=user_id,
                        file_id=file_id,
                        caption=f_caption,
                        protect_content=forward_protect
                    )
                else:
                    sent_msg = await safe_action(message.reply_text, original_caption, protect_content=forward_protect)

                if sent_msg:
                    if buttons_data:
                        buttons = [[InlineKeyboardButton(btn["name"], url=btn["url"])] for btn in buttons_data]
                        try:
                            if sent_msg.caption is not None:
                                await safe_action(sent_msg.edit_caption, f_caption, reply_markup=InlineKeyboardMarkup(buttons))
                            else:
                                await safe_action(sent_msg.edit_text, original_caption, reply_markup=InlineKeyboardMarkup(buttons))
                        except Exception as e:
                            if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
                                raise

                notice = None
                if sent_msg and auto_delete:
                    notice = await safe_action(client.send_message,
                        user_id,
                        auto_delete_msg.format(time=number, unit=unit),
                    )
                    
                    reload_url = f"https://t.me/{me.username}?start=SINGLE-{encoded}"
                    asyncio.create_task(auto_delete_message(client, [sent_msg], notice, auto_delete_time2, reload_url))
            except UserIsBlocked:
                print(f"⚠️ User {user_id} blocked the bot. Skipping single...")
                return
            except Exception as e:
                await safe_action(client.send_message,
                    LOG_CHANNEL,
                    f"⚠️ Clone Single File Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                )
                print(f"⚠️ Clone Single File Handler Error: {e}")
                print(traceback.format_exc())

        # --- Batch File Handler ---
        if data.startswith("BATCH-"):
            try:
                file_id = data.split("-", 1)[1]
                decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")

                if access_token and user_id != owner_id and user_id not in moderators and user_id not in premium and not await check_verification(client, user_id):
                    verify_url = await get_token(client, user_id, f"https://t.me/{me.username}?start=")
                    btn = [[InlineKeyboardButton("✅ Verify", url=verify_url)]]

                    if premium_upi:
                        btn.append([InlineKeyboardButton("🛡 Remove Ads", callback_data='remove_ads')])

                    if tutorial_url:
                        btn.append([InlineKeyboardButton("ℹ️ Tutorial", url=tutorial_url)])

                    btn.append([InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{me.username}?start=BATCH-{file_id}")])

                    return await safe_action(message.reply_text,
                        "🚫 You are not **verified**! Kindly **verify** to continue.",
                        protect_content=forward_protect,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )

                batch = await db.get_batch(decode_file_id)
                if not batch:
                    return await safe_action(message.reply, "⚠️ Batch not found or expired.")

                file_ids = batch.get("file_ids", [])
                total_files = len(file_ids)
                if not total_files:
                    return await safe_action(message.reply, "⚠️ No files in this batch.")

                sts = await safe_action(message.reply, f"📦 Preparing batch...\n\nTotal files: **{total_files}**")

                sent_files = []
                for index, db_file_id in enumerate(file_ids, start=1):
                    try:
                        await safe_action(sts.edit_text, f"📤 Sending file {index}/{total_files}...")

                        if batch.get("is_auto_post"):
                            file = await db.get_file_by_file_id(db_file_id, me.id)
                        else:
                            file = await db.get_file(db_file_id)

                        if not file:
                            continue

                        file_id = file.get("file_id")
                        file_name = file.get("file_name") or "None"
                        file_size = file.get("file_size")
                        media_type = file.get("media_type", "document")
                        original_caption = file.get("caption") or ""

                        if file_size and isinstance(file_size, int):
                            await db.add_storage_used(me.id, file_size)

                        if caption:
                            try:
                                f_caption = caption.format(
                                    file_name=file_name,
                                    file_size=get_size(file_size) if file_size else "N/A",
                                    caption=original_caption
                                )
                            except:
                                f_caption = original_caption or f"<code>{file_name}</code>"
                        else:
                            f_caption = original_caption or f"<code>{file_name}</code>"

                        if not f_caption.strip():
                            f_caption = "None"

                        sent_msg = None
                        if file_id:
                            sent_msg = await safe_action(client.send_cached_media,
                                chat_id=user_id,
                                file_id=file_id,
                                caption=f_caption,
                                protect_content=forward_protect
                            )
                        else:
                            sent_msg = await safe_action(message.reply_text, original_caption, protect_content=forward_protect)

                        buttons = []
                        for btn in buttons_data:
                            buttons.append([InlineKeyboardButton(btn["name"], url=btn["url"])])

                        if buttons:
                            try:
                                if sent_msg and sent_msg.caption is not None:
                                    await safe_action(sent_msg.edit_caption, f_caption, reply_markup=InlineKeyboardMarkup(buttons))
                                else:
                                    await safe_action(sent_msg.edit_text, original_caption, reply_markup=InlineKeyboardMarkup(buttons))
                            except Exception as e:
                                if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
                                    raise

                        sent_files.append(sent_msg)
                        await asyncio.sleep(1.5)
                    except UserIsBlocked:
                        print(f"⚠️ User {user_id} blocked the bot. Skipping batch...")
                        return
                    except Exception as e:
                        if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
                            raise
                        if "INPUT_USER_DEACTIVATED" in str(e):
                            print(f"⚠️ User {user_id} account is deleted. Skipping batch...")
                            return
                        else:
                            await safe_action(client.send_message,
                                LOG_CHANNEL,
                                f"⚠️ Clone Batch File Handler Error sending message:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                            )
                            print(f"⚠️ Clone Batch File Handler Error sending message: {e}")
                            continue

                notice = None
                if sent_files and auto_delete:
                    notice = await safe_action(client.send_message,
                        user_id,
                        auto_delete_msg.format(time=number, unit=unit),
                    )

                    reload_url = f"https://t.me/{me.username}?start=BATCH-{file_id}"
                    asyncio.create_task(auto_delete_message(client, sent_files, notice, auto_delete_time2, reload_url))

                await safe_action(sts.edit_text, f"✅ Batch completed!\n\nTotal files sent: **{total_files}**")
                await asyncio.sleep(5)
                await safe_action(sts.delete)
            except Exception as e:
                if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
                    raise
                if isinstance(e, UserIsBlocked):
                    print(f"⚠️ User {user_id} blocked the bot. Ignoring.")
                else:
                    await safe_action(client.send_message,
                        LOG_CHANNEL,
                        f"⚠️ Clone Batch File Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                    )
                    print(f"⚠️ Clone Batch File Handler Error: {e}")
                    print(traceback.format_exc())

        # --- Auto Post Handler ---
        if data.startswith("AUTO-"):
            encoded = data.replace("AUTO-", "", 1)
            decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("ascii").strip()
            pre, file_id = decoded.split("_", 1)

            if access_token and user_id != owner_id and user_id not in moderators and user_id not in premium and not await check_verification(client, user_id):
                verify_url = await get_token(client, user_id, f"https://t.me/{me.username}?start=")
                btn = [[InlineKeyboardButton("✅ Verify", url=verify_url)]]

                if premium_upi:
                    btn.append([InlineKeyboardButton("🛡 Remove Ads", callback_data='remove_ads')])

                if tutorial_url:
                    btn.append([InlineKeyboardButton("ℹ️ Tutorial", url=tutorial_url)])

                btn.append([InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{me.username}?start=AUTO-{encoded}")])

                return await safe_action(message.reply_text,
                    "🚫 You are not **verified**! Kindly **verify** to continue.",
                    protect_content=forward_protect,
                    reply_markup=InlineKeyboardMarkup(btn)
                )

            try:
                msg = await safe_action(client.send_cached_media,
                    chat_id=user_id,
                    file_id=file_id,
                    protect_content=forward_protect
                )

                filetype = msg.media
                file = getattr(msg, filetype.value)
                file_name = getattr(file, "file_name", None) or "None"
                file_size = getattr(file, "file_size", None)

                if file_size and isinstance(file_size, int):
                    await db.add_storage_used(me.id, file_size)

                original_caption = msg.caption or ""
                if caption:
                    try:
                        f_caption = caption.format(
                            file_name=file_name,
                            file_size=get_size(file_size) if file_size else "N/A",
                            caption=original_caption
                        )
                    except:
                        f_caption = original_caption or f"<code>{file_name}</code>"
                else:
                    f_caption = original_caption or f"<code>{file_name}</code>"

                buttons = []
                for btn in buttons_data:
                    buttons.append([InlineKeyboardButton(btn["name"], url=btn["url"])])

                if buttons:
                    await safe_action(msg.edit_caption, f_caption, reply_markup=InlineKeyboardMarkup(buttons))
                else:
                    await safe_action(msg.edit_caption, f_caption)

                notice=None
                if msg and auto_delete:
                    notice = await safe_action(client.send_message,
                        user_id,
                        auto_delete_msg.format(time=number, unit=unit),
                    )

                    reload_url = f"https://t.me/{me.username}?start=AUTO-{encoded}"
                    asyncio.create_task(auto_delete_message(client, [msg], notice, auto_delete_time2, reload_url))
                return
            except UserIsBlocked:
                print(f"⚠️ User {user_id} blocked the bot. Skipping auto post...")
                return
            except Exception as e:
                if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
                    raise
                await safe_action(client.send_message,
                    LOG_CHANNEL,
                    f"⚠️ Clone Auto Post Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                )
                print(f"⚠️ Clone Auto Post Handler Error: {e}")
                print(traceback.format_exc())
    except UserIsBlocked:
        print(f"⚠️ User {user_id} blocked the bot. Skipping batch...")
        return
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Start Bot Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Start Bot Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("help") & filters.private & filters.incoming)
async def help(client, message):
    try:
        me = await client.get_me()
        clone = await db.get_bot(me.id)
        if not clone:
            return

        await safe_action(message.reply_text, script.HELP_TXT)
    except UserIsBlocked:
        print(f"⚠️ User {message.from_user.id} blocked the bot. Skipping fsub...")
        return
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Help Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Help Error: {e}")
        print(traceback.format_exc())

async def auto_post_clone(bot_id: int, db, target_channel: int):
    try:
        bot_id = int(bot_id)
        clone = await db.get_clone_by_id(bot_id)
        if not clone or not clone.get("auto_post", False):
            return

        owner_id = clone.get("user_id")
        if not await db.is_premium(owner_id):
            return

        username = clone.get('username', bot_id)

        clone_client = get_client(bot_id)
        if not clone_client:
            return

        while True:
            try:
                fresh = await db.get_clone_by_id(bot_id)
                if not fresh or not fresh.get("auto_post", False):
                    return

                owner_id = fresh.get("user_id")
                if not await db.is_premium(owner_id):
                    return

                username = fresh.get('username', bot_id)

                mode = fresh.get("ap_mode", "single")

                item = None
                items = []

                if mode == "single":
                    item = await db.pop_random_unposted_media(bot_id)
                    if not item:
                        print(f"⌛ No new media for @{username}, sleeping 60s...")
                        await asyncio.sleep(60)
                        continue

                    file_id = item.get("file_id")
                    if not file_id:
                        await db.mark_media_posted(item["_id"], bot_id)
                        continue

                    await db.mark_media_posted(item["_id"], bot_id)

                    db_file_id = str(item["_id"])
                    string = f"file_{db_file_id}"
                    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
                    bot_username = (await clone_client.get_me()).username
                    share_link = f"https://t.me/{bot_username}?start=SINGLE-{outstr}"

                elif mode == "batch":
                    batch_size = random.randint(10, 100)
                    for _ in range(batch_size):
                        item = await db.pop_random_unposted_media(bot_id)
                        if item:
                            items.append(item)

                    if not items:
                        print(f"⌛ No new media for @{username}, sleeping 60s...")
                        await asyncio.sleep(60)
                        continue

                    file_ids = [it["file_id"] for it in items]
                    batch_id = await db.add_batch(bot_id, file_ids, is_auto_post=True)
                    string = str(batch_id)
                    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
                    bot_username = (await clone_client.get_me()).username
                    share_link = f"https://t.me/{bot_username}?start=BATCH-{outstr}"

                random_caption = clone.get("random_caption", False)
                header = fresh.get("header", None)
                footer = fresh.get("footer", None)
                selected_caption = random.choice(script.CAPTION_LIST) if script.CAPTION_LIST else ""

                text = ""

                if header:
                    text += f"<blockquote>{header}</blockquote>\n\n"

                if mode == "single":
                    if random_caption:
                        text += f"{selected_caption}\n\n<blockquote>🔗 Here is your link:\n{share_link}</blockquote>"
                    else:
                        text += f"🔗 Here is your link:\n{share_link}"
                elif mode == "batch":
                    if random_caption:
                        text += f"📦 Batch contains {len(items)} items.\n\n{selected_caption}\n\n<blockquote>🔗 Here is your link:\n{share_link}</blockquote>"
                    else:
                        text += f"📦 Batch contains {len(items)} items.\n\n🔗 Here is your link:\n{share_link}"

                if footer:
                    text += f"\n\n<blockquote>{footer}</blockquote>"

                await clone_client.send_photo(
                    chat_id=target_channel,
                    photo=fresh.get("ap_image", None) or "https://i.ibb.co/gFv0Nm8M/IMG-20250904-163513-052.jpg",
                    caption=text,
                    parse_mode=enums.ParseMode.HTML
                )

                if mode == "single":
                    await db.mark_media_posted(bot_id, item["_id"])
                elif mode == "batch":
                    for it in items:
                        await db.mark_media_posted(bot_id, it["file_id"])

                sleep_time = parse_time(fresh.get("ap_sleep", "1h"))
                await asyncio.sleep(sleep_time)
            except Exception as e:
                if 'item' in locals() and item:
                    if mode == "single":
                        await db.unmark_media_posted(bot_id, item["file_id"])
                    elif mode == "batch":
                        for it in items:
                            await db.unmark_media_posted(bot_id, it["file_id"])

                print(f"⚠️ Clone Auto-post error for @{username}: {e}")
                try:
                    await clone_client.send_message(
                        LOG_CHANNEL,
                        f"⚠️ Clone Auto Post Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                    )
                except:
                    pass
                await asyncio.sleep(30)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"❌ Clone AutoPost crashed for {bot_id}:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"❌ Clone AutoPost crashed for {bot_id}: {e}")

@Client.on_message(filters.command(['genlink']) & filters.private)
async def genlink(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        if message.reply_to_message:
            g_msg = message.reply_to_message
        else:
            g_msg = await safe_action(client.ask,
                message.chat.id,
                "📩 Please send me the message (file/text/media) to generate a shareable link.\n\nSend /cancel to stop.",
            )

            if g_msg.text and g_msg.text.lower() == '/cancel':
                return await safe_action(message.reply, '🚫 Process has been cancelled.')

        file_id = None
        file_name = None
        file_size = None
        media_type = "text"

        if g_msg.media:
            media_type = g_msg.media.value
            media_obj = getattr(g_msg, media_type, None)
            if media_obj:
                file_id = getattr(media_obj, "file_id", None)
                file_name = getattr(media_obj, "file_name", None)
                file_size = getattr(media_obj, "file_size", None)

        db_file_id = await db.add_file(
            bot_id=me.id,
            file_id=file_id,
            file_name=file_name,
            file_size=file_size,
            caption=g_msg.caption or g_msg.text,
            media_type=media_type
        )

        string = f"file_{db_file_id}"
        outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        share_link = f"https://t.me/{me.username}?start=SINGLE-{outstr}"

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://t.me/share/url?url={share_link}')]]
        )

        await safe_action(message.reply,
            f"🔗 Here is your link:\n\n{share_link}",
            reply_markup=reply_markup
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Generate Link Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Generate Link Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command(['batch']) & filters.private)
async def batch(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        usage_text = (
            f"📌 Use correct format.\n\n"
            f"Example:\n/batch https://t.me/{me.username}/10 https://t.me/{me.username}/20"
        )

        if " " not in message.text:
            return await safe_action(message.reply, usage_text)

        links = message.text.strip().split(" ")
        if len(links) != 3:
            return await safe_action(message.reply, usage_text)

        cmd, first, last = links
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

        match = regex.match(first)
        if not match:
            return await safe_action(message.reply, '❌ Invalid first link.')
        f_chat_id = match.group(4)
        f_msg_id = int(match.group(5))
        f_chat_id = int(f"-100{f_chat_id}") if f_chat_id.isnumeric() else f_chat_id

        match = regex.match(last)
        if not match:
            return await safe_action(message.reply, '❌ Invalid last link.')
        l_chat_id = match.group(4)
        l_msg_id = int(match.group(5))
        l_chat_id = int(f"-100{l_chat_id}") if l_chat_id.isnumeric() else l_chat_id

        if f_chat_id != l_chat_id:
            return await safe_action(message.reply, "❌ Chat IDs do not match.")

        is_bot_admin = await is_admin(client, f_chat_id, me.id)
        if not is_bot_admin:
            return await safe_action(message.reply, "⚠️ I must be an admin in that channel/group to index messages.")

        chat_id = (await client.get_chat(f_chat_id)).id

        start_id = min(f_msg_id, l_msg_id)
        end_id = max(f_msg_id, l_msg_id)
        total_msgs = (end_id - start_id) + 1

        sts = await safe_action(message.reply, "⏳ Generating links for your messages... This may take some time.")

        outlist = []
        og_msg = 0
        tot = 0

        for msg_id in range(start_id, end_id + 1):
            try:
                msg = await client.get_messages(f_chat_id, msg_id)
            except Exception:
                await asyncio.sleep(0.1)
                continue

            tot += 1
            if og_msg % 10 == 0 or tot == total_msgs:
                try:
                    progress_bar = batch_progress_bar(tot, total_msgs)
                    await safe_action(sts.edit, f"""
⚙️ <b>Generating Batch Link...</b>

📂 Total: {total_msgs}
✅ Done: {tot}/{total_msgs}
⏳ Remaining: {total_msgs - tot}
📌 Status: Saving Messages

{progress}
""")
                except:
                    pass

            if not msg or msg.empty or msg.service:
                await asyncio.sleep(0.1)
                continue

            file_id = None
            file_name = None
            file_size = None
            media_type = "text"

            if msg.media:
                media_type = msg.media.value
                media_obj = getattr(msg, media_type, None)
                if media_obj:
                    file_id = getattr(media_obj, "file_id", None)
                    file_name = getattr(media_obj, "file_name", None)
                    file_size = getattr(media_obj, "file_size", None)

            db_file_id = await db.add_file(
                bot_id=me.id,
                file_id=file_id,
                file_name=file_name,
                file_size=file_size,
                caption=msg.caption or msg.text,
                media_type=media_type
            )

            og_msg += 1
            outlist.append(db_file_id)

        batch_id = await db.add_batch(me.id, outlist)
        string = str(batch_id)
        file_id = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        share_link = f"https://t.me/{me.username}?start=BATCH-{file_id}"

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://t.me/share/url?url={share_link}')]]
        )

        await safe_action(sts.edit,
            f"🔗 Here is your link:\n\n{share_link}",
            reply_markup=reply_markup
        )
    except ChannelInvalid:
        await safe_action(message.reply, '⚠️ This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        await safe_action(message.reply, '⚠️ Invalid Link specified.')
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Batch Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Batch Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("shortener") & filters.private)
async def shorten_handler(client: Client, message: Message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        user_id = message.from_user.id
        cmd = message.command
        user = await clonedb.get_user(user_id)

        help_text = (
            "/shortener - Start shortening links\n"
            "/shortener None - Reset Base Site and Shortener API\n\n"
            "Flow:\n"
            "1️⃣ Send /shortener to start\n"
            "2️⃣ Set your Base Site (e.g., shortnerdomain.com)\n"
            "3️⃣ Set your Shortener API\n"
            "4️⃣ Send the link to shortener\n\n"
            "Example to reset: `/shortener None`"
        )

        if len(cmd) == 1:
            help_msg = await safe_action(message.reply, help_text)
            SHORTEN_STATE[user_id] = {"step": 1, "help_msg_id": help_msg.id}

            if user.get("base_site") and user.get("shortener_api"):
                SHORTEN_STATE[user_id]["step"] = 3
                await safe_action(message.reply, "🔗 Base site and API already set. Send the link you want to shorten:")
            else:
                await safe_action(message.reply, "Please send your **base site** (e.g., shortnerdomain.com):")
            return

        if len(cmd) == 2 and cmd[1].lower() == "none":
            await clonedb.update_user_info(user_id, {"base_site": None, "shortener_api": None})
            SHORTEN_STATE.pop(user_id, None)
            return await safe_action(message.reply, "✅ Base site and API have been reset successfully.")
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Shorten Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Shorten Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        if message.reply_to_message:
            b_msg = message.reply_to_message
        else:
            b_msg = await safe_action(client.ask,
                message.from_user.id,
                "📩 Now send me your broadcast message\n\nType /cancel to stop.",
            )

            if b_msg.text and b_msg.text.lower() == "/cancel":
                return await safe_action(message.reply, "🚫 Broadcast cancelled.")

        users = await clonedb.get_all_users(me.id)
        total_users = await clonedb.total_users_count(me.id)
        sts = await safe_action(message.reply_text, "⏳ Broadcast starting...")

        done = blocked = deleted = failed = success = 0
        start_time = time.time()

        async for user in users:
            if 'user_id' in user:
                pti, sh = await broadcast_messagesy(me.id, int(user['user_id']), b_msg)
                if pti:
                    success += 1
                else:
                    if sh == "Blocked":
                        blocked += 1
                    elif sh == "Deleted":
                        deleted += 1
                    else:
                        failed += 1
                done += 1

                if done % 10 == 0 or done == total_users:
                    progress = broadcast_progress_bar(done, total_users)
                    percent = (done / total_users) * 100
                    elapsed = time.time() - start_time
                    speed = done / elapsed if elapsed > 0 else 0
                    remaining = total_users - done
                    eta = timedelta(seconds=int(remaining / speed)) if speed > 0 else "∞"

                    try:
                        await safe_action(sts.edit, f"""
📢 <b>Broadcast in Progress...</b>

{progress}

👥 Total Users: {total_users}
✅ Success: {success}
🚫 Blocked: {blocked}
❌ Deleted: {deleted}
⚠️ Failed: {failed}

⏳ ETA: {eta}
⚡ Speed: {speed:.2f} users/sec
""")
                    except:
                        pass
            else:
                done += 1
                failed += 1

        time_taken = timedelta(seconds=int(time.time() - start_time))
        final_progress = broadcast_progress_bar(total_users, total_users)
        final_text = f"""
✅ <b>Broadcast Completed</b> ✅

⏱ Duration: {time_taken}
👥 Total Users: {total_users}

📊 Results:
✅ Success: {success} ({(success/total_users)*100:.1f}%)
🚫 Blocked: {blocked} ({(blocked/total_users)*100:.1f}%)
❌ Deleted: {deleted} ({(deleted/total_users)*100:.1f}%)
⚠️ Failed: {failed} ({(failed/total_users)*100:.1f}%)

━━━━━━━━━━━━━━━━━━━━━━
{final_progress} 100%
━━━━━━━━━━━━━━━━━━━━━━

⚡ Speed: {speed:.2f} users/sec
"""
        await safe_action(sts.edit, final_text)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Broadcast Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Broadcast Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("stats") & filters.private & filters.incoming)
async def stats(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        users_count = clone.get("users_count", 0)
        storage_used = clone.get("storage_used", 0)
        storage_limit = clone.get("storage_limit", 536870912)
        storage_free = storage_limit - storage_used
        banned_users = len(clone.get("banned_users", []))

        uptime = str(timedelta(seconds=int(time.time() - START_TIME)))

        await safe_action(message.reply,
            f"📊 Status for @{clone.get('username')}\n\n"
            f"👤 Users: {users_count}\n"
            f"🚫 Banned: {banned_users}\n"
            f"💾 Used: {get_size(storage_used)} / {get_size(storage_limit)}\n"
            f"💽 Free: {get_size(storage_free)}\n"
            f"⏱ Uptime: {uptime}\n",
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Stats Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Stats Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("contact") & filters.private & filters.incoming)
async def contact(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = [int(m) for m in clone.get("moderators", [])]

        if message.reply_to_message:
            c_msg = message.reply_to_message
        else:
            c_msg = await safe_action(client.ask,
                message.from_user.id,
                "📩 Now send me your contact message\n\nType /cancel to stop."
            )

            if c_msg.text and c_msg.text.lower() == "/cancel":
                return await safe_action(message.reply, "🚫 Contact cancelled.")

        header = (
            f"📩 **New Contact Message**\n\n"
            f"👤 User: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
            f"🆔 ID: `{message.from_user.id}`\n"
        )

        if c_msg.media:
            orig_caption = c_msg.caption or ""
            final_caption = f"{header}\n💬 Message:\n{orig_caption}" if orig_caption else header
            if owner_id:
                await safe_action(c_msg.copy, owner_id, caption=final_caption)
            for mod_id in moderators:
                await safe_action(c_msg.copy, mod_id, caption=final_caption)
        elif c_msg.text:
            content = f"\n💬 Message:\n{c_msg.text}"
            final_text = header + content
            if owner_id:
                await safe_action(client.send_message, owner_id, final_text)
            for mod_id in moderators:
                await safe_action(client.send_message, mod_id, final_text)
        else:
            if owner_id:
                await safe_action(client.send_message, owner_id, header)
            for mod_id in moderators:
                await safe_action(client.send_message, mod_id, header)

        await safe_action(message.reply_text, "✅ Your message has been sent to the admin!")
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Contact Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Contact Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.private & filters.reply)
async def reply(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        if not message.reply_to_message:
            return

        if not message.reply_to_message.text or "🆔 ID:" not in message.reply_to_message.text:
            return

        try:
            user_id_line = [line for line in message.reply_to_message.text.splitlines() if line.startswith("🆔 ID:")][0]
            user_id = int(user_id_line.replace("🆔 ID:", "").strip(" `"))
        except Exception:
            return

        if message.media:
            orig_caption = message.caption or ""
            final_caption = f"📩 **Reply from Admin**\n\n💬 Message:\n{orig_caption}" if orig_caption else "📩 **Reply from Admin**"
            await safe_action(message.copy, user_id, caption=final_caption)
        elif message.text:
            text = f"📩 **Reply from Admin**\n\n💬 Message:\n{message.text}"
            await safe_action(client.send_message, user_id, text)
        else:
            await safe_action(client.send_message, user_id, "📩 **Reply from Admin**")

        await safe_action(message.reply, "✅ Reply delivered!")
    except UserIsBlocked:
        print(f"⚠️ User {message.from_user.id} blocked the bot. Skipping reply...")
        return
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Reply Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Reply Error: {e}")
        print(traceback.format_exc())

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        data = query.data

        if data.startswith("checksub"):
            if not await is_subscribedy(client, query):
                await safe_action(query.answer, "Join our channel first.", show_alert=True)
                return
            
            _, kk, file_id = data.split("#")
            await safe_action(query.answer,url=f"https://t.me/{me.username}?start={kk}_{file_id}")

        # Remove Ads / Premium Plan Menu
        elif data == "remove_ads":
            premium_btns = [
                [InlineKeyboardButton("7 Days", callback_data="premium_7")],
                [InlineKeyboardButton("1 Month", callback_data="premium_30")],
                [InlineKeyboardButton("6 Months", callback_data="premium_180")],
                [InlineKeyboardButton("1 Year", callback_data="premium_365")],
                [InlineKeyboardButton("⬅️ Back", callback_data="start")]
            ]
            await safe_action(query.message.edit_text,
                "💎 Choose your Premium Plan to remove ads:",
                reply_markup=InlineKeyboardMarkup(premium_btns)
            )

        # User clicked a specific plan
        elif data.startswith("premium_") and not data.startswith("premium_done_"):
            parts = data.split("_")
            if len(parts) < 2 or not parts[1].isdigit():
                await safe_action(query.answer, "⚠️ Invalid plan.", show_alert=True)
                return
            days = int(parts[1])
            price_list = {7: "₹49", 30: "₹149", 180: "₹749", 365: "₹1199"}
            price = price_list.get(days, "N/A")
            premium_upi = clone.get("premium_upi", None)
            buttons = [
                [InlineKeyboardButton("✅ Payment Done", callback_data=f"premium_done_{days}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="remove_ads")]
            ]
            await safe_action(query.message.edit_text,
                f"💎 Premium Plan Details:\n\n"
                f"🗓 Duration: {days} days\n"
                f"💰 Price: {price}\n"
                f"📲 UPI ID: `{premium_upi}`\n\n"
                f"📝 Steps to complete payment:\n"
                f"1️⃣ Use the UPI ID above to make the payment\n"
                f"2️⃣ Make payment of {price}\n"
                f"3️⃣ Take a screenshot of the payment\n"
                f"4️⃣ Click '✅ Payment Done' below\n"
                f"5️⃣ Send a screenshot through contact command\n\n"
                f"⏳ Once payment is confirmed, your premium access will be activated.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # User clicked Payment Done
        elif data.startswith("premium_done_"):
            parts = data.split("_")
            if len(parts) < 3 or not parts[-1].isdigit():
                await safe_action(query.answer, "⚠️ Invalid premium data.", show_alert=True)
                return
            days = int(parts[-1])
            user_id = query.from_user.id
            first_name = query.from_user.first_name

            await safe_action(query.message.edit_text,
                f"⏳ Payment received for **Premium Plan** ({days} days).\nWaiting for admin approval...",
                parse_mode=enums.ParseMode.MARKDOWN
            )

            approval_buttons = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_{days}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_{days}")
                ]
            ]

            if owner_id:
                await safe_action(client.send_message,
                    owner_id,
                    f"📩 *New Payment Confirmation*\n\n"
                    f"👤 User: [{first_name}](tg://user?id={user_id})\n"
                    f"🆔 ID: `{user_id}`\n"
                    f"🗓 Plan: {days} days\n\n"
                    f"Do you want to approve or reject?",
                    reply_markup=InlineKeyboardMarkup(approval_buttons)
                )

            for mod_id in moderators:
                await safe_action(client.send_message,
                    mod_id,
                    f"📩 *New Payment Confirmation*\n\n"
                    f"👤 User: [{first_name}](tg://user?id={user_id})\n"
                    f"🆔 ID: `{user_id}`\n"
                    f"🗓 Plan: {days} days\n\n"
                    f"Do you want to approve or reject?",
                    reply_markup=InlineKeyboardMarkup(approval_buttons)
                )

        # Admin approves premium
        elif data.startswith("approve_"):
            try:
                parts = data.split("_")
                if len(parts) < 3:
                    await safe_action(query.answer, "⚠️ Invalid approve data.", show_alert=True)
                    return

                user_id_str, days_str = parts[1], parts[2]
                user_id = int(user_id_str)
                days = int(days_str)

            except Exception:
                await safe_action(query.answer, "⚠️ Invalid approve data.", show_alert=True)
                return

            premium_users = clone.get("premium_user", [])
            normalized = []

            for pu in premium_users:
                if isinstance(pu, dict):
                    uid = pu.get("user_id")
                    expiry = pu.get("expiry", 0)
                    if uid:
                        normalized.append({"user_id": int(uid), "expiry": expiry})
                else:
                    normalized.append({"user_id": int(pu), "expiry": 0})

            normalized = [u for u in normalized if u["user_id"] != user_id]

            expiry = datetime.utcnow() + timedelta(days=days)
            normalized.append({"user_id": user_id, "expiry": expiry.timestamp()})

            await db.update_clone(me.id, {"premium_user": normalized})

            await safe_action(client.send_message,
                user_id,
                f"✅ Your Premium Plan ({days} days) has been approved!\nEnjoy ad-free experience 🎉"
            )

            await safe_action(query.message.edit_text,
                f"✅ Approved Premium Plan for user `{user_id}` ({days} days)."
            )

        # Admin rejects premium
        elif data.startswith("reject_"):
            try:
                parts = data.split("_")
                if len(parts) < 3:
                    await safe_action(query.answer, "⚠️ Invalid reject data.", show_alert=True)
                    return

                user_id_str, days_str = parts[1], parts[2]
                user_id = int(user_id_str)
                days = int(days_str)

            except Exception:
                await safe_action(query.answer, "⚠️ Invalid reject data.", show_alert=True)
                return

            premium_users = clone.get("premium_user", [])
            normalized = []

            for pu in premium_users:
                if isinstance(pu, dict):
                    uid = pu.get("user_id")
                    expiry = pu.get("expiry", 0)
                    if uid and int(uid) != user_id:
                        normalized.append({"user_id": int(uid), "expiry": expiry})
                else:
                    if int(pu) != user_id:
                        normalized.append({"user_id": int(pu), "expiry": 0})

            await db.update_clone(me.id, {"premium_user": normalized})

            await safe_action(client.send_message,
                user_id,
                f"❌ Your Premium Plan ({days} days) payment was *rejected*.\nContact support for help.",
            )

            await safe_action(query.message.edit_text,
                f"❌ Rejected Premium Plan for user `{user_id}` ({days} days)."
            )

        # Start Menu
        elif data == "start":
            buttons = [
                [InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
                 InlineKeyboardButton('ℹ️ About', callback_data='about')],
                [InlineKeyboardButton('🤖 Create Your Own Clone', url=f'https://t.me/{BOT_USERNAME}?start')],
                [InlineKeyboardButton('🔒 Close', callback_data='close')]
            ]
            start_text = clone.get("wlc", script.START_TXT)
            await safe_action(query.message.edit_text,
                text=start_text.format(user=query.from_user.mention, bot=me.mention),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await safe_action(query.answer)

        # Help
        elif data == "help":
            buttons = [[InlineKeyboardButton('⬅️ Back', callback_data='start')]]
            await safe_action(query.message.edit_text,
                text=script.HELP_TXT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await safe_action(query.answer)

        # About
        elif data == "about":
            buttons = [[InlineKeyboardButton('⬅️ Back', callback_data='start')]]
            ownerid = int(clone['user_id'])
            await safe_action(query.message.edit_text,
                text=script.CABOUT_TXT.format(bot=me.mention, developer=ownerid),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await safe_action(query.answer)

        # Close
        elif data == "close":
            await safe_action(query.message.delete)

        else:
            await safe_action(client.send_message,
                LOG_CHANNEL,
                f"⚠️ Clone Unknown Callback Data Received:\n\n{data}\n\nUser: {query.from_user.id}\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
            )
            await safe_action(query.answer, "⚠️ Unknown action.", show_alert=True)
    except UserIsBlocked:
        print(f"⚠️ User {query.from_user.id} blocked the bot. Skipping callback...")
        return
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e) and "MESSAGE_ID_INVALID" not in str(e):
            raise
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Callback Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Callback Handler Error: {e}")
        print(traceback.format_exc())
        await safe_action(query.answer, "❌ An error occurred. The admin has been notified.", show_alert=True)

@Client.on_message(filters.all)
async def message_capture(client: Client, message: Message):
    try:
        if not message or not message.chat:
            return

        chat = message.chat
        user_id = message.from_user.id if message.from_user else None

        if chat.type == enums.ChatType.PRIVATE and user_id:
            if user_id not in SHORTEN_STATE:
                return

            state = SHORTEN_STATE[user_id]

            help_msg_id = state.get("help_msg_id")
            if help_msg_id:
                try:
                    await safe_action(client.delete_messages, chat_id=message.chat.id, message_ids=help_msg_id)
                except:
                    pass
                state.pop("help_msg_id", None)

            if state["step"] == 1:
                base_site = message.text.strip()
                new_text = base_site.removeprefix("https://").removeprefix("http://")
                if not domain(new_text):
                    return await safe_action(message.reply, "❌ Invalid domain. Send a valid base site:")
                await clonedb.update_user_info(user_id, {"base_site": new_text})
                state["step"] = 2
                await safe_action(message.reply, "✅ Base site set. Now send your **Shortener API key**:")
                return

            if state["step"] == 2:
                api = message.text.strip()
                await clonedb.update_user_info(user_id, {"shortener_api": api})
                state["step"] = 3
                await safe_action(message.reply, "✅ API set. Now send the **link to shorten**:")
                return

            if state["step"] == 3:
                long_link = message.text.strip()
                user = await clonedb.get_user(user_id)
                base_site = user.get("base_site")
                api_key = user.get("shortener_api")

                if not base_site or not api_key:
                    SHORTEN_STATE[user_id] = {"step": 1}
                    return await safe_action(message.reply, "❌ Base site or API missing. Let's start over.")

                short_link = await get_short_link(user, long_link)

                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔁 Share URL", url=f'https://t.me/share/url?url={short_link}')]]
                )

                await safe_action(message.reply,
                    f"🔗 Here is your shortened link:\n\n{short_link}",
                    reply_markup=reply_markup
                )
                
                SHORTEN_STATE.pop(user_id, None)
        elif chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
            me = await get_me_safe(client)
            if not me:
                return

            clone = await db.get_bot(me.id)
            if not clone:
                return

            owner_id = clone.get("user_id")
            moderators = clone.get("moderators", [])
            moderators = [int(m) for m in moderators]
            word_filter = clone.get("word_filter", False)
            random_caption = clone.get("random_caption", False)
            header = clone.get("header", None)
            footer = clone.get("footer", None)

            bot_is_admin = await is_admin(client, message.chat.id, me.id)

            selected_caption = random.choice(script.CAPTION_LIST)

            text = message.text or message.caption or ""
            original_text = text

            if text:
                if word_filter:
                    text = clean_text(original_text)
                else:
                    text = text

            if bot_is_admin:
                if message.chat.id not in [LOG_CHANNEL, -1003015483271, -1002768686427]:
                    notify_msg = None
                    if text != original_text:
                        try:
                            await safe_action(message.edit, text)
                            notify_msg = f"⚠️ Edited inappropriate content in clone @{me.username}.\nChat Title: {message.chat.title}\nChat ID: {message.chat.id}\nMessage ID: {message.id}"
                        except Exception as e:
                            if "CHAT_ADMIN_REQUIRED" in str(e) or "MESSAGE_EDIT_FORBIDDEN" in str(e):
                                print(f"⚠️ Cannot edit message in {chat.id} (no permission). Skipping.")
                            else:
                                print(f"⚠️ Unexpected edit error: {e}")
                                print(traceback.format_exc())

                        if notify_msg and notify_msg.strip():
                            for mod_id in moderators:
                                await safe_action(client.send_message, chat_id=mod_id, text=notify_msg)
                            if owner_id:
                                await safe_action(client.send_message, chat_id=owner_id, text=notify_msg)
            else:
                for mod_id in moderators:
                    await safe_action(client.send_message, chat_id=mod_id, text="⚠️ Bot is not admin.")
                if owner_id:
                    await safe_action(client.send_message, chat_id=owner_id, text="⚠️ Bot is not admin.")

            new_text = ""

            if header:
                new_text += f"<blockquote>{header}</blockquote>\n\n"

            if random_caption:
                new_text += f"{selected_caption}\n\n<blockquote>{text}</blockquote>"
            else:
                new_text += f"{text}"

            if footer:
                new_text += f"\n\n<blockquote>{footer}</blockquote>"

            if bot_is_admin:
                if message.chat.id not in [LOG_CHANNEL, -1003015483271, -1002768686427]:
                    if me.username and me.username in text:
                        await safe_action(message.delete)

                        file_id = None
                        if message.photo:
                            file_id = message.photo.file_id
                        elif message.video:
                            file_id = message.video.file_id
                        elif message.document:
                            file_id = message.document.file_id

                        if file_id:
                            await safe_action(client.send_cached_media,
                                chat_id=message.chat.id,
                                file_id=file_id,
                                caption=new_text if new_text.strip() else None,
                                parse_mode=enums.ParseMode.HTML
                            )
                        else:
                            if new_text and new_text.strip():
                                await safe_action(client.send_message,
                                    chat_id=message.chat.id,
                                    text=new_text,
                                    parse_mode=enums.ParseMode.HTML
                                )
            else:
                for mod_id in moderators:
                    await safe_action(client.send_message, chat_id=mod_id, text="⚠️ Bot is not admin.")
                if owner_id:
                    await safe_action(client.send_message, chat_id=owner_id, text="⚠️ Bot is not admin.")

            media_file_id = None
            media_type = None
            if message.chat.id in [-1003015483271, -1002768686427]:
                if not await db.is_premium(owner_id):
                    return

                if message.photo:
                    media_file_id = message.photo.file_id
                    media_type = "photo"
                elif message.video:
                    media_file_id = message.video.file_id
                    media_type = "video"
                elif message.document:
                    media_file_id = message.document.file_id
                    media_type = "document"
                elif message.animation:
                    media_file_id = message.animation.file_id
                    media_type = "animation"

                if media_file_id:
                    if await db.is_media_exist(me.id, media_file_id):
                        print(f"⚠️ Duplicate media skip kiya: {media_type} ({media_file_id}) for bot {me.id}")
                        return

                    await db.add_media(
                        bot_id=me.id,
                        file_id=media_file_id,
                        caption=message.caption or "",
                        media_type=media_type,
                        date=int(message.date.timestamp())
                    )
                    print(f"✅ Saved media: {media_type} ({media_file_id}) for bot @{me.username}")
                    await asyncio.sleep(0.25)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone message_capture Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone message_capture Error: {e}")
        print(traceback.format_exc())

@Client.on_chat_member_updated()
async def member_updated_handler(client, event):
    try:
        old_status = getattr(event.old_chat_member, "status", None)
        new_status = getattr(event.new_chat_member, "status", None)

        if new_status not in (
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER
        ):
            return

        if old_status in (
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER
        ):
            return

        invite_link_used = getattr(event, "invite_link", None)
        if not invite_link_used:
            return

        user_id = event.new_chat_member.user.id
        chat_id = event.chat.id

        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        fsub_data = clone.get("force_subscribe", [])
        updated = False

        for item in fsub_data:
            try:
                if int(item.get("channel")) != chat_id:
                    continue
                if item.get("mode", "normal") != "normal":
                    continue
                bot_invite = item.get("link")
                if not bot_invite or bot_invite != invite_link_used.invite_link:
                    continue

                users_counted = item.get("users_counted") or []
                if user_id not in users_counted:
                    item["joined"] = item.get("joined", 0) + 1
                    users_counted.append(user_id)
                    item["users_counted"] = users_counted
                    updated = True

            except Exception as e:
                print(f"⚠️ member_updated_handler inner loop error: {e}")
                print(traceback.format_exc())
                continue

        if updated:
            await db.update_clone(me.id, {"force_subscribe": fsub_data})

    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone member_updated_handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone member_updated_handler Error: {e}")
        print(traceback.format_exc())

@Client.on_chat_join_request()
async def join_request_handler(client, request):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_bot(me.id)
        if not clone:
            return

        fsub_data = clone.get("force_subscribe", [])
        updated = False

        user_id = request.from_user.id
        chat_id = request.chat.id
        link_used = request.invite_link

        for item in fsub_data:
            if int(item["channel"]) == chat_id:
                if link_used and item.get("link") and link_used.invite_link == item["link"]:
                    users_counted = item.get("users_counted", [])
                    if user_id not in users_counted:
                        item["joined"] = item.get("joined", 0) + 1
                        users_counted.append(user_id)
                        item["users_counted"] = users_counted
                        updated = True

        if updated:
            await db.update_clone(client.me.id, {"force_subscribe": fsub_data})

    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone join_request_handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone join_request_handler Error: {e}")
        print(traceback.format_exc())
