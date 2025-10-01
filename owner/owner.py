import os, logging, asyncio, re, time, shutil, sys, traceback
from datetime import *
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from pyrogram.errors.exceptions.bad_request_400 import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *
from clone.clone import *

logger = logging.getLogger(__name__)

PREMIUM_STATE = {}
CLONE_TOKEN = {}
START_TEXT = {}
START_PHOTO = {}
CAPTION_TEXT = {}
ADD_BUTTON = {}
HEADER_TEXT = {}
FOOTER_TEXT = {}
ADD_FSUB = {}
ACCESS_TOKEN = {}
AT_VALIDITY = {}
AT_TUTORIAL = {}
AUTO_POST = {}
AP_IMAGE = {}
AP_SLEEP = {}
PU_UPI = {}
ADD_PU = {}
AD_TIME = {}
AD_MESSAGE = {}
ADD_MODERATOR = {}

START_TIME = time.time()

if SESSION_STRING and len(SESSION_STRING) > 30:
    assistant = Client(
        "assistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
else:
    assistant = Client(
        "assistant",
        api_id=API_ID,
        api_hash=API_HASH
    )

async def promote(bot_username: str):
    try:
        if not assistant.is_connected:
            await assistant.start()

        await assistant.promote_chat_member(
            LOG_CHANNEL,
            bot_username,
            privileges=types.ChatPrivileges(
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_chat=True,
                can_manage_video_chats=True
            )
        )

        await safe_action(assistant.send_message,
            LOG_CHANNEL,
            f"✅ Clone bot @{bot_username} promoted as admin"
        )
        print(f"✅ Clone bot @{bot_username} promoted as admin")
    except Exception as e:
        await safe_action(assistant.send_message,
            LOG_CHANNEL,
            f"⚠️ Promote Clone Bot @{bot_username} Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Promote Clone Bot @{bot_username} Error: {e}")
        print(traceback.format_exc())

async def set_auto_menu(client):
    try:
        owner_cmds = [
            BotCommand("start", "Check I am alive"),
            BotCommand("help", "View help menu"),
            BotCommand("addpremium", "Add a premium user"),
            BotCommand("remove_premium", "Remove a premium user"),
            BotCommand("list_premium", "Show all premium users"),
            BotCommand("check_premium", "Check premium user"),
            BotCommand("broadcast", "Broadcast a message to users"),
            BotCommand("stats", "View bot statistics"),
            BotCommand("restart", "Restart a server"),
        ]
        for admin_id in ADMINS:
            await client.set_bot_commands(owner_cmds, scope=BotCommandScopeChat(chat_id=admin_id))

        default_cmds = [
            BotCommand("start", "Check I am alive"),
            BotCommand("help", "View help menu"),
            BotCommand("contact", "Message to admin"),
        ]
        await client.set_bot_commands(default_cmds, scope=BotCommandScopeDefault())

        print("✅ Main Bot Menu Commands Set!")
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Set Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Set Menu Error: {e}")
        print(traceback.format_exc())

async def set_clone_menu(xd):
    try:
        clone_cmds = [
            BotCommand("start", "Check I am alive"),
            BotCommand("help", "View help menu"),
            BotCommand("genlink", "Store a single message or file"),
            BotCommand("batch", "Store multiple messages from a channel"),
            BotCommand("shortener", "Shorten any shareable links"),
            BotCommand("broadcast", "Broadcast a message to users"),
            BotCommand("stats", "View bot statistics"),
            BotCommand("contact", "Message to admin"),
        ]
        await xd.set_bot_commands(clone_cmds, scope=BotCommandScopeDefault())
        print("✅ Clone Bot Menu Commands Set!")
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Bot Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Bot Menu Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(client, message):
    try:
        user_id=message.from_user.id
        first_name=message.from_user.first_name
        last_name=message.from_user.last_name
        mention=message.from_user.mention
        username=message.from_user.username

        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, first_name)
            await safe_action(client.send_message,
                LOG_CHANNEL,
                script.LOG_TEXT.format(user_id, mention, username)
            )

        if AUTH_CHANNEL and not await is_subscribedx(client, message):
            await asyncio.sleep(2)
            if not await is_subscribedx(client, message):
                if REQUEST_TO_JOIN_MODE:
                    invite_link = await client.create_chat_invite_link(chat_id=int(AUTH_CHANNEL), creates_join_request=True)
                else:
                    invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))

                btn = [[InlineKeyboardButton("🔔 Join Channel", url=invite_link.invite_link)]]

                return await safe_action(client.send_message,
                    user_id,
                    "🚨 You must join the channel first to use this bot.",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.MARKDOWN
                )

        if len(message.command) == 1:
            buttons = [
                [
                    InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
                    InlineKeyboardButton('😊 About', callback_data='about')
                ],
                [InlineKeyboardButton('🤖 Create Your Own Clone', callback_data='clone')],
                [InlineKeyboardButton('🌟 Buy Premium', callback_data='premium')],
                [InlineKeyboardButton('🔒 Close', callback_data='close')]
            ]
            return await safe_action(message.reply_text,
                script.START_TXT.format(user=message.from_user.mention, bot=client.me.mention),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Start Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Start Handler Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("help") & filters.private & filters.incoming)
async def help(client, message):
    try:
        await safe_action(message.reply_text, script.HELP_TXT)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Help Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Help Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS) & filters.private & filters.incoming)
async def add_premium(client: Client, message: Message):
    try:
        ask_id = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="👤 Send the User ID to add as premium:",
            filters=filters.text,
        )
        user_id = int(ask_id.text.strip())

        ask_days = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="📅 Send number of days for premium:",
            filters=filters.text,
        )
        days = int(ask_days.text.strip())

        ask_plan = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="💎 Send plan type:\n\n- `normal`\n- `ultra`",
            filters=filters.text,
        )
        plan = ask_plan.text.lower().strip()
        if plan not in ["normal", "ultra"]:
            return await safe_action(message.reply_text, "❌ Invalid plan type. Must be 'normal' or 'ultra'.")

        await db.add_premium_user(user_id, days, plan)

        expiry = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
        await safe_action(message.reply_text,
            f"✅ Added **{plan.title()} Premium**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📅 Days: {days}\n"
            f"⏳ Expiry: {expiry}"
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Add Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Add Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS) & filters.private & filters.incoming)
async def remove_premium(client: Client, message: Message):
    try:
        ask_id = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="👤 Send the User ID to remove from premium:",
            filters=filters.text,
        )
        
        user_id = int(ask_id.text.strip())
        user = await db.get_premium_user(user_id)
        if not user:
            return await safe_action(message.reply_text, f"ℹ️ User `{user_id}` is **not premium**.")

        await db.remove_premium_user(user_id)
        await safe_action(message.reply_text, f"✅ Removed premium from {user_id}.")
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Remove Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Remove Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("list_premium") & filters.user(ADMINS) & filters.private & filters.incoming)
async def list_premium(client: Client, message: Message):
    try:
        users = await db.list_premium_users()
        if not users:
            return await safe_action(message.reply_text, "ℹ️ No premium users found.")

        text = "👑 **Premium Users List** 👑\n\n"
        for u in users:
            user_id = u["id"]
            plan = u.get("plan_type", "normal").title()
            expiry = u.get("expiry_time")

            try:
                user = await client.get_users(user_id)
                username = f"@{user.username}" if user.username else "—"
            except Exception:
                username = "—"

            if expiry:
                exp_str = expiry.strftime("%Y-%m-%d %H:%M")
                remaining = expiry - datetime.utcnow()
                days_left = remaining.days
                text += f"• `{user_id}` | {username} | {plan} | Expires: {exp_str} ({days_left} days left)\n"
            else:
                text += f"• `{user_id}` | {username} | {plan} | ❌ Expired\n"

        if len(text) > 4000:
            await safe_action(message.reply_document,
                document=("premium_users.txt", text.encode("utf-8")),
                caption="📄 Premium Users List"
            )
        else:
            await safe_action(message.reply_text, text)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ List Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ List Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("check_premium") & filters.user(ADMINS) & filters.private & filters.incoming)
async def check_premium(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            return await safe_action(message.reply_text, "❌ Usage: /check_premium <user_id>")

        user_id = int(message.command[1])
        user = await db.get_premium_user(user_id)

        if not user:
            return await safe_action(message.reply_text, f"ℹ️ User `{user_id}` is **not premium**.")

        plan = user.get("plan_type", "normal").title()
        expiry = user.get("expiry_time")

        if expiry and expiry > datetime.utcnow():
            remaining = expiry - datetime.utcnow()
            days_left = remaining.days
            exp_str = expiry.strftime("%Y-%m-%d %H:%M")
            await safe_action(message.reply_text,
                f"👤 **User:** `{user_id}`\n"
                f"💎 **Plan:** {plan}\n"
                f"📅 **Expiry:** {exp_str}\n"
                f"⏳ **Remaining:** {days_left} days"
            )
        else:
            await safe_action(message.reply_text,
                f"👤 **User:** `{user_id}`\n"
                f"💎 **Plan:** {plan}\n"
                f"❌ Premium expired."
            )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Check Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Check Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.private)
async def broadcast(client, message):
    try:
        if message.reply_to_message:
            b_msg = message.reply_to_message
        else:
            b_msg = await safe_action(client.ask,
                message.chat.id,
                "📩 Send the message to broadcast\n\n/cancel to stop.",
            )

            if b_msg.text and b_msg.text.lower() == '/cancel':
                return await safe_action(message.reply, '🚫 Broadcast cancelled.')

        sts = await safe_action(message.reply_text, "⏳ Broadcast starting...")
        start_time = time.time()
        total_users = await db.total_users_count()

        done = blocked = deleted = failed = success = 0

        users = await db.get_all_users()
        async for user in users:
            try:
                if "id" in user:
                    pti, sh = await broadcast_messagesx(int(user["id"]), b_msg)
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
            except Exception:
                failed += 1
                done += 1
                continue

        time_taken = timedelta(seconds=int(time.time() - start_time))
        #speed = round(done / (time.time()-start_time), 2) if done > 0 else 0
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
            f"⚠️ Broadcast Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Broadcast Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("stats") & filters.user(ADMINS) & filters.private & filters.incoming)
async def stats(client, message):
    try:
        username = client.me.username
        users_count = await db.total_users_count()

        uptime = str(timedelta(seconds=int(time.time() - START_TIME)))

        await safe_action(message.reply,
            f"📊 Status for @{username}\n\n"
            f"👤 Users: {users_count}\n"
            f"⏱ Uptime: {uptime}\n",
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Stats Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Stats Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command('restart') & filters.user(ADMINS) & filters.private)
async def restart(client, message):
    msg = await safe_action(message.reply_text, f"🔄 Restarting the server...\n[░░░░░░░░░░] 0%", quote=True)

    for i in range(1, 11):
        await asyncio.sleep(0.5)
        bar = '▓' * i + '░' * (10 - i)
        await safe_action(msg.edit_text, f"🔄 Restarting the server...\n[{bar}] {i*10}%")

    await safe_action(msg.edit_text, f"✅ Server restarted successfully!")

    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(f"⚠️ Error restarting the server: {e}")
        return await safe_action(msg.edit_text,
            f"❌ Failed to restart the server.\n\nError: {e}"
        )

@Client.on_message(filters.command("contact") & filters.private & filters.incoming)
async def contact(client, message):
    try:
        if message.reply_to_message:
            c_msg = message.reply_to_message
        else:
            c_msg = await safe_action(client.ask,
                message.from_user.id,
                "📩 Now send me your contact message\n\nType /cancel to stop.",
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
            for admin_id in ADMINS:
                await safe_action(c_msg.copy, admin_id, caption=final_caption)
        elif c_msg.text:
            content = f"\n💬 Message:\n{c_msg.text}"
            final_text = header + content
            for admin_id in ADMINS:
                await safe_action(client.send_message, admin_id, final_text)
        else:
            for admin_id in ADMINS:
                await safe_action(client.send_message, admin_id, header)

        await safe_action(message.reply_text, "✅ Your message has been sent to the admin!")
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Contact Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Contact Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.private & filters.reply)
async def reply(client, message):
    try:
        if not message.reply_to_message:
            return

        if not message.reply_to_message.text or "🆔 ID:" not in message.reply_to_message.text:
            return

        try:
            user_id_line = [line for line in message.reply_to_message.text.splitlines() if line.startswith("🆔 ID:")][0]
            user_id = int(user_id_line.replace("🆔 ID:", "").strip(" `"))
        except:
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
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Reply Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Reply Error: {e}")
        print(traceback.format_exc())

