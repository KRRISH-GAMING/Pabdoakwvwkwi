from imports import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *

@Client.on_message(filters.command("help") & filters.private)
async def help(client, message):
    try:
        me = await client.get_me()
        clone = await db.get_clone(me.id)
        if not clone:
            return

        await safe_action(message.reply_text, script.HELP_TXT)
    except Exception as e:
        await safe_action(client.send_message,
            LOG_CHANNEL,
            f"⚠️ Clone Help Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Help Error: {e}")
        print(traceback.format_exc())