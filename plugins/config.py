import re, os

def is_enabled(value, default):
    try:
        if value.lower() in ["true", "yes", "1", "enable", "y"]:
            return True
        elif value.lower() in ["false", "no", "0", "disable", "n"]:
            return False
        else:
            return default
    except Exception as e:
        print("⚠️ Error in is_enabled:", e)
        return default

try:
    id_pattern = re.compile(r"^.\d+$")

    PORT = os.environ.get("PORT", "8080")

    # Bot Information
    API_ID = int(os.environ.get("API_ID", "35384565"))
    API_HASH = os.environ.get("API_HASH", "dbba8a136120df358bd3b6e1fbc18792")
    SESSION_STRING = os.environ.get("SESSION_STRING", "BQDsMO8AYBThDSMHkoXplgI2_wYTP-7m6WX79Yn9ihzDp0Ika1b025mWfR9gYs0-BOukentqjnsb1izUT4Mg_5HHnbqOB_ZLPvgNaMAGRCCgM2HYPxB531pGoZvNh2gpIqE2m4OE7DGreCjyy_R_wCOrkSh559u7T1rSYAQrJ1N_TQ7hRNe55gPMweG0eEJgUFvrf2pkP_iWF8ifxncWHr1u8av868qPUaYyUxdGQPo7_ChsdKq8unSj_UU4xakuNx8X6GQTStF1Uc3iM4Yb1VDWfojj_ByVPmnT8XIE8qQJLVV-gy8uN96Uhryt-nMPm2HDF1Hnzq60SZiZd-FsHeh2epOhZQAAAABaJgrVAA")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8382815364:AAFWKZGynQi_cNt7mAkuCxDyzbo4StY6k8s")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "KMFileStoreBot") # without @

    # Database Information
    DB_URI = os.environ.get("DB_URI", "mongodb+srv://KM-Main:KM-Main123@km-main.qpiat2x.mongodb.net/?retryWrites=true&w=majority&appName=KM-Main")
    DB_NAME = os.environ.get("DB_NAME", "main")

    # Clone Database Information
    CLONE_DB_URI = os.environ.get("CLONE_DB_URI", "mongodb+srv://KM-Clone:KM-Clone123@km-clone.y2ynhi5.mongodb.net/?retryWrites=true&w=majority&appName=KM-Clone")
    CDB_NAME = os.environ.get("CDB_NAME", "clone")

    # Moderator Information
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get("ADMINS", "8477930865").split()]

    # Channel Information
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003551728019"))
    SINGLE_CHANNEL = int(os.environ.get("SINGLE_CHANNEL", "-1003122680068"))
    BATCH_CHANNEL = int(os.environ.get("BATCH_CHANNEL", "-1002745649036"))

    # This Is Force Subscribe Channel, also known as Auth Channel 
    auth_channel = os.environ.get("AUTH_CHANNEL", "-1002829948273") # give your force subscribe channel id here else leave it blank
    AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
except Exception as e:
    print("⚠️ Error loading config.py:", e)
    traceback.print_exc()