async def show_clone_menu(client, message, user_id, page: int = 1, per_page: int = 6):
    try:
        is_admin = user_id in ADMINS

        if is_admin:
            bots_cursor = await db.get_all_clone()
            clones = await bots_cursor.to_list(None)
        else:
            clones = await db.get_clones_by_user(user_id)
        
        buttons = []
        if is_admin:
            total_clones = len(clones)
            start = (page - 1) * per_page
            end = start + per_page
            clones_page = clones[start:end]
        else:
            clones_page = clones

        if clones_page:
            for clone in clones_page:
                bot_name = clone.get("name") or f"Clone {clone['bot_id']}"
                buttons.append([
                    InlineKeyboardButton(
                        f"⚙️ {bot_name}",
                        callback_data=f"manage_{clone['bot_id']}"
                    )
                ])

        if is_admin and total_clones > per_page:
            nav_buttons = []
            if page > 1:
                nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"clone_page_{page-1}"))
            if end < total_clones:
                nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"clone_page_{page+1}"))
            if nav_buttons:
                buttons.append(nav_buttons)

        is_vip = await db.is_premium(user_id, required_plan="vip")
        if is_vip or not clones:
            buttons.append([InlineKeyboardButton("➕ Add Clone", callback_data="add_clone")])

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="start")])

        await safe_action(message.edit_text,
            script.MANAGEC_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Clone Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Clone Menu Error: {e}")
        print(traceback.format_exc())

async def show_text_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('✏️ Edit', callback_data=f'edit_text_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_text_{bot_id}'),
            InlineKeyboardButton('🔄 Default', callback_data=f'default_text_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'start_message_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.ST_TXT_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Text Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Text Menu Error: {e}")
        print(traceback.format_exc())

async def show_photo_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('➕ Add', callback_data=f'add_photo_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_photo_{bot_id}'),
            InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_photo_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'start_message_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.ST_PIC_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Photo Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Photo Menu Error: {e}")
        print(traceback.format_exc())

async def show_caption_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('➕ Add', callback_data=f'add_caption_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_caption_{bot_id}'),
            InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_caption_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'start_message_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Caption Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Caption Menu Error: {e}")
        print(traceback.format_exc())

async def show_button_menu(client, message, bot_id):
    try:
        clone = await db.get_clone(bot_id)
        owner_id = clone.get("user_id")
        buttons_data = clone.get("button", [])
        buttons = []

        for i, btn in enumerate(buttons_data):
            url = btn.get("url", "").strip()
            name = btn.get("name", "Unnamed")

            buttons.append(
                [InlineKeyboardButton(name, url=url),
                  InlineKeyboardButton("❌", callback_data=f"remove_button_{i}_{bot_id}")]
            )

        is_premium_user = await db.is_premium(owner_id)

        if is_premium_user or len(buttons_data) < 3:
            buttons.append([InlineKeyboardButton("➕ Add Button", callback_data=f"add_button_{bot_id}")])

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"start_message_{bot_id}")])

        await safe_action(message.edit_text,
            text=script.BUTTON_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Button Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Button Menu Error: {e}")
        print(traceback.format_exc())

async def show_header_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('➕ Add', callback_data=f'add_header_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_header_{bot_id}'),
            InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_header_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'link_message_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.HEADER_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Header Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Header Menu Error: {e}")
        print(traceback.format_exc())

async def show_footer_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('➕ Add', callback_data=f'add_footer_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_footer_{bot_id}'),
            InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_footer_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'link_message_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.FOOTER_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Footer Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Footer Menu Error: {e}")
        print(traceback.format_exc())

async def show_fsub_menu(client, message, bot_id):
    try:
        clone = await db.get_clone(bot_id)
        owner_id = clone.get("user_id")
        fsub_data = clone.get("force_subscribe", [])

        buttons = []
        new_fsub_data = []
        text = ""

        for i, btn in enumerate(fsub_data):
            target = btn.get("limit", 0)
            joined = btn.get("joined", 0)
            ch_name = btn.get("name", "Unknown")
            ch_link = btn.get("link", None)
            mode = btn.get("mode", "normal")

            if target != 0 and joined >= target:
                status = "✅ Completed"
            elif target == 0:
                status = "♾️ Unlimited"
            else:
                status = "⏳ Active"

            progress = f"👥 {joined}" if target == 0 else f"👥 {joined}/{target}"

            text += f"**{ch_name}** ({'✅ Normal' if mode=='normal' else '📝 Request'})\n{progress} | {status}\n\n"

            row = []
            if ch_link:
                row.append(InlineKeyboardButton(ch_name, url=ch_link))
            else:
                row.append(InlineKeyboardButton(ch_name, callback_data="noop"))

            row.append(InlineKeyboardButton("❌", callback_data=f"remove_fsub_{i}_{bot_id}"))
            buttons.append(row)

            new_fsub_data.append(btn)

        await db.update_clone(bot_id, {"force_subscribe": new_fsub_data})

        is_premium_user = await db.is_premium(owner_id)

        if is_premium_user or len(fsub_data) < 4:
            buttons.append([InlineKeyboardButton("➕ Add Channel", callback_data=f"add_fsub_{bot_id}")])

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")])

        if not fsub_data:
            text = '📢 No active Force Subscribe channels.\n\n➕ Add one below:'

        await safe_action(message.edit_text,
            text=f"{script.FSUB_TXT}\n\n{text}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Force Subscribe Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Force Subscribe Menu Error: {e}")
        print(traceback.format_exc())

async def show_token_menu(client, message, bot_id):
    try:
        clone = await db.get_clone(bot_id)
        current = clone.get("access_token", False)
        shorten_link = clone.get("at_shorten_link", None)
        shorten_api = clone.get("at_shorten_api", None)
        validity = str(clone.get("at_validity", "24h"))
        tutorial = clone.get("at_tutorial", None)
        renew_log = clone.get("at_renew_log", {})

        today = datetime.now().strftime("%Y-%m-%d")
        today_count = renew_log.get(today, 0)

        num_str = "".join(filter(str.isdigit, validity)) or "0"
        unit_char = "".join(filter(str.isalpha, validity)) or "h"

        try:
            number = int(num_str)
        except:
            number = 0

        unit_map = {"d": "day(s)", "h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
        unit = unit_map.get(unit_char.lower(), "hour(s)")

        if current:
            buttons = [
                [InlineKeyboardButton("⏱ Validity", callback_data=f"at_validty_{bot_id}"),
                InlineKeyboardButton("📘 Tutorial", callback_data=f"at_tutorial_{bot_id}"),
                InlineKeyboardButton("❌ Disable", callback_data=f"at_status_{bot_id}")]
            ]

            if tutorial:
                text_msg = f"📘 Tutorial: <a href='{tutorial}'>Click Here</a>\n"
            else:
                text_msg = f"📘 Tutorial: Not Set\n"

            status = (
                f"🟢 Enabled\n\n"
                f"🔗 Shorten Link: {shorten_link or 'Not Set'}\n"
                f"🛠 Shorten API: {shorten_api or 'Not Set'}\n"
                f"⏱ Validity: {number} {unit}\n"
                f"{text_msg}"
                f"🔄 Renewed Today: {today_count} times\n\n"
            )
        else:
            buttons = []
            buttons.append([InlineKeyboardButton("✅ Enable", callback_data=f"at_status_{bot_id}")])
            status = "🔴 Disabled"

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")])
        await safe_action(message.edit_text,
            text=script.TOKEN_TXT.format(status=f"{status}"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Token Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Token Menu Error: {e}")
        print(traceback.format_exc())

async def show_validity_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('✏️ Edit', callback_data=f'edit_atvalidity_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_atvalidity_{bot_id}'),
            InlineKeyboardButton('🔄 Default', callback_data=f'default_atvalidity_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'access_token_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.AT_VALIDITY_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Validity Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Validity Menu Error: {e}")
        print(traceback.format_exc())

async def show_tutorial_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('➕ Add', callback_data=f'add_attutorial_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_attutorial_{bot_id}'),
            InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_attutorial_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'access_token_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.AT_TUTORIAL_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Tutorial Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Tutorial Menu Error: {e}")
        print(traceback.format_exc())

async def show_post_menu(client, message, bot_id):
    try:
        clone = await db.get_clone(bot_id)
        current = clone.get("auto_post", False)
        image = clone.get("ap_image", None)
        sleep = str(clone.get("ap_sleep", "1h"))
        mode = clone.get("ap_mode", "single")

        num_str = "".join(filter(str.isdigit, sleep)) or "0"
        unit_char = "".join(filter(str.isalpha, sleep)) or "h"

        try:
            number = int(num_str)
        except:
            number = 0

        unit_map = {"d": "day(s)", "h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
        unit = unit_map.get(unit_char.lower(), "hour(s)")

        if current:
            buttons = [
                [InlineKeyboardButton('🖼️ Image', callback_data=f'apimage_{bot_id}'),
                InlineKeyboardButton("⏱ Sleep", callback_data=f"ap_sleep_{bot_id}"),
                InlineKeyboardButton("❌ Disable", callback_data=f"ap_status_{bot_id}")]
            ]

            status = (
                f"🟢 Enabled\n\n"
                f"⏱ Sleep: {number} {unit}\n"
                f"⚡ Mode: {mode}\n\n"
            )
        else:
            buttons = []
            buttons.append([InlineKeyboardButton("✅ Enable", callback_data=f"ap_status_{bot_id}")])
            status = "🔴 Disabled"

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")])
        await safe_action(message.edit_text,
            text=script.AUTO_POST_TXT.format(status=f"{status}"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Post Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Post Menu Error: {e}")
        print(traceback.format_exc())

async def show_image_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('➕ Add', callback_data=f'add_apimage_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_apimage_{bot_id}'),
            InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_apimage_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'auto_post_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.AP_IMG_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Image Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Image Menu Error: {e}")
        print(traceback.format_exc())

async def show_sleep_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('✏️ Edit', callback_data=f'edit_apsleep_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_apsleep_{bot_id}'),
            InlineKeyboardButton('🔄 Default', callback_data=f'default_apsleep_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'auto_post_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.AP_SLEEP_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Sleep Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Sleep Menu Error: {e}")
        print(traceback.format_exc())

async def show_premium_menu(client, message, bot_id):
    try:
        clone = await db.get_clone(bot_id)
        if not clone:
            await safe_action(message.edit_text, "❌ Clone not found.")
            return

        premium_user = clone.get("premium_user", [])
        pu_list_lines = []

        for pu in premium_user:
            user_id_int = None
            name = None

            if isinstance(pu, dict):
                user_id_int = pu.get("user_id")
                name = pu.get("name")
            else:
                try:
                    user_id_int = int(pu)
                except ValueError:
                    user_id_int = pu

            if not name:
                user = await db.col.find_one({"id": user_id_int})
                name = user.get("name") if user else None

            if not name:
                try:
                    tg_user = await client.get_users(user_id_int)
                    name = tg_user.first_name
                except:
                    name = str(user_id_int)

            if user_id_int:
                pu_list_lines.append(f"👤 {name} (`{user_id_int}`)")

        pu_list_text = "\n".join(pu_list_lines) if pu_list_lines else "No premium users yet."

        buttons = [
            [
                InlineKeyboardButton("➕ Add", callback_data=f"add_pu_{bot_id}"),
                InlineKeyboardButton("➖ Remove", callback_data=f"remove_premium_user_{bot_id}"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")]
        ]

        text = script.PREMIUM_TXT + f"\n\n👥 **Current Premium Users:**\n{pu_list_text}"

        await safe_action(message.edit_text,text=text, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Premium User Menu Error:\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Premium User Menu Error: {e}")
        print(traceback.format_exc())

async def show_time_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('✏️ Edit', callback_data=f'edit_adtime_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_adtime_{bot_id}'),
            InlineKeyboardButton('🔄 Default', callback_data=f'default_adtime_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'auto_delete_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.AD_TIME_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Time Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Time Menu Error: {e}")
        print(traceback.format_exc())

async def show_message_menu(client, message, bot_id):
    try:
        buttons = [
            [InlineKeyboardButton('✏️ Edit', callback_data=f'edit_admessage_{bot_id}'),
            InlineKeyboardButton('👁️ See', callback_data=f'see_admessage_{bot_id}'),
            InlineKeyboardButton('🔄 Default', callback_data=f'default_admessage_{bot_id}')],
            [InlineKeyboardButton('⬅️ Back', callback_data=f'auto_delete_{bot_id}')]
        ]
        await safe_action(message.edit_text,
            text=script.AD_MSG_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Message Menu Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Message Menu Error: {e}")
        print(traceback.format_exc())

async def show_moderator_menu(client, message, bot_id):
    try:
        clone = await db.get_clone(bot_id)
        moderators = clone.get("moderators", [])

        mod_list_lines = []
        for mod in moderators:
            try:
                user_id_int = int(mod)
            except ValueError:
                user_id_int = mod

            user = await db.col.find_one({"id": user_id_int})
            name = user.get("name") if user else mod
            mod_list_lines.append(f"👤 {name} (`{mod}`)")

        mod_list_text = "\n".join(mod_list_lines)

        buttons = [
            [
                InlineKeyboardButton("➕ Add", callback_data=f"add_moderator_{bot_id}"),
                InlineKeyboardButton("➖ Remove", callback_data=f"remove_moderator_{bot_id}"),
                InlineKeyboardButton("🔁 Transfer", callback_data=f"transfer_moderator_{bot_id}")
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")]
        ]

        text = script.MODERATOR_TXT
        if mod_list_text:
            text += f"\n\n👥 **Current Moderators:**\n{mod_list_text}"

        await safe_action(message.edit_text, text=text, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Show Moderator Menu Error:\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Show Moderator Menu Error: {e}")
        print(traceback.format_exc())

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    try:
        user_id = query.from_user.id
        data = query.data

        # Start Menu
        if data == "start":
            await safe_action(query.answer)
            buttons = [
                [InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
                 InlineKeyboardButton('ℹ️ About', callback_data='about')],
                [InlineKeyboardButton('🤖 Create Your Own Clone', callback_data='clone')],
                [InlineKeyboardButton('🌟 Buy Premium', callback_data='premium')],
                [InlineKeyboardButton('🔒 Close', callback_data='close')]
            ]
            me = await client.get_me()
            await safe_action(query.message.edit_text,
                text=script.START_TXT.format(user=query.from_user.mention, bot=me.mention),
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Help
        elif data == "help":
            await safe_action(query.answer)
            buttons = [[InlineKeyboardButton('⬅️ Back', callback_data='start')]]
            await safe_action(query.message.edit_text,
                text=script.HELP_TXT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # About
        elif data == "about":
            await safe_action(query.answer)
            buttons = [[InlineKeyboardButton('⬅️ Back', callback_data='start')]]
            me = await client.get_me()
            await safe_action(query.message.edit_text,
                text=script.ABOUT_TXT.format(bot=me.mention),
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Clone Menu
        elif data == "clone":
            await safe_action(query.answer)
            await show_clone_menu(client, query.message, user_id)

        # Clone Menu Page
        elif data.startswith("clone_page_"):
            await safe_action(query.answer)
            page = int(data.replace("clone_page_", ""))
            await show_clone_menu(client, query.message, user_id, page=page)

        # Add Clone
        elif data == "add_clone":
            await safe_action(query.answer)
            CLONE_TOKEN[user_id] = query.message
            buttons = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_add_clone")]]
            await safe_action(query.message.edit_text,
                text=script.CLONE_TXT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Cancel Add Clone
        elif data == "cancel_add_clone":
            await safe_action(query.answer)
            CLONE_TOKEN.pop(user_id, None)
            await show_clone_menu(client, query.message, user_id)

        # Clone Manage Menu
        elif data.startswith("manage_"):
            bot_id = data.split("_", 1)[1]
            clone = await db.get_clone(bot_id)
            if not clone:
                return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

            await safe_action(query.answer)
            last_active = clone.get("last_active", int(time.time()))
            if time.time() - last_active > 7 * 24 * 60 * 60:
                await db.update_clone(bot_id, {"active": False})
                clone["active"] = False
                await safe_action(message.reply_text, f"Your clone @{clone['username']} was automatically deactivated by our system due to being inactive for the last 7 days.\n\nYou can reactivate it anytime using /start.")

            active = clone.get("active", True)
            activate_text = "✅ Activate" if active else "❌ Deactivated"

            buttons = [
                [InlineKeyboardButton('📝 Start Message', callback_data=f'start_message_{bot_id}'),
                 InlineKeyboardButton('📢 Channel Message', callback_data=f'link_message_{bot_id}')],
                [InlineKeyboardButton('🔔 Force Subscribe', callback_data=f'force_subscribe_{bot_id}'),
                 InlineKeyboardButton('🔑 Access Token', callback_data=f'access_token_{bot_id}')],
                [InlineKeyboardButton('📤 Auto Post', callback_data=f'auto_post_{bot_id}'),
                 InlineKeyboardButton('🌟 Premium User', callback_data=f'premium_user_{bot_id}')],
                [InlineKeyboardButton('⏳ Auto Delete', callback_data=f'auto_delete_{bot_id}'),
                 InlineKeyboardButton('🚫 Forward Protect', callback_data=f'forward_protect_{bot_id}')],
                [InlineKeyboardButton('🛡 Moderator', callback_data=f'moderator_{bot_id}'),
                 InlineKeyboardButton('📊 Status', callback_data=f'status_{bot_id}')],
                [InlineKeyboardButton(activate_text, callback_data=f'activate_deactivate_{bot_id}'),
                 InlineKeyboardButton('🔄 Restart', callback_data=f'restart_{bot_id}')],
                [InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_{bot_id}')],
                [InlineKeyboardButton('⬅️ Back', callback_data='clone')]
            ]
            await safe_action(query.message.edit_text,
                text=script.CUSTOMIZEC_TXT.format(username=f"@{clone['username']}"),
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Handle per-clone actions
        elif any(data.startswith(prefix) for prefix in [
            "start_message_", "start_text_", "edit_text_", "cancel_edit_", "see_text_", "default_text_", "start_photo_", "add_photo_", "cancel_addphoto_", "see_photo_", "delete_photo_", "start_caption_", "add_caption_", "cancel_addcaption_", "see_caption_", "delete_caption_", "start_button_", "add_button_", "cancel_addbutton_", "remove_button_",
            "link_message_", "word_filter_", "wf_status_", "media_filter_", "mf_status_", "random_caption_", "rc_status_", "header_", "add_header_", "cancel_addheader_", "see_header_", "delete_header_", "footer_", "add_footer_", "cancel_addfooter_", "see_footer_", "delete_footer_",
            "force_subscribe_", "add_fsub_", "fsub_mode_", "cancel_addfsub_", "remove_fsub_",
            "access_token_", "at_status_", "cancel_at_", "at_validty_", "edit_atvalidity_", "cancel_editatvalidity_", "see_atvalidity_", "default_atvalidity_", "at_tutorial_", "add_attutorial_", "cancel_addattutorial_", "see_attutorial_", "delete_attutorial_",
            "auto_post_", "ap_status_", "ap_mode_", "cancel_autopost_", "apimage", "add_apimage_", "cancel_addapimage_", "see_apimage_", "delete_apimage_", "ap_sleep_", "edit_apsleep_", "cancel_editapsleep_", "see_apsleep_", "default_apsleep_",
            "premium_user_", "cancel_pu_", "add_pu_", "cancel_addpu_", "remove_premium_user_", "remove_pu_",
            "auto_delete_", "ad_status_", "ad_time_", "edit_adtime_", "cancel_editadtime_", "see_adtime_", "default_adtime_", "ad_message_", "edit_admessage_", "cancel_editadmessage_", "see_admessage_", "default_admessage_",
            "forward_protect_", "fp_status_",
            "moderator_", "add_moderator_", "cancel_addmoderator_", "remove_moderator_", "remove_mod_", "transfer_moderator_", "transfer_mod_",
            "status_", "activate_deactivate_", "restart_", "delete_", "delete_clone_"
        ]):

            action = None
            bot_id = None
            pu_id = None
            mod_id = None
            mode = None
            chat_id = None
            index = None

            if data.startswith("remove_button_"):
                _, _, index, bot_id = data.split("_", 3)
                action = "remove_button"
                index = int(index)
            elif data.startswith("fsub_mode_"):
                mode, bot_id = data[len("fsub_mode_"):].rsplit("_", 1)
                if mode not in ["normal", "request"]:
                    mode = "normal"
                action = "fsub_mode"
            elif data.startswith("remove_fsub_"):
                _, _, index, bot_id = data.split("_", 3)
                action = "remove_fsub"
                index = int(index)
            elif data.startswith("ap_mode_"):
                mode_bot, chat_id_str = data[len("ap_mode_"):].rsplit("_", 1)
                chat_id = int(chat_id_str)
                parts = mode_bot.split("_")
                mode = parts[0]
                bot_id = parts[1]
                action = "ap_mode"
            elif data.startswith("remove_pu_"):
                _, _, bot_id_str, pu_id_str = data.split("_", 3)
                bot_id = int(bot_id_str)
                pu_id = int(pu_id_str)
                action = "remove_pu"
            elif data.startswith("remove_mod_"):
                _, _, bot_id, mod_id = data.split("_", 3)
                action = "remove_mod"
            elif data.startswith("transfer_mod_"):
                _, _, bot_id, mod_id = data.split("_", 3)
                action = "transfer_mod"
            else:
                action, bot_id = data.rsplit("_", 1)

            clone = await db.get_clone(bot_id)
            if not clone:
                return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

            last_active = clone.get("last_active", int(time.time()))
            if time.time() - last_active > 7 * 24 * 60 * 60:
                await db.update_clone(bot_id, {"active": False})
                clone["active"] = False
                await safe_action(message.reply_text, f"Your clone @{clone['username']} was automatically deactivated by our system due to being inactive for the last 7 days.\n\nYou can reactivate it anytime using /start.")

            active = clone.get("active", True)

            await db.update_clone(bot_id, {"last_active": int(time.time())})

            # Start Message Menu
            if action == "start_message":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                buttons = [
                    [InlineKeyboardButton('✏️ Start Text', callback_data=f'start_text_{bot_id}'),
                     InlineKeyboardButton('🖼️ Start Photo', callback_data=f'start_photo_{bot_id}')],
                    [InlineKeyboardButton('💬 Start Caption', callback_data=f'start_caption_{bot_id}'),
                     InlineKeyboardButton('🔘 Start Button', callback_data=f'start_button_{bot_id}')],
                    [InlineKeyboardButton('⬅️ Back', callback_data=f'manage_{bot_id}')]
                ]
                await safe_action(query.message.edit_text,
                    text=script.ST_MSG_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Start Text Menu
            elif action == "start_text":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_text_menu(client, query.message, bot_id)

            # Edit Text
            elif action == "edit_text":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                START_TEXT[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_edit_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_ST_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Edit Text
            elif action == "cancel_edit":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                START_TEXT.pop(user_id, None)
                await show_text_menu(client, query.message, bot_id)

            # See Start Text
            elif action == "see_text":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                start_text = clone.get("start_text", script.START_TXT)
                preview = start_text[:150]
                if len(start_text) > 150:
                    preview += "..."
                await safe_action(query.answer, f"📝 Current Start Text:\n\n{preview}", show_alert=True)

            # Default Start Text
            elif action == "default_text":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await db.update_clone(bot_id, {"start_text": script.START_TXT})
                await safe_action(query.answer, f"🔄 Start text reset to default.", show_alert=True)

            # Start Photo Menu
            elif action == "start_photo":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_photo_menu(client, query.message, bot_id)
        
            # Add Start Photo
            elif action == "add_photo":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                START_PHOTO[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addphoto_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_ST_PIC,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Add Photo
            elif action == "cancel_addphoto":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                START_PHOTO.pop(user_id, None)
                await show_photo_menu(client, query.message, bot_id)
        
            # See Start Photo
            elif action == "see_photo":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                start_photo = clone.get("start_photo", None)
                if start_photo:
                    await safe_action(client.send_photo,
                        chat_id=query.message.chat.id,
                        photo=start_photo,
                        caption="📌 This is the current start photo for this clone."
                    )
                else:
                    await safe_action(query.answer, "❌ No start photo set for this clone.", show_alert=True)

            # Delete Start Photo
            elif action == "delete_photo":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                start_photo = clone.get("start_photo", None)
                if start_photo:
                    await db.update_clone(bot_id, {"start_photo": None})
                    await safe_action(query.answer, "✨ Successfully deleted your clone start photo.", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No start photo set for this clone.", show_alert=True)

            # Caption Menu
            elif action == "start_caption":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_caption_menu(client, query.message, bot_id)

            # Add Caption
            elif action == "add_caption":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                CAPTION_TEXT[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addcaption_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_CAPTION_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Add Caption
            elif action == "cancel_addcaption":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                CAPTION_TEXT.pop(user_id, None)
                await show_caption_menu(client, query.message, bot_id)

            # See Caption
            elif action == "see_caption":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                caption = clone.get("caption", None)
                if caption:
                    await safe_action(query.answer, f"📝 Current Caption Text:\n\n{caption}", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No caption text set for this clone.", show_alert=True)

            # Delete Caption
            elif action == "delete_caption":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                caption = clone.get("caption", None)
                if caption:
                    await db.update_clone(bot_id, {"caption": None})
                    await safe_action(query.answer, "✨ Successfully deleted your caption text.", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No caption text set for this clone.", show_alert=True)

            # Button Menu
            elif action == "start_button":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_button_menu(client, query.message, bot_id)

            # Add Button
            elif action == "add_button":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                buttons_data = clone.get("button", [])
                if len(buttons_data) >= 3:
                    return await safe_action(query.answer, "❌ You can only add up to 3 buttons.", show_alert=True)

                ADD_BUTTON[user_id] = {
                        "orig_msg": query.message,
                        "bot_id": bot_id,
                        "step": "name"
                    }
                buttons = [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_addbutton_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_BUTTON_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Button
            elif action == "cancel_addbutton":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ADD_BUTTON.pop(user_id, None)
                await show_button_menu(client, query.message, bot_id)

            # Delete Button
            elif action == "remove_button":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                buttons_data = clone.get("button", [])
                if 0 <= index < len(buttons_data):
                    deleted_btn = buttons_data.pop(index)
                    await db.update_clone(bot_id, {"button": buttons_data})
                    await safe_action(query.answer, f"❌ Deleted button: {deleted_btn['name']}", show_alert=True)
                else:
                    await safe_action(query.answer, "Invalid button index!", show_alert=True)

                await show_button_menu(client, query.message, bot_id)

            # Link Message Menu
            elif action == "link_message":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                buttons = [
                    [InlineKeyboardButton('🚫 Word Filter', callback_data=f'word_filter_{bot_id}'),
                     InlineKeyboardButton('🎲 Random Caption', callback_data=f'random_caption_{bot_id}')],
                    [InlineKeyboardButton('🔺 Header Text', callback_data=f'header_{bot_id}'),
                     InlineKeyboardButton('🔻 Footer Text', callback_data=f'footer_{bot_id}')],
                    [InlineKeyboardButton('⬅️ Back', callback_data=f'manage_{bot_id}')]
                ]
                await safe_action(query.message.edit_text,
                    text=script.CH_MSG_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Offensive Word Filter
            elif action == "word_filter":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                current = clone.get("word_filter", False)
                if current:
                    buttons = [[InlineKeyboardButton("❌ Disable", callback_data=f"wf_status_{bot_id}")]]
                    status = "🟢 Enabled"
                else:
                    buttons = [[InlineKeyboardButton("✅ Enable", callback_data=f"wf_status_{bot_id}")]]
                    status = "🔴 Disabled"

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"link_message_{bot_id}")])
                await safe_action(query.message.edit_text,
                    text=script.WORD_FILTER_TXT.format(status=f"{status}"),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Offensive Word Filter Status
            elif action == "wf_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("word_filter", False)
                await db.update_clone(bot_id, {"word_filter": new_value})

                if new_value:
                    status_text = "🟢 **Offensive Word Filter** has been successfully ENABLED!"
                else:
                    status_text = "🔴 **Offensive Word Filter** has been successfully DISABLED!"

                buttons = [[InlineKeyboardButton("⬅️ Back", callback_data=f"word_filter_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Offensive Media Filter
            elif action == "media_filter":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                current = clone.get("media_filter", False)
                if current:
                    buttons = [[InlineKeyboardButton("❌ Disable", callback_data=f"mf_status_{bot_id}")]]
                    status = "🟢 Enabled"
                else:
                    buttons = [[InlineKeyboardButton("✅ Enable", callback_data=f"mf_status_{bot_id}")]]
                    status = "🔴 Disabled"

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"link_message_{bot_id}")])
                await safe_action(query.message.edit_text,
                    text=script.MEDIA_FILTER_TXT.format(status=f"{status}"),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Offensive Media Filter Status
            elif action == "mf_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("media_filter", False)
                await db.update_clone(bot_id, {"media_filter": new_value})

                if new_value:
                    status_text = "🟢 **Offensive Media Filter** has been successfully ENABLED!"
                else:
                    status_text = "🔴 **Offensive Media Filter** has been successfully DISABLED!"

                buttons = [[InlineKeyboardButton("⬅️ Back", callback_data=f"media_filter_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Random Caption
            elif action == "random_caption":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                user_data = await db.is_premium(user_id)
                if not user_data:
                    return await safe_action(query.answer,
                        "🚫 This feature is for premium users only.\n\n"
                        "Contact admin to upgrade.",
                        show_alert=True
                    )

                await safe_action(query.answer)
                current = clone.get("random_caption", False)
                if current:
                    buttons = [[InlineKeyboardButton("❌ Disable", callback_data=f"rc_status_{bot_id}")]]
                    status = "🟢 Enabled"
                else:
                    buttons = [[InlineKeyboardButton("✅ Enable", callback_data=f"rc_status_{bot_id}")]]
                    status = "🔴 Disabled"

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"link_message_{bot_id}")])
                await safe_action(query.message.edit_text,
                    text=script.RANDOM_CAPTION_TXT.format(status=f"{status}"),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Random Caption Status
            elif action == "rc_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("random_caption", False)
                await db.update_clone(bot_id, {"random_caption": new_value})

                if new_value:
                    status_text = "🟢 **Random Caption** has been successfully ENABLED!"
                else:
                    status_text = "🔴 **Random Caption** has been successfully DISABLED!"

                buttons = [[InlineKeyboardButton("⬅️ Back", callback_data=f"random_caption_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Header Menu
            elif action == "header":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_header_menu(client, query.message, bot_id)

            # Add Header
            elif action == "add_header":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                HEADER_TEXT[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addheader_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_HEADER_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Add Header
            elif action == "cancel_addheader":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                HEADER_TEXT.pop(user_id, None)
                await show_header_menu(client, query.message, bot_id)

            # See Header
            elif action == "see_header":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                header = clone.get("header", None)
                if header:
                    await safe_action(query.answer, f"📝 Current Header Text:\n\n{header}", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No header text set for this clone.", show_alert=True)

            # Delete Header
            elif action == "delete_header":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                header = clone.get("header", None)
                if header:
                    await db.update_clone(bot_id, {"header": None})
                    await safe_action(query.answer, "✨ Successfully deleted your header text.", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No header text set for this clone.", show_alert=True)

            # Footer Menu
            elif action == "footer":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_footer_menu(client, query.message, bot_id)

            # Add Footer
            elif action == "add_footer":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                FOOTER_TEXT[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addfooter_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_FOOTER_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Add Footer
            elif action == "cancel_addfooter":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                FOOTER_TEXT.pop(user_id, None)
                await show_footer_menu(client, query.message, bot_id)

            # See Footer
            elif action == "see_footer":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                footer = clone.get("footer", None)
                if footer:
                    await safe_action(query.answer, f"📝 Current Footer Text:\n\n{footer}", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No footer text set for this clone.", show_alert=True)

            # Delete Footer
            elif action == "delete_footer":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                footer = clone.get("footer", None)
                if footer:
                    await db.update_clone(bot_id, {"footer": None})
                    await safe_action(query.answer, "✨ Successfully deleted your footer text.", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No footer text set for this clone.", show_alert=True)

            # Force Subscribe Menu
            elif action == "force_subscribe":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_fsub_menu(client, query.message, bot_id)

            # Add Force Subscribe
            elif action == "add_fsub":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                fsub_data = clone.get("force_subscribe", [])
                if not await db.is_premium(user_id):
                    if len(fsub_data) >= 4:
                        return await safe_action(query.answer, "❌ You can only add up to 4 channel.", show_alert=True)

                await safe_action(query.answer)
                ADD_FSUB[user_id] = {
                    "orig_msg": query.message,
                    "bot_id": bot_id,
                    "step": "channel"
                }
                buttons = [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_addfsub_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_FSUB_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            elif action == "fsub_mode":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                data = ADD_FSUB.get(user_id)
                if not data:
                    return await safe_action(query.answer, "Session expired. Please try again.", show_alert=True)

                await safe_action(query.answer)
                mode = mode
                data["mode"] = mode
                bot_id = data["bot_id"]
                ch = data["channel"]
                target = data["target"]
                link = data.get("link")
                name = data.get("name", "Channel")

                await safe_action(query.message.edit_text, "✏️ Updating your clone's **force subscribe channel**, please wait...")
                try:
                    fsub_data = clone.get("force_subscribe", [])
                    existing = next((x for x in fsub_data if x["channel"] == ch), None)
                    if existing:
                        existing.update({
                            "name": name,
                            "limit": target,
                            "mode": mode,
                            "link": existing.get("link")
                        })
                    else:
                        fsub_data.append({
                            "channel": ch,
                            "name": name,
                            "link": None,
                            "limit": target,
                            "joined": 0,
                            "mode": mode
                        })
                    await db.update_clone(bot_id, {"force_subscribe": fsub_data})
                    await safe_action(query.message.edit_text, "✅ Successfully updated **force subscribe channel**!")
                    await asyncio.sleep(2)
                    await show_fsub_menu(client, query.message, bot_id)
                    ADD_FSUB.pop(user_id, None)
                except Exception as e:
                    await safe_action(client.send_message,
                        LOG_CHANNEL,
                        f"⚠️ Update Force Subscribe Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
                    )
                    print(f"⚠️ Update Force Subscribe Error: {e}")
                    print(traceback.format_exc())
                    await safe_action(query.message.edit_text, f"❌ Failed to update **force subscribe channel**: {e}")
                    await asyncio.sleep(2)
                    await show_fsub_menu(client, query.message, bot_id)
                    ADD_FSUB.pop(user_id, None)
                finally:
                    ADD_FSUB.pop(user_id, None)

            # Cancel Force Subscribe
            elif action == "cancel_addfsub":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ADD_FSUB.pop(user_id, None)
                await show_fsub_menu(client, query.message, bot_id)

            # Delete Force Subscribe
            elif action == "remove_fsub":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                fsub_data = clone.get("force_subscribe", [])
                if 0 <= index < len(fsub_data):
                    deleted_btn = fsub_data.pop(index)
                    await db.update_clone(bot_id, {"force_subscribe": fsub_data})
                    await safe_action(query.answer, f"❌ Deleted Channel: {deleted_btn['name']}", show_alert=True)
                else:
                    await safe_action(query.answer, "Invalid Channel index!", show_alert=True)

                await show_fsub_menu(client, query.message, bot_id)

            # Access Token
            elif action == "access_token":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_token_menu(client, query.message, bot_id)

            # Access Token Status
            elif action == "at_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("access_token", False)
                await db.update_clone(bot_id, {"access_token": new_value})

                if new_value:
                    ACCESS_TOKEN[user_id] = {
                        "orig_msg": query.message,
                        "bot_id": bot_id,
                        "step": "link",
                        "at_shorten_link": None
                    }
                    status_text = "🔗 Please send your **Shorten Link** now."
                    text = "❌ Cancel"
                    callback = f"cancel_at_{bot_id}"
                else:
                    await db.update_clone(
                        bot_id,
                        {"access_token": False, "at_shorten_link": None, "at_shorten_api": None}
                    )
                    status_text = "🔴 Access Token has been successfully DISABLED!"
                    text = "⬅️ Back"
                    callback = f"access_token_{bot_id}"

                buttons = [[InlineKeyboardButton(text, callback_data=callback)]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Access Token
            elif action == "cancel_at":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ACCESS_TOKEN.pop(user_id, None)
                await db.update_clone(bot_id, {"access_token": False})
                await show_token_menu(client, query.message, bot_id)

            # Access Token Validity Menu
            elif action == "at_validty":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_validity_menu(client, query.message, bot_id)

            # Edit Access Token Validity
            elif action == "edit_atvalidity":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AT_VALIDITY[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_editatvalidity_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="⏱ Please provide the new **Access Token Validity** in **Seconds/Minutes/hours** (e.g., `30s` for 30 second, `5m` for 5 minute, `1h` for 1 hour):",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Access Token Validity
            elif action == "cancel_editatvalidity":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AT_VALIDITY.pop(user_id, None)
                await show_validity_menu(client, query.message, bot_id)

            # See Access Token Validity
            elif action == "see_atvalidity":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                at_validity = str(clone.get("at_validity", "24h"))

                num_str = "".join(filter(str.isdigit, at_validity)) or "0"
                unit_char = "".join(filter(str.isalpha, at_validity)) or "h"

                try:
                    number = int(num_str)
                except:
                    number = 0

                unit_map = {"h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
                unit = unit_map.get(unit_char.lower(), "hour(s)")

                await safe_action(query.answer, f"📝 Current Access Token Validity:\n\n{number} {unit}", show_alert=True)

            # Default Access Token Validity
            elif action == "default_atvalidity":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await db.update_clone(bot_id, {"at_validity": "24h"})
                await safe_action(query.answer, f"🔄 Access token validity reset to default.", show_alert=True)

            # Access Token Tutorial
            elif action == "at_tutorial":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_tutorial_menu(client, query.message, bot_id)

            # Add Access Token Tutorial
            elif action == "add_attutorial":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AT_TUTORIAL[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_editadmessage_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="🔗 Please provide the updated **Access Token Tutorial** link:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Access Token Tutorial
            elif action == "cancel_addattutorial":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AT_TUTORIAL.pop(user_id, None)
                await show_tutorial_menu(client, query.message, bot_id)

            # See Access Token Tutorial
            elif action == "see_attutorial":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                at_tutorial = clone.get("at_tutorial", None)
                if at_tutorial:
                    await safe_action(query.answer, f"📝 Current Access Token Tutorial:\n\n{at_tutorial}", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No access token tutorial set for this clone.", show_alert=True)

            # Delete Access Token Tutorial
            elif action == "delete_attutorial":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                at_tutorial = clone.get("at_tutorial", None)
                if at_tutorial:
                    await db.update_clone(bot_id, {"at_tutorial": None})
                    await safe_action(query.answer, "✨ Successfully deleted your clone access token tutorial link.", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No access token tutorial set for this clone.", show_alert=True)

            # Auto Post
            elif action == "auto_post":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                user_data = await db.get_premium_user(user_id)
                if not user_data:
                    return await safe_action(query.answer,
                        "🚫 This feature is for premium users only.\n\n"
                        "Contact admin to upgrade.",
                        show_alert=True
                    )

                plan_type = user_data.get("plan_type", "normal")

                if plan_type not in ["ultra", "vip"]:
                    return await safe_action(query.answer,
                        "🚫 This feature is available only for ultra & vip premium users.\n\n"
                        "Upgrade to access.",
                        show_alert=True
                    )

                await safe_action(query.answer)
                await show_post_menu(client, query.message, bot_id)

            # Auto Post Status
            elif action == "ap_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("auto_post", False)
                await db.update_clone(bot_id, {"auto_post": new_value})

                if new_value:
                    AUTO_POST[user_id] = (query.message, bot_id)
                    status_text = script.AP_STATUS
                    text = "❌ Cancel"
                    callback = f"cancel_autopost_{bot_id}"
                else:
                    await db.update_clone(bot_id, {"auto_post": False, "ap_channel": None})
                    status_text = "🔴 Auto Post has been successfully DISABLED!"
                    text = "⬅️ Back"
                    callback = f"auto_post_{bot_id}"

                buttons = [[InlineKeyboardButton(text, callback_data=callback)]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Auto Post
            elif action == "cancel_autopost":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AUTO_POST.pop(user_id, None)
                await db.update_clone(bot_id, {"auto_post": False})
                await show_post_menu(client, query.message, bot_id)

            # Auto Post Mode
            elif action == "ap_mode":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await safe_action(query.message.edit_text, "✏️ Updating **auto post**, please wait...")
                try:
                    await db.update_clone(bot_id, {
                        "auto_post": True,
                        "ap_channel": chat_id,
                        "ap_mode": mode
                    })
                    asyncio.create_task(auto_post_clone(bot_id, db, chat_id))
                    await safe_action(query.message.edit_text, "✅ Successfully updated **auto post**!")
                    await asyncio.sleep(2)
                    await show_post_menu(client, query.message, bot_id)
                    AUTO_POST.pop(user_id, None)
                except Exception as e:
                    await db.update_clone(bot_id, {"auto_post": False, "ap_channel": None})
                    await safe_action(client.send_message, LOG_CHANNEL, f"⚠️ Update Auto Post Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>.")
                    await safe_action(query.message.edit_text, f"❌ Failed to update **auto post**: {e}")
                    await asyncio.sleep(2)
                    await show_post_menu(client, query.message, bot_id)
                    AUTO_POST.pop(user_id, None)
                finally:
                    AUTO_POST.pop(user_id, None)

            # Auto Post Image Menu
            elif action == "apimage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_image_menu(client, query.message, bot_id)
        
            # Add Auto Post Image
            elif action == "add_apimage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AP_IMAGE[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addphoto_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text=script.EDIT_AP_IMG,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Add Auto Post Image
            elif action == "cancel_addapimage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AP_IMAGE.pop(user_id, None)
                await show_image_menu(client, query.message, bot_id)
        
            # See Auto Post Image
            elif action == "see_apimage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                auto_post_image = clone.get("ap_image", None)
                if auto_post_image:
                    await safe_action(client.send_photo,
                        chat_id=query.message.chat.id,
                        photo=auto_post_image,
                        caption="📌 This is the current auto post image for this clone."
                    )
                else:
                    await safe_action(query.answer, "❌ No auto post image set for this clone.", show_alert=True)

            # Delete Auto Post Image
            elif action == "delete_apimage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                auto_post_image = clone.get("ap_image", None)
                if auto_post_image:
                    await db.update_clone(bot_id, {"ap_image": None})
                    await safe_action(query.answer, "✨ Successfully deleted your clone auto post image.", show_alert=True)
                else:
                    await safe_action(query.answer, "❌ No auto post image set for this clone.", show_alert=True)

            # Auto Post Sleep Menu
            elif action == "ap_sleep":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_sleep_menu(client, query.message, bot_id)

            # Edit Auto Post Sleep
            elif action == "edit_apsleep":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AP_SLEEP[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_editapsleep_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="⏱ Please provide the new **Auto Post Sleep** in **Seconds/Minutes/hours** (e.g., `30s` for 30 second, `5m` for 5 minute, `1h` for 1 hour):",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Auto Post Sleep
            elif action == "cancel_editapsleep":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AP_SLEEP.pop(user_id, None)
                await show_sleep_menu(client, query.message, bot_id)

            # See Auto Post Sleep
            elif action == "see_apsleep":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                ap_sleep = str(clone.get("ap_sleep", "1h"))

                num_str = "".join(filter(str.isdigit, ap_sleep)) or "0"
                unit_char = "".join(filter(str.isalpha, ap_sleep)) or "h"

                try:
                    number = int(num_str)
                except:
                    number = 0

                unit_map = {"h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
                unit = unit_map.get(unit_char.lower(), "hour(s)")

                await safe_action(query.answer, f"📝 Current Auto Post Sleep:\n\n{number} {unit}", show_alert=True)

            # Default Auto Post Sleep
            elif action == "default_apsleep":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await db.update_clone(bot_id, {"ap_sleep": "1h"})
                await safe_action(query.answer, f"🔄 Auto post sleep reset to default.", show_alert=True)

            # Premium User
            elif action == "premium_user":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                user_data = await db.is_premium(user_id)
                if not user_data:
                    return await safe_action(query.answer,
                        "🚫 This feature is for premium users only.\n\n"
                        "Contact admin to upgrade.",
                        show_alert=True
                    )

                await safe_action(query.answer)
                premium_upi = clone.get("pu_upi", None)
                if premium_upi:
                    await show_premium_menu(client, query.message, bot_id)
                else:
                    PU_UPI[user_id] = (query.message, bot_id)
                    buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_pu_{bot_id}')]]
                    await safe_action(query.message.edit_text,
                        text="🔗 Please provide the updated **Upi I'd**:",
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )

            # Cancel Premium User
            elif action == "cancel_pu":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                PU_UPI.pop(user_id, None)
                await db.update_clone(bot_id, {"pu_upi": None})

                buttons = [[InlineKeyboardButton('⬅️ Back', callback_data=f'manage_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="❌ Premium User setup cancelled.\nYou can re-enable it anytime by providing a valid UPI ID.",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Add Premium User
            elif action == "add_pu":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ADD_PU[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addpu_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="✏️ Please provide the User ID of the new **premium user**:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Add Premium User
            elif action == "cancel_addpu":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ADD_PU.pop(user_id, None)
                await show_premium_menu(client, query.message, bot_id)

            # Remove Premium User Menu
            elif action == "remove_premium_user":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivated. Activate first!", show_alert=True)

                premium_user = clone.get("premium_user", [])
                if not premium_user:
                    return await safe_action(query.answer, "❌ No premium user found!", show_alert=True)

                await safe_action(query.answer)
                buttons = []

                for pu in premium_user:
                    user_id_int = None
                    name = None

                    if isinstance(pu, dict):
                        user_id_int = pu.get("user_id")
                        name = pu.get("name")
                    else:
                        try:
                            user_id_int = int(pu)
                        except ValueError:
                            user_id_int = pu

                    if not name:
                        user = await db.col.find_one({"id": user_id_int})
                        name = user.get("name") if user else None

                    if not name:
                        try:
                            tg_user = await client.get_users(user_id_int)
                            name = tg_user.first_name
                        except:
                            name = str(user_id_int)

                    if user_id_int:
                        buttons.append([InlineKeyboardButton(f"👤 {name}", callback_data=f"remove_pu_{bot_id}_{user_id_int}")])

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"premium_user_{bot_id}")])
                await safe_action(query.message.edit_text,
                    "👥 Please select a **premium user** to remove from the list:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Remove Premium User Action
            elif action == "remove_pu":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                premium_user = clone.get("premium_user", [])
                if not premium_user:
                    return await safe_action(query.answer, "❌ No premium user found!", show_alert=True)

                new_list = []
                for pu in premium_user:
                    if isinstance(pu, dict):
                        if pu.get("user_id") != pu_id:
                            new_list.append(pu)
                    else:
                        if int(pu) != pu_id:
                            new_list.append(pu)

                await db.update_clone(bot_id, {"premium_user": new_list})
                await safe_action(query.answer, "✅ Premium user removed!", show_alert=True)
                await show_premium_menu(client, query.message, bot_id)

            # Auto Delete Menu
            elif action == "auto_delete":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                current = clone.get("auto_delete", False)
                time_set = str(clone.get("ad_time", "1h"))
                msg_set = clone.get("ad_msg", script.AD_TXT)

                num_str = "".join(filter(str.isdigit, time_set)) or "0"
                unit_char = "".join(filter(str.isalpha, time_set)) or "h"

                try:
                    number = int(num_str)
                except:
                    number = 0

                unit_map = {"d": "day(s)", "h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
                unit = unit_map.get(unit_char.lower(), "hour(s)")

                try:
                    formatted_msg = msg_set.format(time=number, unit=unit)
                except KeyError:
                    formatted_msg = msg_set

                if current:
                    buttons = [
                        [InlineKeyboardButton("⏱ Time", callback_data=f"ad_time_{bot_id}"),
                        InlineKeyboardButton("📝 Message", callback_data=f"ad_message_{bot_id}"),
                        InlineKeyboardButton("❌ Disable", callback_data=f"ad_status_{bot_id}")]
                    ]
                    status = (
                        f"🟢 Enabled\n\n"
                        f"⏱ Time: {number} {unit}\n\n"
                        f"📝 Message: {formatted_msg}"
                    )
                else:
                    buttons = [[InlineKeyboardButton("✅ Enable", callback_data=f"ad_status_{bot_id}")]]
                    status = "🔴 Disabled"

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")])
                await safe_action(query.message.edit_text,
                    text=script.DELETE_TXT.format(status=f"{status}"),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Auto Delete Status
            elif action == "ad_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("auto_delete", False)
                await db.update_clone(bot_id, {"auto_delete": new_value})

                if new_value:
                    status_text = "🟢 Auto Delete has been successfully ENABLED!"
                else:
                    status_text = "🔴 Auto Delete has been successfully DISABLED!"

                buttons = [[InlineKeyboardButton("⬅️ Back", callback_data=f"auto_delete_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Auto Delete Time Menu
            elif action == "ad_time":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_time_menu(client, query.message, bot_id)

            # Edit Auto Delete Time
            elif action == "edit_adtime":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AD_TIME[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_editadtime_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="⏱ Please provide the new **Auto Delete Time** in **Seconds/Minutes/hours** (e.g., `30s` for 30 second, `5m` for 5 minute, `1h` for 1 hour):",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Auto Delete Time
            elif action == "cancel_editadtime":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AD_TIME.pop(user_id, None)
                await show_time_menu(client, query.message, bot_id)

            # See Auto Delete Time
            elif action == "see_adtime":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                ad_time = str(clone.get("ad_time", "1h"))

                num_str = "".join(filter(str.isdigit, ad_time)) or "0"
                unit_char = "".join(filter(str.isalpha, ad_time)) or "h"

                try:
                    number = int(num_str)
                except:
                    number = 0

                unit_map = {"d": "day(s)", "h": "hour(s)", "m": "minute(s)", "s": "second(s)"}
                unit = unit_map.get(unit_char.lower(), "hour(s)")

                await safe_action(query.answer, f"📝 Current Auto Delete Time:\n\n{number} {unit}", show_alert=True)

            # Default Auto Delete Time
            elif action == "default_adtime":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await db.update_clone(bot_id, {"ad_time": "1h"})
                await safe_action(query.answer, f"🔄 Auto delete time reset to default.", show_alert=True)

            # Auto Delete Message Menu
            elif action == "ad_message":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_message_menu(client, query.message, bot_id)

            # Edit Auto Delete Message
            elif action == "edit_admessage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AD_MESSAGE[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_editadmessage_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="📄 Please provide the new **Auto Delete Message**:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Auto Delete Message
            elif action == "cancel_editadmessage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                AD_MESSAGE.pop(user_id, None)
                await show_message_menu(client, query.message, bot_id)

            # See Auto Delete Message
            elif action == "see_admessage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                ad_message = clone.get("ad_msg", script.AD_TXT)
                await safe_action(query.answer, f"📝 Current Auto Delete Message:\n\n{ad_message}", show_alert=True)

            # Default Auto Delete Message
            elif action == "default_admessage":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await db.update_clone(bot_id, {"ad_msg": script.AD_TXT})
                await safe_action(query.answer, f"🔄 Auto delete message reset to default.", show_alert=True)

            # Forward Protect
            elif action == "forward_protect":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                current = clone.get("forward_protect", False)
                if current:
                    buttons = [[InlineKeyboardButton("❌ Disable", callback_data=f"fp_status_{bot_id}")]]
                    status = "🟢 Enabled"
                else:
                    buttons = [[InlineKeyboardButton("✅ Enable", callback_data=f"fp_status_{bot_id}")]]
                    status = "🔴 Disabled"

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"manage_{bot_id}")])
                await safe_action(query.message.edit_text,
                    text=script.FORWARD_TXT.format(status=f"{status}"),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Forward Protect Status
            elif action == "fp_status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                new_value = not clone.get("forward_protect", False)
                await db.update_clone(bot_id, {"forward_protect": new_value})

                if new_value:
                    status_text = "🟢 **Forward Protect** has been successfully ENABLED!"
                else:
                    status_text = "🔴 **Forward Protect** has been successfully DISABLED!"

                buttons = [[InlineKeyboardButton("⬅️ Back", callback_data=f"forward_protect_{bot_id}")]]
                await safe_action(query.message.edit_text,
                    text=status_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Moderator Menu
            elif action == "moderator":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await show_moderator_menu(client, query.message, bot_id)

            # Add Moderator
            elif action == "add_moderator":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ADD_MODERATOR[user_id] = (query.message, bot_id)
                buttons = [[InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_addmoderator_{bot_id}')]]
                await safe_action(query.message.edit_text,
                    text="✏️ Please provide the User ID of the new **moderator**:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Cancel Moderator
            elif action == "cancel_addmoderator":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                ADD_MODERATOR.pop(user_id, None)
                await show_moderator_menu(client, query.message, bot_id)

            # Remove Moderator Menu
            elif action == "remove_moderator":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                moderators = clone.get("moderators", [])
                if not moderators:
                    return await safe_action(query.answer, "❌ No moderators found!", show_alert=True)

                await safe_action(query.answer)
                buttons = []

                for mod in moderators:
                    try:
                        user_id_int = int(mod)
                    except ValueError:
                        user_id_int = mod

                    user = await db.col.find_one({"id": user_id_int})
                    name = user.get("name") if user else mod

                    buttons.append([InlineKeyboardButton(f"👤 {name}", callback_data=f"remove_mod_{bot_id}_{mod}")])

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"moderator_{bot_id}")])
                await safe_action(query.message.edit_text,
                    "👥 Please select a **moderator** to remove from the list:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Remove Moderator
            elif action == "remove_mod":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                moderators = clone.get("moderators", [])
                if not moderators:
                    return await safe_action(query.answer, "❌ No moderators found!", show_alert=True)

                await db.update_clone(bot_id, {"$pull": {"moderators": mod_id}}, raw=True)
                await safe_action(query.answer, "✅ Moderator removed!", show_alert=True)
                await show_moderator_menu(client, query.message, bot_id)

            # Transfer Moderator Menu
            elif action == "transfer_moderator":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                moderators = clone.get("moderators", [])
                if not moderators:
                    return await safe_action(query.answer, "❌ No moderators found!", show_alert=True)

                await safe_action(query.answer)
                buttons = []

                for mod in moderators:
                    try:
                        user_id_int = int(mod)
                    except ValueError:
                        user_id_int = mod

                    user = await db.col.find_one({"id": user_id_int})
                    name = user.get("name") if user else mod

                    buttons.append([InlineKeyboardButton(f"👤 {name}", callback_data=f"transfer_mod_{bot_id}_{mod}")])

                buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"moderator_{bot_id}")])
                await safe_action(query.message.edit_text,
                    "🔁 Please select a **moderator** to transfer ownership rights:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Transfer Moderator
            elif action == "transfer_mod":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                moderators = clone.get("moderators", [])
                if not moderators:
                    return await safe_action(query.answer, "❌ No moderators found!", show_alert=True)

                old_owner = int(clone.get("user_id"))
                if int(user_id) != old_owner:
                    return await safe_action(query.answer, "❌ Only the owner can transfer ownership!", show_alert=True)

                mod_id = int(mod_id)
                await db.update_clone(bot_id, {"$set": {"user_id": mod_id}}, raw=True)

                if str(old_owner) not in clone.get("moderators", []):
                    await db.update_clone(bot_id, {"$addToSet": {"moderators": str(old_owner)}}, raw=True)

                await db.update_clone(bot_id, {"$pull": {"moderators": str(mod_id)}}, raw=True)
                await safe_action(client.send_message,
                    mod_id,
                    f"✅ You are now the owner of the bot **{clone.get('name')}** (ID: {clone.get('bot_id')})"
                )
                await safe_action(query.answer, "✅ Ownership transferred!", show_alert=True)
                await show_clone_menu(client, query.message, old_owner)

            # Status
            elif action == "status":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                users = await clonedb.total_users_count(bot_id)
                banned_users = len(clone.get("banned_users", []))

                uptime = str(timedelta(seconds=int(time.time() - START_TIME)))

                await safe_action(query.answer,
                    f"📊 Status for @{clone.get('username')}\n\n"
                    f"👤 Users: {users}\n"
                    f"🚫 Banned: {banned_users}\n"
                    f"⏱ Uptime: {uptime}\n",
                    show_alert=True
                )

            # Activate/Deactivate
            elif action == "activate_deactivate":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                new_status = not clone.get("active", True)
                await db.update_clone(bot_id, {"active": new_status, "last_active": int(time.time())})

                status_text = "✅ Activated" if new_status else "❌ Deactivated"
                await safe_action(query.answer, f"Bot is now {status_text}", show_alert=True)

                await safe_action(query.answer)
                manage_buttons = query.message.reply_markup.inline_keyboard
                for row in manage_buttons:
                    for btn in row:
                        if "activate_deactivate" in btn.callback_data:
                            btn.text = status_text

                await query.message.edit_reply_markup(
                    InlineKeyboardMarkup(manage_buttons)
                )

            # Restart
            elif action == "restart":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await safe_action(query.message.edit_text, f"🔄 Restarting clone bot `@{clone['username']}`...\n[░░░░░░░░░░] 0%")

                for i in range(1, 11):
                    await asyncio.sleep(0.5)
                    bar = '▓' * i + '░' * (10 - i)
                    await safe_action(query.message.edit_text, f"🔄 Restarting clone bot `@{clone['username']}`...\n[{bar}] {i*10}%")

                try:
                    clone_client = get_client(bot_id)
                    if not clone_client:
                        return await safe_action(query.message.edit_text, "❌ Clone client not found in memory!")

                    await clone_client.stop()
                    await asyncio.sleep(2)
                    await clone_client.start()
                except Exception as e:
                    print(f"⚠️ Error restarting clone {bot_id}: {e}")
                    return await safe_action(query.message.edit_text,
                        f"❌ Failed to restart clone bot `@{clone['username']}`.\n\nError: {e}"
                    )

                await safe_action(query.message.edit_text, f"✅ Clone bot `@{clone['username']}` restarted successfully!")
                await asyncio.sleep(2)
                await show_clone_menu(client, query.message, user_id)

            # Delete Menu
            elif action == "delete":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                buttons = [
                    [InlineKeyboardButton('✅ Yes, Sure', callback_data=f'delete_clone_{bot_id}')],
                    [InlineKeyboardButton('❌ No, Go Back', callback_data=f'manage_{bot_id}')]
                ]
                await safe_action(query.message.edit_text,
                    text='⚠️ Are You Sure? Do you want **delete** your clone bot.',
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Delete Clone
            elif action == "delete_clone":
                if not clone:
                    return await safe_action(query.answer, "❌ Clone not found!", show_alert=True)

                if not active:
                    return await safe_action(query.answer, "⚠️ This bot is deactivate. Activate first!", show_alert=True)

                await safe_action(query.answer)
                await safe_action(query.message.edit_text, "🗑 Deleting clone, please wait...")

                clone_client = get_client(bot_id)
                if clone_client:
                    try:
                        await clone_client.stop()
                    except Exception as e:
                        print(f"Error stopping client {bot_id}: {e}")
                    remove_client(bot_id)

                await db.delete_clone(bot_id)
                await safe_action(query.message.edit_text, "✅ Clone deleted successfully.")
                await asyncio.sleep(2)
                await show_clone_menu(client, query.message, user_id)

        # Premium Menu
        elif data == "premium":
            await safe_action(query.answer)
            text = (
                "💎 **Premium Features** 💎\n\n"
                "**Normal Plan:**\n"
                "- Unlimited Button\n"
                "- Random Caption\n"
                "- Unlimited FSub Channel\n"
                "- Premium Users\n\n"
                "**Ultra Plan:**\n"
                "- Unlimited Button\n"
                "- Random Caption\n"
                "- Unlimited FSub Channel\n"
                "- Auto Posting\n"
                "- Premium Users\n\n"
                "**Vip Plan:**\n"
                "- Unlimited Clone Bot\n"
                "- Unlimited Button\n"
                "- Unlimited FSub Channel\n"
                "- Auto Posting\n"
                "- Premium Users\n\n"
            )

            buttons = [
                [InlineKeyboardButton("💰 Buy Normal Premium", callback_data="buy_normal")],
                [InlineKeyboardButton("🚀 Buy Ultra Premium", callback_data="buy_ultra")],
                [InlineKeyboardButton("👑 Buy VIP Premium", callback_data="buy_vip")],
                [InlineKeyboardButton("⬅️ Back", callback_data="start")]
            ]

            await safe_action(query.message.edit_text,
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )

        # Payment Flow
        elif data in ["buy_normal", "buy_ultra", "buy_vip"]:
            if data == "buy_normal":
                price = "₹99"
                feature_type = "Normal Premium"
            elif data == "buy_ultra":
                price = "₹249"
                feature_type = "Ultra Premium"
            else:
                price = "₹599"
                feature_type = "VIP Premium"

            await safe_action(query.answer)

            upi_id = "krishraj237@fam"
            upi_name = "KM File Store Bot"
            qr_image = generate_upi_qr(upi_id, upi_name, price)

            text = (
                f"💳 **{feature_type} Payment** 💳\n\n"
                f"💰 Amount: {price}\n"
                f"🏦 UPI ID: `{upi_id}`\n\n"
                "📸 Scan the QR below or send payment to UPI ID.\n\n"
                "After payment, click **✅ Payment Done** below to confirm."
            )

            buttons = [
                [InlineKeyboardButton("✅ Payment Done", callback_data=f"paid_{feature_type.replace(' ', '_')}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="premium")]
            ]

            await safe_action(query.message.delete)

            await safe_action(client.send_photo,
                chat_id=query.message.chat.id,
                photo=qr_image,
                caption=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )

        # User clicked Payment Done
        elif data.startswith("paid_"):
            await safe_action(query.answer)
            feature_type = data.replace("paid_", "").replace("_", " ")
            amount_expected = 99 if "Normal" in feature_type else 249 if "Ultra" in feature_type else 599

            await safe_action(query.message.edit_text,
                await safe_action(query.message.edit_text,
                text=(
                    f"🔍 Checking payment status...\n\n"
                    f"Feature: **{feature_type}**\n"
                    f"💰 Amount: ₹{amount_expected}\n"
                    f"⚡ Please wait while we verify your transaction."
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )

            payments = await fetch_fampay_payments()

            matched_payment = None
            for txn in payments:
                if txn["amount"] == amount_expected:
                    matched_payment = txn
                    break

            if matched_payment:
                days=30
                expiry_date = datetime.utcnow() + timedelta(days=days)
                plan_type = feature_type.lower().split()[0]
                await db.add_premium_user(user_id, days, plan_type)
                await safe_action(query.message.edit_text,
                    f"✅ Payment confirmed!\n"
                    f"Feature: **{feature_type}**\n"
                    f"Amount: ₹{amount_expected}\n"
                    f"Transaction ID: `{matched_payment['txn_id']}`\n"
                    "Your plan is now active.",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            else:
                await safe_action(query.message.edit_text,
                    f"✅ Your payment request for **{feature_type}** has been recorded.\n\n"
                    f"💰 Amount: ₹{amount_expected}\n"
                    f"⏳ Waiting for payment confirmation via UPI...\n\n"
                    f"⚡ As soon as we receive your transaction, your plan will be auto-activated.",
                    parse_mode=enums.ParseMode.MARKDOWN
                )

        # Close
        elif data == "close":
            await safe_action(query.answer)
            await safe_action(query.message.delete)

        else:
            await safe_action(client.send_message,
                LOG_CHANNEL,
                f"⚠️ Unknown Callback Data Received:\n\n{data}\n\nUser: {query.from_user.id}\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
            )
            await safe_action(query.answer, "⚠️ Unknown action.", show_alert=True)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Callback Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Callback Handler Error: {e}")
        print(traceback.format_exc())
        await safe_action(query.answer, "❌ An error occurred. The admin has been notified.", show_alert=True)

@Client.on_message(filters.all)
async def message_capture(client: Client, message: Message):
    try:
        chat = message.chat
        if chat and (chat.type == enums.ChatType.PRIVATE):
            user_id = message.from_user.id if message.from_user else None

            if not (
                user_id in PREMIUM_STATE
                or user_id in CLONE_TOKEN
                or user_id in START_TEXT
                or user_id in START_PHOTO
                or user_id in CAPTION_TEXT
                or user_id in ADD_BUTTON
                or user_id in HEADER_TEXT
                or user_id in FOOTER_TEXT
                or user_id in ADD_FSUB
                or user_id in ACCESS_TOKEN
                or user_id in AT_VALIDITY
                or user_id in AT_TUTORIAL
                or user_id in AUTO_POST
                or user_id in AP_IMAGE
                or user_id in AP_SLEEP
                or user_id in PU_UPI
                or user_id in ADD_PU
                or user_id in AD_TIME
                or user_id in AD_MESSAGE
                or user_id in ADD_MODERATOR
            ):
                return

            # -------------------- CREATE CLONE --------------------
            if user_id in CLONE_TOKEN:
                msg = CLONE_TOKEN[user_id]
                try:
                    await safe_action(message.delete)
                except:
                    pass

                is_vip = await db.is_premium(user_id, required_plan="vip")
                if not is_vip and await db.is_clone_exist(user_id):
                    await safe_action(msg.edit_text, "You have already cloned a **bot**. Delete it first.")
                    await asyncio.sleep(2)
                    await show_clone_menu(client, msg, user_id)
                    CLONE_TOKEN.pop(user_id, None)
                    return

                token = None
                if message.forward_from and message.forward_from.id == 93372553:
                    try:
                        token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", message.text or "")[0]
                    except IndexError:
                        token = None
                else:
                    try:
                        token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", message.text or "")[0]
                    except IndexError:
                        token = None

                if not token:
                    await safe_action(msg.edit_text, "❌ Could not detect **bot token**. Forward the BotFather message or type the token correctly.")
                    await asyncio.sleep(2)
                    await show_clone_menu(client, msg, user_id)
                    CLONE_TOKEN.pop(user_id, None)
                    return

                await safe_action(msg.edit_text, "👨‍💻 Creating your **bot**, please wait...")
                try:
                    xd = Client(
                        name=f"{token}",
                        api_id=API_ID,
                        api_hash=API_HASH,
                        bot_token=token,
                        plugins={"root": "clone"},
                        workers=20,
                        in_memory=True
                    )

                    await xd.start()
                    bot = await xd.get_me()
                    set_client(bot.id, xd)
                    await db.add_clone_bot(bot.id, user_id, bot.first_name, bot.username, token)
                    await promote(bot.username)
                    await set_clone_menu(xd)

                    await safe_action(client.send_message,
                        LOG_CHANNEL,
                        f"✅ New Clone Bot Created\n\n"
                        f"Bot Id: {bot.id}\n"
                        f"User Id: {user_id}\n"
                        f"Username: @{message.from_user.username}\n"
                        f"Bot Name: {bot.first_name} {bot.last_name}\n"
                        f"Bot Username: @{bot.username}\n"
                        f"Bot Token: <code>{token}</code>"
                    )

                    await safe_action(msg.edit_text, f"✅ Successfully cloned your **bot**: @{bot.username}")
                    await asyncio.sleep(2)
                    await show_clone_menu(client, msg, user_id)
                    CLONE_TOKEN.pop(user_id, None)
                except Exception as e:
                    await safe_action(client.send_message, LOG_CHANNEL, f"⚠️ Create Bot Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>.")
                    await safe_action(msg.edit_text, f"❌ Failed to create **bot**: {e}")
                    await asyncio.sleep(2)
                    await show_clone_menu(client, msg, user_id)
                    CLONE_TOKEN.pop(user_id, None)
                finally:
                    CLONE_TOKEN.pop(user_id, None)
                return

            # -------------------- GENERIC TEXT/PHOTO HANDLERS --------------------
            handlers = [
                ("START_TEXT", START_TEXT, "text", "start_text", "show_text_menu"),
                ("START_PHOTO", START_PHOTO, "photo", "start_photo", "show_photo_menu"),
                ("CAPTION_TEXT", CAPTION_TEXT, "text", "caption", "show_caption_menu"),
                ("HEADER_TEXT", HEADER_TEXT, "text", "header", "show_header_menu"),
                ("FOOTER_TEXT", FOOTER_TEXT, "text", "footer", "show_footer_menu"),
                ("AT_VALIDITY", AT_VALIDITY, "text", "at_validity", "show_validity_menu"),
                ("AT_TUTORIAL", AT_TUTORIAL, "text", "at_tutorial", "show_tutorial_menu"),
                ("AP_IMAGE", AP_IMAGE, "photo", "ap_image", "show_image_menu"),
                ("AP_SLEEP", AP_SLEEP, "text", "ap_sleep", "show_sleep_menu"),
                ("PU_UPI", PU_UPI, "text", "pu_upi", "show_premium_menu"),
                ("ADD_PU", ADD_PU, "text", "premium_user", "show_premium_menu"),
                ("AD_TIME", AD_TIME, "text", "ad_time", "show_time_menu"),
                ("AD_MESSAGE", AD_MESSAGE, "text", "ad_msg", "show_message_menu"),
                ("ADD_MODERATOR", ADD_MODERATOR, "text", "moderators", "show_moderator_menu")
            ]

            for name, handler_dict, input_type, db_field, menu_func in handlers:
                if user_id in handler_dict:
                    orig_msg, bot_id = handler_dict[user_id]
                    try:
                        await safe_action(message.delete)
                    except:
                        pass

                    if input_type == "text":
                        content = message.text.strip() if message.text else ""
                        if not content:
                            await safe_action(orig_msg.edit_text, "❌ Empty message. Please send a valid text.")
                            await asyncio.sleep(2)
                            await globals()[menu_func](client, orig_msg, bot_id)
                            handler_dict.pop(user_id, None)
                            return
                    elif input_type == "photo":
                        if not message.photo:
                            await safe_action(orig_msg.edit_text, "❌ Please send a valid photo.")
                            await asyncio.sleep(2)
                            await globals()[menu_func](client, orig_msg, bot_id)
                            handler_dict.pop(user_id, None)
                            return

                    random_code()

                    await safe_action(orig_msg.edit_text, f"✏️ Updating **{db_field.replace('_', ' ')}**, please wait...")
                    try:
                        clone = await db.get_clone(bot_id)
                        if db_field == "start_photo":
                            storage_dir = "storage"
                            os.makedirs(storage_dir, exist_ok=True)
                            content = os.path.join(storage_dir, f"{code}_photo.jpg")
                            fileid = message.photo.file_id
                            temp_file = await client.download_media(fileid)
                            if os.path.exists(content):
                                os.remove(content)
                            shutil.move(temp_file, content)
                        elif db_field == "ap_image":
                            storage_dir = "storage"
                            os.makedirs(storage_dir, exist_ok=True)
                            content = os.path.join(storage_dir, f"{code}_photo.jpg")
                            fileid = message.photo.file_id
                            temp_file = await client.download_media(fileid)
                            if os.path.exists(content):
                                os.remove(content)
                            shutil.move(temp_file, content)
                        elif db_field == "premium_user":
                            premium_user = clone.get("premium_user", [])
                            premium_user.append(content)
                            await db.update_clone(bot_id, {db_field: premium_user})
                        elif db_field == "moderators":
                            moderators = clone.get("moderators", [])
                            moderators.append(content)
                            await db.update_clone(bot_id, {db_field: moderators})
                        else:
                            await db.update_clone(bot_id, {db_field: content})

                        await safe_action(orig_msg.edit_text, f"✅ Successfully updated **{db_field.replace('_', ' ')}**!")
                        await asyncio.sleep(2)
                        await globals()[menu_func](client, orig_msg, bot_id)
                        handler_dict.pop(user_id, None)
                    except Exception as e:
                        await safe_action(client.send_message, LOG_CHANNEL, f"⚠️ Error updating {db_field}:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>.")
                        await safe_action(orig_msg.edit_text, f"❌ Failed to update **{db_field.replace('_', ' ')}**: {e}")
                        await asyncio.sleep(2)
                        await globals()[menu_func](client, orig_msg, bot_id)
                        handler_dict.pop(user_id, None)
                    finally:
                        handler_dict.pop(user_id, None)
                    return

            # -------------------- ADD BUTTON --------------------
            if user_id in ADD_BUTTON:
                data = ADD_BUTTON[user_id]
                orig_msg, bot_id, step = data["orig_msg"], data["bot_id"], data["step"]
                try:
                    await safe_action(message.delete)
                except:
                    pass

                new_text = message.text.strip() if message.text else ""
                if not new_text:
                    await safe_action(orig_msg.edit_text, "❌ Empty message. Please send valid text.")
                    await asyncio.sleep(2)
                    await show_button_menu(client, orig_msg, bot_id)
                    ADD_BUTTON.pop(user_id, None)
                    return

                if step == "name":
                    ADD_BUTTON[user_id]["btn_name"] = new_text
                    ADD_BUTTON[user_id]["step"] = "url"
                    await safe_action(orig_msg.edit_text, f"✅ Button name saved: **{new_text}**\n\nNow send the URL.")
                elif step == "url":
                    btn_name = data["btn_name"]
                    btn_url = new_text
                    await safe_action(orig_msg.edit_text, "✏️ Updating **start button**, please wait...")
                    try:
                        clone = await db.get_clone(bot_id)
                        buttons_data = clone.get("button", [])
                        buttons_data.append({"name": btn_name, "url": btn_url})
                        await db.update_clone(bot_id, {"button": buttons_data})
                        await safe_action(orig_msg.edit_text, "✅ Successfully updated **start button**!")
                        await asyncio.sleep(2)
                        await show_button_menu(client, orig_msg, bot_id)
                        ADD_BUTTON.pop(user_id, None)
                    except Exception as e:
                        await safe_action(client.send_message, LOG_CHANNEL, f"⚠️ Update Start Button Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>.")
                        await safe_action(orig_msg.edit_text, f"❌ Failed to update **start button**: {e}")
                        await asyncio.sleep(2)
                        await show_button_menu(client, orig_msg, bot_id)
                        ADD_BUTTON.pop(user_id, None)
                    finally:
                        ADD_BUTTON.pop(user_id, None)
                    return

            # -------------------- FORCE SUBSCRIBE --------------------
            if user_id in ADD_FSUB:
                data = ADD_FSUB[user_id]
                orig_msg, bot_id, step = data["orig_msg"], data["bot_id"], data["step"]
                try:
                    await safe_action(message.delete)
                except:
                    pass

                new_text = message.text.strip() if message.text else ""

                if step == "channel":
                    channel_id_int = None
                    if message.forward_from_chat:
                        forward_chat = message.forward_from_chat
                        channel_id_int = forward_chat.id
                    else:
                        try:
                            channel_id_int = int(new_text)
                        except ValueError:
                            channel_id_int = new_text

                    clone_client = get_client(bot_id)
                    if not clone_client:
                        await safe_action(orig_msg.edit_text, "❌ Clone bot not running, please restart it.")
                        await asyncio.sleep(2)
                        await show_fsub_menu(client, orig_msg, bot_id)
                        ADD_FSUB.pop(user_id, None)
                        return

                    try:
                        chat = await clone_client.get_chat(channel_id_int)
                        ch_name = chat.title or "Unknown"
                        ch_link = f"https://t.me/{chat.username}" if chat.username else None
                    except Exception as e:
                        await safe_action(orig_msg.edit_text, f"❌ Failed to get channel info: {e}")
                        await asyncio.sleep(2)
                        await show_fsub_menu(client, orig_msg, bot_id)
                        ADD_FSUB.pop(user_id, None)
                        return

                    try:
                        me = await clone_client.get_me()
                        member = await clone_client.get_chat_member(chat.id, me.id)
                        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                            await safe_action(orig_msg.edit_text, "❌ The clone bot is NOT an admin in this channel. Add it as admin first.")
                            await asyncio.sleep(2)
                            await show_fsub_menu(client, orig_msg, bot_id)
                            ADD_FSUB.pop(user_id, None)
                            return
                    except Exception as e:
                        await safe_action(orig_msg.edit_text, f"❌ Failed to check clone bot in channel: {e}")
                        await asyncio.sleep(2)
                        await show_fsub_menu(client, orig_msg, bot_id)
                        ADD_FSUB.pop(user_id, None)
                        return
                    
                    ADD_FSUB[user_id]["channel"] = int(chat.id)
                    ADD_FSUB[user_id]["name"] = ch_name
                    ADD_FSUB[user_id]["link"] = ch_link
                    ADD_FSUB[user_id]["step"] = "target"
                    await safe_action(orig_msg.edit_text, f"✅ Channel saved: `{new_text}`\n\nNow send the target number of users.\n\nSend 0 for unlimited.")
                elif step == "target":
                    try:
                        target = int(new_text)
                        if target < 0:
                            raise ValueError
                        ADD_FSUB[user_id]["target"] = target
                        ADD_FSUB[user_id]["step"] = "mode"
                        await safe_action(orig_msg.edit_text, f"✅ Target saved: `{target}`\n\nNow choose the mode.")
                        buttons = [
                            [
                                InlineKeyboardButton("✅ Normal Join", callback_data=f"fsub_mode_normal_{bot_id}"),
                                InlineKeyboardButton("📝 Request Join", callback_data=f"fsub_mode_request_{bot_id}")
                            ],
                            [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_addfsub_{bot_id}")]
                        ]
                        await safe_action(orig_msg.edit_text,
                            f"🎯 Target saved: `{target}`\n\nNow choose the **mode** for this channel:",
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                    except:
                        await safe_action(orig_msg.edit_text, "❌ Invalid number! Send 0 or a positive integer.")
                        await asyncio.sleep(2)
                        await show_fsub_menu(client, orig_msg, bot_id)
                        ADD_FSUB.pop(user_id, None)
                        return

            # -------------------- ACCESS TOKEN --------------------
            if user_id in ACCESS_TOKEN:
                data = ACCESS_TOKEN[user_id]
                orig_msg, bot_id, step = data["orig_msg"], data["bot_id"], data["step"]
                try:
                    await safe_action(message.delete)
                except:
                    pass

                new_text = message.text.strip() if message.text else ""
                if not new_text:
                    await db.update_clone(bot_id, {"access_token": False})
                    await safe_action(orig_msg.edit_text, "❌ Empty message. Please send valid text.")
                    await asyncio.sleep(2)
                    await show_token_menu(client, orig_msg, bot_id)
                    ACCESS_TOKEN.pop(user_id, None)
                    return

                if step == "link":
                    new_text = new_text.removeprefix("https://").removeprefix("http://")
                    ACCESS_TOKEN[user_id]["at_shorten_link"] = new_text
                    ACCESS_TOKEN[user_id]["step"] = "api"
                    await safe_action(orig_msg.edit_text, "✅ Shorten link saved! Now send your API key.")
                elif step == "api":
                    await safe_action(orig_msg.edit_text, "✏️ Updating **access token**, please wait...")
                    try:
                        await db.update_clone(bot_id, {"at_shorten_link": data["at_shorten_link"], "at_shorten_api": new_text})
                        await safe_action(orig_msg.edit_text, "✅ Successfully updated **access token**!")
                        await asyncio.sleep(2)
                        await show_token_menu(client, orig_msg, bot_id)
                        ACCESS_TOKEN.pop(user_id, None)
                    except Exception as e:
                        await db.update_clone(
                            bot_id,
                            {"access_token": False, "at_shorten_link": None, "at_shorten_api": None}
                        )
                        await safe_action(client.send_message, LOG_CHANNEL, f"⚠️ Update Access Token Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>.")
                        await safe_action(orig_msg.edit_text, f"❌ Failed to update **access token**: {e}")
                        await asyncio.sleep(2)
                        await show_token_menu(client, orig_msg, bot_id)
                        ACCESS_TOKEN.pop(user_id, None)
                    finally:
                        ACCESS_TOKEN.pop(user_id, None)
                    return

            # -------------------- AUTO POST --------------------
            if user_id in AUTO_POST:
                orig_msg, bot_id = AUTO_POST[user_id]
                try:
                    await safe_action(message.delete)
                except:
                    pass

                new_text = message.text.strip() if message.text else ""

                channel_id_int = None
                if message.forward_from_chat:
                    forward_chat = message.forward_from_chat
                    channel_id_int = forward_chat.id
                else:
                    try:
                        channel_id_int = int(new_text)
                    except ValueError:
                        channel_id_int = new_text

                clone_client = get_client(bot_id)
                if not clone_client:
                    await db.update_clone(bot_id, {"auto_post": False, "ap_channel": None})
                    await safe_action(orig_msg.edit_text, "❌ Clone bot not running, please restart it.")
                    await asyncio.sleep(2)
                    await show_post_menu(client, orig_msg, bot_id)
                    AUTO_POST.pop(user_id, None)
                    return

                try:
                    chat = await clone_client.get_chat(channel_id_int)
                    ch_name = chat.title or "Unknown"
                    ch_link = f"https://t.me/{chat.username}" if chat.username else None
                except Exception as e:
                    await db.update_clone(bot_id, {"auto_post": False, "ap_channel": None})
                    await safe_action(orig_msg.edit_text, f"❌ Failed to get channel info: {e}")
                    await asyncio.sleep(2)
                    await show_post_menu(client, orig_msg, bot_id)
                    AUTO_POST.pop(user_id, None)
                    return

                try:
                    me = await clone_client.get_me()
                    member = await clone_client.get_chat_member(chat.id, me.id)
                    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                        await db.update_clone(bot_id, {"auto_post": False, "ap_channel": None})
                        await safe_action(orig_msg.edit_text, "❌ The clone bot is NOT an admin in this channel. Add it as admin first.")
                        await asyncio.sleep(2)
                        await show_post_menu(client, orig_msg, bot_id)
                        AUTO_POST.pop(user_id, None)
                        return
                except Exception as e:
                    await db.update_clone(bot_id, {"auto_post": False, "ap_channel": None})
                    await safe_action(orig_msg.edit_text, f"❌ Failed to check clone bot in channel: {e}")
                    await asyncio.sleep(2)
                    await show_post_menu(client, orig_msg, bot_id)
                    AUTO_POST.pop(user_id, None)
                    return

                buttons = [
                    [
                        InlineKeyboardButton("📌 Single Mode", callback_data=f"ap_mode_single_{bot_id}_{chat.id}"),
                        InlineKeyboardButton("📂 Batch Mode", callback_data=f"ap_mode_batch_{bot_id}_{chat.id}")
                    ],
                    [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_autopost_{bot_id}")]
                ]

                await safe_action(orig_msg.edit_text,
                    f"✅ Channel detected: **{ch_name}**\n\n"
                    "👉 Please select **Auto Post Mode**:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

                AUTO_POST.pop(user_id, None)
                return
    except Exception as e:
        await safe_action(client.send_message, LOG_CHANNEL, f"⚠️ Unexpected Error in message_capture:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>.")
        print(f"⚠️ Unexpected Error in message_capture: {e}")
        print(traceback.format_exc())
