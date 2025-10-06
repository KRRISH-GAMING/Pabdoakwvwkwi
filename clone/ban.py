from imports import *
from plugins.database import *
from plugins.helper import *

@Client.on_message(filters.command("ban") & filters.private)
async def ban(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_clone(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        ask_id = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="👤 Send the User ID to ban:",
            filters=filters.text,
        )
        user_id = int(ask_id.text.strip())

        await db.ban_user(me.id, user_id)
        await message.reply_text(f"✅ User `{user_id}` banned successfully.", quote=True)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Ban Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Ban Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("unban") & filters.private)
async def unban(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_clone(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        ask_id = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="👤 Send the User ID to unban:",
            filters=filters.text,
        )
        user_id = int(ask_id.text.strip())

        await db.unban_user(me.id, user_id)
        await message.reply_text(f"✅ User `{user_id}` unbanned successfully.", quote=True)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Unban Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Unban Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("list_ban") & filters.private)
async def list_ban(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_clone(me.id)
        if not clone:
            return

        owner_id = clone.get("user_id")
        moderators = clone.get("moderators", [])
        moderators = [int(m) for m in moderators]

        if message.from_user.id != owner_id and message.from_user.id not in moderators:
            return await safe_action(message.reply, "❌ You are not authorized to use this bot.")

        banned = await db.get_banned_users(me.id)
        if not banned:
            return await message.reply_text("✅ No banned users.")

        text = "🚫 **Banned Users:**\n" + "\n".join([f"`{u}`" for u in banned])
        await message.reply_text(text, quote=True)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone List Ban Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone List Ban Error: {e}")
        print(traceback.format_exc())