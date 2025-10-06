from imports import *
from plugins.database import *
from plugins.helper import *

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client, message):
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

        users = await clonedb.total_users_count(me.id)
        banned_users = len(clone.get("banned_users", []))

        uptime = str(timedelta(seconds=int(pytime.time() - START_TIME)))

        await safe_action(message.reply,
            f"📊 Status for @{clone.get('username')}\n\n"
            f"👤 Users: {users}\n"
            f"🚫 Banned: {banned_users}\n"
            f"⏱ Uptime: {uptime}\n",
        )
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Stats Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Stats Error: {e}")
        print(traceback.format_exc())