from imports import *
from plugins.config import *
from plugins.database import *
from plugins.helper import *
from plugins.script import *
from owner.owner import *
from clone.clone import *

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

StartTime = pytime.time()
__version__ = 1.1

class StreamXBot(Client):

    def __init__(self):
        super().__init__(
            name="filetolink",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "owner"},
            sleep_threshold=5,
        )
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
      
StreamBot = StreamXBot()

multi_clients = {}
work_loads = {}

class TokenParser:
    def __init__(self, config_file: Optional[str] = None):
        self.tokens = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        self.tokens = dict(
            (c + 1, t)
            for c, (_, t) in enumerate(
                filter(
                    lambda n: n[0].startswith("MULTI_TOKEN"), sorted(environ.items())
                )
            )
        )
        return self.tokens

async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    
    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                sleep_threshold=SLEEP_THRESHOLD,
                workers=20,
                no_updates=True,
                in_memory=True
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")

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

routes = web.RouteTableDef()

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
            "version": __version__,
        }
    )

async def restart_bots():
    bots_cursor = await db.get_all_clone()
    bots = await bots_cursor.to_list(None)

    semaphore = asyncio.Semaphore(10)
    tasks = []

    async def restart_single(bot):
        bot_token = bot["token"]
        bot_id = bot["_id"]
        try:
            async with semaphore:
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
                print(f"✅ Restarted clone bot @{bot_me.username} ({bot_me.id})")

            clone = await db.get_clone(bot_me.id)
            if clone and clone.get("auto_post", False):
                auto_post_channel = clone.get("ap_channel", None)
                if auto_post_channel:
                    asyncio.create_task(
                        auto_post_clone(bot_me.id, db, auto_post_channel)
                    )
                    print(f"▶️ Auto-post started for @{bot_me.username}")
        except FloodWait as e:
            print(f"⏱ FloodWait: sleeping {e.value} seconds")
            await asyncio.sleep(e.value)
            async with semaphore:
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
                print(f"✅ Restarted clone bot @{bot_me.username} ({bot_me.id})")

            clone = await db.get_clone(bot_me.id)
            if clone and clone.get("auto_post", False):
                auto_post_channel = clone.get("ap_channel", None)
                if auto_post_channel:
                    asyncio.create_task(
                        auto_post_clone(bot_me.id, db, auto_post_channel)
                    )
                    print(f"▶️ Auto-post started for @{bot_me.username}")
        except (UserDeactivated, AuthKeyUnregistered):
            print(f"⚠️ Bot {bot_id} invalid/deactivated. Removing from DB...")
            await db.delete_clone_by_id(bot_id)
        except Exception as e:
            if "SESSION_REVOKED" in str(e) or "ACCESS_TOKEN_EXPIRED" in str(e):
                print(f"⚠️ Token expired or revoked for bot {bot_id}, removing from DB...")
                await db.delete_clone_by_id(bot_id)
            else:
                print(f"❌ Error restarting bot {bot_id}: {e}")

    for bot in bots:
        tasks.append(restart_single(bot))

    await asyncio.gather(*tasks)
    print("✅ All clone bots processed for restart.")

"""async def auto_restart_loop():
    while True:
        print("🔁 Starting scheduled bot restart...")
        await restart_bots()
        print("🕗 Sleeping for 8 hours before next restart...\n")
        await asyncio.sleep(8 * 60 * 60)"""

"""async def init_auto_deletes(client, db: Database):
    scheduled = await db.get_all_scheduled_deletes()

    for task in scheduled:
        chat_id = task["chat_id"]
        message_ids = task["message_ids"]
        notice_id = task["notice_id"]
        delete_at = task["delete_at"]
        reload_url = task.get("reload_url")

        if delete_at.tzinfo is None:
            delete_at = delete_at.replace(tzinfo=timezone.utc)

        delay_time = (delete_at - datetime.now(timezone.utc)).total_seconds()
        if delay_time < 0:
            delay_time = 0

        asyncio.create_task(
            schedule_delete(client, db, chat_id, message_ids, notice_id, delay_time, reload_url)
        )"""

StreamBot.start()

async def start():
    print('\n')
    print('Initalizing KM File Store Bot')
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    await set_auto_menu(StreamBot)

    await assistant.start()
    print(f"Assistant {(await assistant.get_me()).username} started")
    await initialize_clients()

    for name in glob.glob("owner/*.py"):
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"owner/{plugin_name}.py")
            import_path = "owner.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Imported => " + plugin_name)

    me = await StreamBot.get_me()

    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await StreamBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    
    #app = web.AppRunner(await web_server())
    #await app.setup()
    #bind_address = "0.0.0.0"
    #await web.TCPSite(app, bind_address, PORT).start()

    await restart_bots()
    print("Bot Started Powered By @VJ_Botz")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info("Service Stopped Bye 👋")
        loop.run_until_complete(assistant.stop())
        loop.run_until_complete(StreamBot.stop())
