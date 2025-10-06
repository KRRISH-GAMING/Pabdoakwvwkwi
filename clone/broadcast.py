from imports import *
from plugins.database import *
from plugins.helper import *

async def broadcast_messages(bot_id, user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(bot_id, user_id, message)
    except InputUserDeactivated:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Error"
    except Exception:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Error"

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client, message):
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

        if message.reply_to_message:
            b_msg = message.reply_to_message
        else:
            b_msg = await safe_action(client.ask,
                message.from_user.id,
                "📩 Now send me your broadcast message\n\nType /cancel to stop.",
            )

            if b_msg.text and b_msg.text.lower() == "/cancel":
                return await safe_action(message.reply, "🚫 Broadcast cancelled.")

        users = await clonedb.get_all_users(me.id)
        total_users = await clonedb.total_users_count(me.id)
        sts = await safe_action(message.reply_text, "⏳ Broadcast starting...")

        done = blocked = deleted = failed = success = 0
        start_time = pytime.time()

        async for user in users:
            if 'user_id' in user:
                pti, sh = await broadcast_messages(me.id, int(user['user_id']), b_msg)
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
                    elapsed = pytime.time() - start_time
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

        time_taken = timedelta(seconds=int(pytime.time() - start_time))
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
            f"⚠️ Clone Broadcast Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Clone Broadcast Error: {e}")
        print(traceback.format_exc())