from imports import *
from plugins.helper import *
from plugins.script import *

@Client.on_message(filters.command("help") & filters.private)
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