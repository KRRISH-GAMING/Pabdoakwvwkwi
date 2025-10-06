from imports import *
from plugins.config import *
from plugins.helper import *

@Client.on_message(filters.command('restart') & filters.private & filters.user(ADMINS))
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