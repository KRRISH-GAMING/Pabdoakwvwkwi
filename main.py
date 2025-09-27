# main.py
import logging
import asyncio
import importlib.util
import sys
import pytz
import time
from typing import Dict
from os import environ
from pathlib import Path
from datetime import date, datetime
from aiohttp import web
from pyrogram import *
from pyrogram.errors import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *
from owner.owner import *

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

multi_clients: Dict[int, Client] = {}
work_loads: Dict[int, int] = {}

StartTime = time.time()
APP_VERSION = "1.1"

routes = web.RouteTableDef()

# ---------- Main Bot ----------
class StreamXBot(Client):
    def __init__(self):
        super().__init__(
            name="filetolink",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=25,  # ✅ main bot balanced
            plugins={"root": "owner"},
            sleep_threshold=5,
        )

StreamBot = StreamXBot()

# ---------- Benchmark Updates/sec ----------
update_counts: Dict[int, int] = {}

def register_client_for_stats(client: Client, client_id: int):
    update_counts[client_id] = 0

    @client.on_raw_update()
    async def count_updates(_, __, ___):
        update_counts[client_id] += 1

async def log_updates_per_sec():
    while True:
        await asyncio.sleep(10)
        stats = []
        for cid, count in update_counts.items():
            ups = count / 10
            bot_name = "MainBot" if cid == 0 else f"Clone-{cid}"
            stats.append(f"{bot_name}: {ups:.2f} ups")
            update_counts[cid] = 0
        if stats:
            logging.info("⚡ " + " | ".join(stats))

# ---------- Fast Parallel Restart ----------
async def restart_bots():
    bots = [bot async for bot in db.get_all_bots()]

    async def restart_single(bot):
        bot_token = bot.get("token")
        db_id = bot["_id"]
        bot_id = bot["bot_id"]

        if not bot_token:
            print(f"⚠️ Skipping bot {db_id}: missing token")
            return

        try:
            xd = Client(
                name=f"clone_{bot_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=bot_token,
                workers=8,  # ✅ lighter for clones
                sleep_threshold=60,
                plugins={"root": "clone"},
                no_updates=True,
                in_memory=True
            )
            await xd.start()
            me = await xd.get_me()

            # ✅ Register in both systems
            set_client(me.id, xd)           # your global registry
            multi_clients[me.id] = xd       # my optimization
            work_loads[me.id] = 0
            register_client_for_stats(xd, me.id)

            print(f"✅ Restarted clone bot @{me.username} ({me.id})")

            # Auto-post if enabled
            """fresh = await db.get_clone_by_id(me.id)
            if fresh and fresh.get("auto_post"):
                auto_post_channel = fresh.get("auto_post_channel")
                if auto_post_channel:
                    async def runner():
                        try:
                            from owner.clone import auto_post_clone
                            await auto_post_clone(me.id, db, auto_post_channel)
                        except Exception as e:
                            print(f"❌ Auto-post crashed for @{me.username}: {e}")
                    asyncio.create_task(runner())
                    print(f"▶️ Auto-post started for @{me.username}")"""

        except UserDeactivated:
            print(f"⚠️ Bot @{bot_id} deactivated. Removing from DB...")
            await db.delete_clone_by_id(db_id)
        except Exception as e:
            print(f"❌ Error while restarting clone {bot_id}: {e}")

    # 🚀 Restart all clones in parallel
    await asyncio.gather(*(restart_single(bot) for bot in bots))

# ---------- Token Parser ----------
class TokenParser:
    def __init__(self, config_file=None):
        self.tokens = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        self.tokens = dict(
            (c + 1, t)
            for c, (_, t) in enumerate(
                filter(lambda n: n[0].startswith("MULTI_TOKEN"), sorted(environ.items()))
            )
        )
        return self.tokens

# ---------- Multi-Client Init ----------
async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        logging.info("No additional clients found, using default client")
        return

    async def start_client(client_id, token):
        try:
            logging.info(f"Starting Clone - Client {client_id}")
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                workers=8,
                sleep_threshold=60,
                no_updates=True,
                in_memory=True
            ).start()
            work_loads[client_id] = 0
            register_client_for_stats(client, client_id)
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id}", exc_info=True)
            return None

    results = await asyncio.gather(
        *[start_client(i, token) for i, token in all_tokens.items()],
        return_exceptions=True
    )
    valid_clients = dict(filter(None, results))
    multi_clients.update(valid_clients)

    if len(multi_clients) > 1:
        logging.info(f"Multi-Client Mode Enabled: {len(multi_clients)} bots running")
    else:
        logging.info("No additional clients were initialized, using default client")

# ---------- Utils ----------
def get_readable_time(seconds: int) -> str:
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", " days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "
    time_list.reverse()
    readable_time += ": ".join(time_list)
    return readable_time

def load_plugins(path="owner"):
    for file in Path(path).glob("*.py"):
        name = file.stem
        import_path = f"{path}.{name}"
        if import_path in sys.modules:
            continue
        spec = importlib.util.spec_from_file_location(import_path, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[import_path] = module
        logging.info(f"✅ Imported => {name}")

# ---------- Web Server ----------
@routes.get("/", allow_head=True)
async def root_route_handler(_):
    return web.json_response(
        {
            "server_status": "running",
            "uptime": get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + StreamBot.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "version": APP_VERSION,
        }
    )

async def web_server():
    web_app = web.Application(client_max_size=30_000_000)
    web_app.add_routes(routes)
    runner = web.AppRunner(web_app)
    await runner.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(runner, bind_address, PORT).start()

# ---------- Startup ----------
async def start():
    logging.info("🚀 Initializing Bot...")

    await StreamBot.start()
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username

    # ✅ Register main bot
    register_client_for_stats(StreamBot, 0)

    # ✅ Ensure MongoDB indexes
    await db.ensure_indexes()

    await set_auto_menu(StreamBot)
    await assistant.start()
    logging.info(f"✅ Assistant {(await assistant.get_me()).username} started")

    await initialize_clients()
    load_plugins("owner")

    # ✅ Start update logger
    asyncio.create_task(log_updates_per_sec())

    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M:%S")

    await StreamBot.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(today, current_time),
    )

    # ✅ Restart clones in parallel
    await restart_bots()
    logging.info("Bot Started.")

    # optional: run web server
    # await web_server()

    await idle()

# ---------- Entrypoint ----------
if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logging.info("Service Stopped Bye 👋")
        asyncio.run(assistant.stop())
        asyncio.run(StreamBot.stop())