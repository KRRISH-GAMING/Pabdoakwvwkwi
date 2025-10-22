import logging, logging.config, os, asyncio, glob, importlib, sys, pytz
from datetime import datetime, date, timezone
from typing import *
from pathlib import Path
from aiohttp import ClientSession, web, ClientTimeout, TCPConnector
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from pyrogram.errors.exceptions.bad_request_400 import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *
from clone.clone import *

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

multi_clients: Dict[int, Client] = {}
work_loads: Dict[int, int] = {}
StartTime = datetime.utcnow()
__version__ = 1.5
routes = web.RouteTableDef()

auto_restart_task = None

class StreamXBot(Client):
    async def iter_messages(self, chat_id: Union[int, str], limit: int) -> AsyncGenerator[types.Message, None]:
        async for message in self.get_chat_history(chat_id, limit=limit):
            yield message

StreamBot = StreamXBot(
    name="KMFileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=20,
    plugins={"root": "owner"},
    sleep_threshold=5
)

class TokenParser:
    def parse_from_env(self) -> Dict[int, str]:
        return {
            i+1: t for i, (_, t) in enumerate(
                filter(lambda x: x[0].startswith("MULTI_TOKEN"), sorted(os.environ.items()))
            )
        }

async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()

    if not all_tokens:
        logger.info("No additional clients found, using default client")
        return

    semaphore = asyncio.Semaphore(10)

    async def start_client(client_id, token):
        async with semaphore:
            try:
                logger.info(f"Starting client {client_id}")
                client = await Client(
                    name=f"clone_{client_id}",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    bot_token=token,
                    workers=20,
                    in_memory=True,
                ).start()
                work_loads[client_id] = 0
                return client_id, client
            except Exception:
                logger.exception(f"Failed starting Client {client_id}")
                return None

    clients = await asyncio.gather(*[start_client(i, t) for i, t in all_tokens.items()])
    clients = [c for c in clients if c]
    multi_clients.update(dict(clients))

    if len(multi_clients) > 1:
        logger.info(f"Multi-Client Mode Enabled: {len(multi_clients)} clients")
    else:
        logger.info("Only default client active")

def get_readable_time(start: datetime) -> str:
    delta = datetime.utcnow() - start
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}d:{int(hours)}h:{int(minutes)}m:{int(seconds)}s"

def get_least_loaded_bot() -> tuple[Client, int]:
    client_id, _ = min(work_loads.items(), key=lambda x: x[1])
    work_loads[client_id] += 1
    return multi_clients[client_id], client_id

async def complete_task(client_id: int):
    if client_id in work_loads:
        work_loads[client_id] = max(0, work_loads[client_id] - 1)

async def dispatch_task(chat_id: int, text: str):
    client, client_id = get_least_loaded_bot()
    try:
        await safe_action(client.send_message, chat_id, text)
    except Exception as e:
        logger.warning(f"Failed to send with bot {client_id}: {e}")
    finally:
        await complete_task(client_id)

async def dispatch_bulk(tasks: list):
    async def worker(task):
        await dispatch_task(task["chat_id"], task["text"])
    await asyncio.gather(*[worker(t) for t in tasks])

@routes.get("/", allow_head=True)
async def root(_):
    return web.json_response({
        "server_status": "running",
        "uptime": get_readable_time(StartTime),
        "telegram_bot": "@" + StreamBot.username,
        "connected_bots": len(multi_clients),
        "loads": {f"bot{c}": l for c, l in work_loads.items()},
        "version": __version__
    })

async def start_web_server():
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web server running on port {PORT}")

