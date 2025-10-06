from imports import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        return False, f"Error: {str(e)}"

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMINS))
async def broadcast(client, message):
    try:
        if message.reply_to_message:
            b_msg = message.reply_to_message
        else:
            b_msg = await safe_action(client.ask,
                message.chat.id,
                "📩 Send the message to broadcast\n\n/cancel to stop.",
            )

            if b_msg.text and b_msg.text.lower() == '/cancel':
                return await safe_action(message.reply, '🚫 Broadcast cancelled.')

        sts = await safe_action(message.reply_text, "⏳ Broadcast starting...")
        start_time = pytime.time()
        total_users = await db.total_users_count()

        done = blocked = deleted = failed = success = 0

        users = await db.get_all_users()
        async for user in users:
            try:
                if "id" in user:
                    pti, sh = await broadcast_messages(int(user["id"]), b_msg)
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
            except Exception:
                failed += 1
                done += 1
                continue

        time_taken = timedelta(seconds=int(pytime.time() - start_time))
        #speed = round(done / (pytime.time()-start_time), 2) if done > 0 else 0
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
            f"⚠️ Broadcast Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Broadcast Error: {e}")
        print(traceback.format_exc())