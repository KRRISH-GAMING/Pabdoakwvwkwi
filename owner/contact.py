from imports import *
from plugins.config import *
from plugins.helper import *

@Client.on_message(filters.command("contact") & filters.private)
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