from imports import *
from plugins.database import *
from plugins.helper import *

@Client.on_message(filters.command("contact") & filters.private)
async def contact(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        clone = await db.get_clone(me.id)
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

        clone = await db.get_clone(me.id)
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
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Reply Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Reply Error: {e}")
        print(traceback.format_exc())