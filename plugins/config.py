import re, os

try:
    id_pattern = re.compile(r"^.\d+$")

    # Bot Information
    API_ID = int(os.environ.get("API_ID", "15479023"))
    API_HASH = os.environ.get("API_HASH", "f8f6cf547822449c29fc60dae3b31dd4")
    SESSION_STRING = os.environ.get("SESSION_STRING", "BQDsMO8AYBThDSMHkoXplgI2_wYTP-7m6WX79Yn9ihzDp0Ika1b025mWfR9gYs0-BOukentqjnsb1izUT4Mg_5HHnbqOB_ZLPvgNaMAGRCCgM2HYPxB531pGoZvNh2gpIqE2m4OE7DGreCjyy_R_wCOrkSh559u7T1rSYAQrJ1N_TQ7hRNe55gPMweG0eEJgUFvrf2pkP_iWF8ifxncWHr1u8av868qPUaYyUxdGQPo7_ChsdKq8unSj_UU4xakuNx8X6GQTStF1Uc3iM4Yb1VDWfojj_ByVPmnT8XIE8qQJLVV-gy8uN96Uhryt-nMPm2HDF1Hnzq60SZiZd-FsHeh2epOhZQAAAABaJgrVAA")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8459663050:AAHlICH3sLKfmoBkM5IzzApJOkhzJohQqcU")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "XclusiveMembershipBot") # without @

    # Database Information
    DB_URI = os.environ.get("DB_URI", "mongodb+srv://KM-Membership:KM-Membership123@km-membership.8xbdxy0.mongodb.net/?retryWrites=true&w=majority&appName=KM-Membership")
    DB_NAME = os.environ.get("DB_NAME", "membership")

    # Moderator Information
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get("ADMINS", "1512442581").split()]

    # Channel Information
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002937162790"))

    # This Is Force Subscribe Channel, also known as Auth Channel 
    auth_channel = os.environ.get("AUTH_CHANNEL", "-1002829948273") # give your force subscribe channel id here else leave it blank
    AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
except Exception as e:
    print("⚠️ Error loading config.py:", e)
    traceback.print_exc()
