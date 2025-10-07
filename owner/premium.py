from imports import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *

@StreamBot.on_message(filters.command("add_premium") & filters.private & filters.user(ADMINS))
async def add_premium(client, message):
    try:
        ask_id = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="👤 Send the User ID to add as premium:",
            filters=filters.text,
            reply_to_message_id=message.id
        )
        user_id = int(ask_id.text.strip())

        ask_days = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="📅 Send number of days for premium:",
            filters=filters.text,
            reply_to_message_id=message.id
        )
        days = int(ask_days.text.strip())

        ask_plan = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="💎 Send plan type:\n\n- `normal`\n- `ultra`",
            filters=filters.text,
            reply_to_message_id=message.id
        )
        plan = ask_plan.text.lower().strip()
        if plan not in ["normal", "ultra"]:
            return await safe_action(message.reply_text, "❌ Invalid plan type. Must be 'normal' or 'ultra'.", quote=True)

        await db.add_premium_user(user_id, days, plan)

        expiry = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
        await safe_action(message.reply_text,
            f"✅ Added **{plan.title()} Premium**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📅 Days: {days}\n"
            f"⏳ Expiry: {expiry}",
            quote=True
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Add Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Add Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("remove_premium") & filters.private & filters.user(ADMINS))
async def remove_premium(client, message):
    try:
        ask_id = await safe_action(client.ask,
            chat_id=message.chat.id,
            text="👤 Send the User ID to remove from premium:",
            filters=filters.text,
            reply_to_message_id=message.id
        )
        
        user_id = int(ask_id.text.strip())
        user = await db.get_premium_user(user_id)
        if not user:
            return await safe_action(message.reply_text, f"ℹ️ User `{user_id}` is **not premium**.", quote=True)

        await db.remove_premium_user(user_id)
        await safe_action(message.reply_text, f"✅ Removed premium from {user_id}.", quote=True)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Remove Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Remove Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("list_premium") & filters.private & filters.user(ADMINS))
async def list_premium(client, message):
    try:
        users = await db.list_premium_users()
        if not users:
            return await safe_action(message.reply_text, "ℹ️ No premium users found.", quote=True)

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
                caption="📄 Premium Users List",
                quote=True
            )
        else:
            await safe_action(message.reply_text, text, quote=True)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ List Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ List Premium Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("check_premium") & filters.private & filters.user(ADMINS))
async def check_premium(client, message):
    try:
        if len(message.command) < 2:
            return await safe_action(message.reply_text, "❌ Usage: /check_premium <user_id>", quote=True)

        user_id = int(message.command[1])
        user = await db.get_premium_user(user_id)

        if not user:
            return await safe_action(message.reply_text, f"ℹ️ User `{user_id}` is **not premium**.", quote=True)

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
                f"⏳ **Remaining:** {days_left} days",
                quote=True
            )
        else:
            await safe_action(message.reply_text,
                f"👤 **User:** `{user_id}`\n"
                f"💎 **Plan:** {plan}\n"
                f"❌ Premium expired.",
                quote=True
            )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Check Premium Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Check Premium Error: {e}")
        print(traceback.format_exc())
