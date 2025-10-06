from imports import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *

@Client.on_message(filters.command("stats") & filters.private & filters.user(ADMINS))
async def stats(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        username = me.username
        users_count = await db.total_users_count()

        uptime = str(timedelta(seconds=int(pytime.time() - START_TIME)))

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