def load_plugins():
    for file in glob.glob("owner/*.py"):
        plugin_name = Path(file).stem
        spec = importlib.util.spec_from_file_location(f"owner.{plugin_name}", file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[f"owner.{plugin_name}"] = module
        logger.info(f"✅ Imported plugin: {plugin_name}")


# Track currently running clones and their auto-post tasks
running_clones = {}      # {bot_id: Client}
auto_post_tasks = {}     # {bot_id: asyncio.Task}


# -------------------------------------------------
# STOP OLD BOT + AUTO-POST TASK (SAFE CLEANUP)
# -------------------------------------------------
async def stop_clone(bot_id: int):
    # Stop old auto-post task
    if bot_id in auto_post_tasks:
        task = auto_post_tasks.pop(bot_id)
        if not task.done():
            task.cancel()
            print(f"🛑 Canceled old auto-post for bot {bot_id}")

    # Stop old client
    if bot_id in running_clones:
        client = running_clones.pop(bot_id)
        try:
            await client.stop()
            print(f"🛑 Stopped old clone bot {bot_id}")
        except Exception as e:
            print(f"⚠️ Error stopping bot {bot_id}: {e}")


# -------------------------------------------------
# RESTART SINGLE CLONE BOT
# -------------------------------------------------
async def restart_single_clone(bot_data):
    bot_token = bot_data["token"]
    bot_id = bot_data["_id"]

    try:
        # Stop any existing bot and its tasks
        await stop_clone(bot_id)

        # Start new client
        xd = Client(
            name=f"clone_{bot_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins={"root": "clone"},
            workers=20,
            in_memory=True
        )

        await xd.start()
        bot_me = await xd.get_me()
        set_client(bot_me.id, xd)
        await set_clone_menu(xd)
        running_clones[bot_me.id] = xd

        print(f"✅ Restarted clone @{bot_me.username} ({bot_me.id})")

        # Restart auto-post task if enabled
        clone = await db.get_clone(bot_me.id)
        if clone and clone.get("auto_post", False):
            auto_post_channel = clone.get("ap_channel")
            if auto_post_channel:
                task = asyncio.create_task(auto_post_clone(bot_me.id, db, auto_post_channel))
                auto_post_tasks[bot_me.id] = task
                print(f"▶️ Auto-post resumed for @{bot_me.username}")

    except FloodWait as e:
        print(f"⏱ FloodWait {e.value}s for {bot_id}")
        await asyncio.sleep(e.value)
        await restart_single_clone(bot_data)

    except (UserDeactivated, AuthKeyUnregistered):
        print(f"⚠️ Bot {bot_id} deactivated — removing from DB")
        await db.delete_clone_by_id(bot_id)

    except Exception as e:
        if "SESSION_REVOKED" in str(e) or "ACCESS_TOKEN_EXPIRED" in str(e):
            print(f"⚠️ Token revoked for {bot_id} — removing from DB")
            await db.delete_clone_by_id(bot_id)
        else:
            print(f"❌ Error restarting bot {bot_id}: {e}")


# -------------------------------------------------
# RESTART ALL CLONES
# -------------------------------------------------
async def restart_all_clones():
    print("♻️ Restarting all clone bots...")
    bots_cursor = await db.get_all_clone()
    bots = await bots_cursor.to_list(None)
    semaphore = asyncio.Semaphore(10)

    async def sem_task(bot):
        async with semaphore:
            await restart_single_clone(bot)

    await asyncio.gather(*(sem_task(bot) for bot in bots))
    print("✅ All clone bots restarted successfully.")


# -------------------------------------------------
# PERIODIC AUTO-RESTART SCHEDULER
# -------------------------------------------------
async def schedule_clone_restart(hours: int = 6):
    """Automatically restart all clone bots every X hours."""
    while True:
        try:
            await restart_all_clones()
        except Exception as e:
            print(f"⚠️ Error during scheduled restart: {e}")
        print(f"🕒 Next restart in {hours} hours...")
        await asyncio.sleep(hours)

async def start():
    logger.info("Initializing Bot...")
    await StreamBot.start()
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    await set_auto_menu(StreamBot)

    await assistant.start()
    logger.info(f"Assistant {(await assistant.get_me()).username} started")

    load_plugins()
    await initialize_clients()
    #await start_web_server()
    #await restart_bots()

    asyncio.create_task(schedule_clone_restart(hours=60))

    try:
        today = date.today()
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        await dispatch_task(LOG_CHANNEL, script.RESTART_TXT.format(today, now))
    except Exception:
        logger.warning("Failed to send restart log")

    logger.info("Bot fully started. Idle mode...")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info("Service Stopped Bye 👋")
        loop.run_until_complete(assistant.stop())
        loop.run_until_complete(StreamBot.stop())
