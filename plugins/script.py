class script(object):
    START_TXT = """Hello {user} 👋 

My name is {bot}.

I am a permanent file store bot.  

Users can access stored messages using the shareable links I provide.

To know more, click the **Help** button."""

    HELP_TXT = """<u>**✨ HELP MENU**</u>

I am a permanent file store bot.  

You can store files from your public channel without me being an admin.  

If your channel or group is private, please make me an admin first.  

Once set up, you can store your files using the commands below and access them via shareable links.

📚 Available Commands:
🔻 /start - Check if I am alive.  
🔻 /help - View help menu.  
🔻 /genlink - Store a single message or file.  
🔻 /batch - Store multiple messages from a channel.  
🔻 /broadcast - Broadcast a message to all users.  
🔻 /stats - View bot statistics.  
🔻 /contact - Message the admin."""

    ABOUT_TXT = """<u>**✨ ABOUT ME**</u>

🤖 Name: {bot}  
📝 Language: <a href=https://www.python.org>Python 3</a>  
📚 Library: <a href=https://docs.pyrogram.org>Pyrogram</a>  
🧑🏻‍💻 Developer: <a href=https://t.me/DeadxNone>Developer</a>  
👥 Support Group: <a href=https://t.me/+8E9nKxs8Y-Y2OGRl>Support</a>  
📢 Update Channel: <a href=https://t.me/+YczdaoCKP-AxMWFl>Updates</a>"""

    CABOUT_TXT = """<u>**✨ ABOUT ME**</u>

🤖 Name: {bot}  
📝 Language: <a href=https://www.python.org>Python 3</a>  
📚 Library: <a href=https://docs.pyrogram.org>Pyrogram</a>  
🧑🏻‍💻 Developer: <a href=tg://user?id={developer}>Developer</a>"""

    MANAGEC_TXT = """<u>**✨ MANAGE CLONE**</u>

Manage and create your very own clone bot, identical to me, with all the same awesome features.  

Use the buttons below to get started."""

    CLONE_TXT = """1️⃣ Send <code>/newbot</code> to @BotFather.  
2️⃣ Choose a name for your bot.  
3️⃣ Choose a unique username.  
4️⃣ BotFather will give you a token.  
5️⃣ Forward that token message to me.  

Then I’ll create a clone bot for you 😌"""

    CUSTOMIZEC_TXT = """<u>**✨ CUSTOMIZE CLONE**</u>

🖍️ Username: {username}

Modify and customize your clone bot from here."""

    ST_MSG_TXT = """<u>**✨ START MESSAGE**</u>

Customize the start message of your clone bot using the options below."""

    ST_TXT_TXT = """<u>**✨ START TEXT**</u>

Personalize the start message text of your clone bot to suit your preferences."""

    EDIT_ST_TXT = """<code>{user}</code> → mention user

Example:
Hi {user} 👋  
I am a file store bot.

📝 Now send your new start message text."""

    ST_PIC_TXT = """<u>**✨ START PHOTO**</u>

Include a photo to be displayed along with your start message."""

    EDIT_ST_PIC = """🖼️ Please upload the new start photo you would like to use.

ℹ️ This photo will be shown in your bot’s start message."""

    CAPTION_TXT = """<u>**✨ CUSTOM CAPTION**</u>

Add a custom caption to your media messages instead of using the original caption.

Available placeholders:
<code>{file_name}</code> → File name  
<code>{file_size}</code> → File size  
<code>{caption}</code> → Original caption"""

    EDIT_CAPTION_TXT = """📝 Please provide the new caption text you want to set.

ℹ️ This caption will be applied to your shareable link messages."""

    BUTTON_TXT = """<u>**✨ CUSTOM BUTTON**</u>

Add up to 3 custom buttons to your media messages."""

    EDIT_BUTTON_TXT = """🔘 Please provide the button name and URL you want to add.

ℹ️ The name will be shown on the button, and the URL will open when users click it."""

    CH_MSG_TXT = """<u>**✨ CHANNEL MESSAGE**</u>

Customize the channel message of your clone bot using the options below."""

    WORD_FILTER_TXT = """<u>**✨ OFFENSIVE WORD FILTER**</u>

Block or filter offensive words in forwarded or posted messages.

Current Status: {status}"""

    BAD_WORDS = [
    # Hindi/Indian slangs
    "madarchod", "behenchod", "chutiya", "lund", "chut", "randi", "chod", "gand", "gandi",
    "sala", "suar", "gadha", "hijra", "bhen ki lund", "maa ki chut", "chodai", "luda",
    "randi ka lund", "haramkhor", "haramzada", "chutmar", "gandmar", "chutiyapa", "lundch",
    "lundka", "randiwali", "hori", "kaminey", "kamina", "betichod", "maa chudai",
    "chut ki gand", "nangi", "nangi ladki", "nanga", "bhosdiwala", "bhosdike", "gandfat", "chutfat",
    "lundgand", "gaand", "gaandfat", "chutgand", "lundmar", "chutkala", "lundkala", "bhosdk",
    "bhenchode", "madarchode", "chutwa", "lundwa", "ludka", "lodu", "bc", "mc", "bcch",
    "bcchd", "behench", "bhosdi", "gandu", "madar", "randiya", "chutiyapa", "harami", "chodu",
    
    # English slangs / curse words
    "fuck", "fucker", "bastard", "bitch", "asshole", "dickhead", "motherfucker", "sonofabitch",
    "cunt", "slut", "whore", "cock", "pussy", "tits", "boobs", "penis", "vagina", "cum",
    "ejaculate", "masturbate", "jerkoff", "gangbang", "porn", "pornhub", "xvideo", "xxx",
    "18+", "adult", "sexvideo", "pornstar", "fuckboy", "fuckgirl", "sexy", "horny", "naked",
    "nude", "stripper", "prostitute", "callgirl", "hooker", "brothel", "sexworker", "sugarbaby",
    "sugardaddy", "sexually", "boobies", "nipples", "jerking", "fucking", "fucked", "fucks",
    "ass", "anal", "blowjob", "handjob", "cumshot", "orgasm", "threesome", "69", "bdsm",
    "bondage", "fetish", "kinky", "spank", "pussylick", "dildos", "vibrator", "pornvideo",
    "sexgame", "sexchat", "sexcam", "nipple", "slutshaming", "cocktail", "hornytime",
    # General insults
    "idiot", "stupid", "moron", "dumb", "loser", "scumbag", "trash", "asshat", "dipshit", "jerk",
    "fool", "twat", "prick", "imbecile", "dork", "weirdo", "slob", "nerd", "loser", "simp", "sex"
]

    MEDIA_FILTER_TXT = """<u>**✨ OFFENSIVE MEDIA FILTER**</u>

Automatically block or filter offensive media in forwarded or posted messages.

Current Status: {status}"""

    RANDOM_CAPTION_TXT = """<u>**✨ RANDOM CAPTION**</u>

Enable random captions for your forwarded or posted messages.

Current Status: {status}"""

    CAPTION_LIST = [
    "Jo dikha hai, woh sirf ek jhalak hai 🥵💦",
    "Tumhein samajh nahi aayega, yeh dekhna padega 🔥💋",
    "Dekho, aur dil se mehsoos karo 🥵💞",
    "Tumhare chehre pe smile aayega, bas dekhte jao 😏💘",
    "Yaar, tumhe dekhne ke baad toh sab kuch perfect lagta hai 😏🍑",
    "Aise chehre pe smile toh zaroori hai 😏💖",
    "Aankhon mein kho jaoge, bas dekhte jao 😜🔥",
    "Yeh jo feeling hai, bas dekhne se aayegi 😜💖",
    "Aankhon se jaadu hai, dil toh hil jaayega 😏🍑",
    "Tumhara control toh gayab ho jayega 😘💦",
    "Kya baat hai, bas dekhte jao 😘💥",
    "Dil se dekho, phir samajh mein aayega 🔥💋",
    "Bhai, dekh toh sahi, dil hil jayega 😜🔥",
    "Ek dekhne ke baad, tumhe apna control lose ho jayega 😩💋",
    "Jo baat dekhne mein hai, woh kisi aur mein kahan 😜💋",
    "Yaar, yeh jo scene hai, bilkul mind-blowing hai 🔥🍑",
    "Bhai, dekh toh sahi, kaisa maal hai 😜💥",
    "Yeh dekhne ke baad toh sab kuch chhup jaayega 😜🔥",
    "Tumhare steps mein kuch toh magic hai 😘💞",
    "Tumhara chehra kuch toh special hai 😏🔥",
    "Jo dekhne ka hai, woh kisi aur mein kahan 😈🍑",
    "Ek baar dekh lo, phir pyaar ho jayega 🔥💘",
    "Kya scene hai yaar, bas dekhte hi reh jaoge 😘💥",
    "Bas aankhon mein bhar lo, phir nasha chadh jaayega 😏💦",
    "Tumhari adaayein toh dil todne ke liye bani hain 😜💋",
    "Tumhare moves dekh kar toh dil garden garden ho gaya 😏🔥",
    "Bas ek baar dekh lo, fir repeat pe chal jaayega 😜💥",
    "Yeh smile toh dil tod ke bhi dil jeet leti hai 😘💖",
    "Jo vibe yaha mil rahi hai, wo kahin aur nahi 😩🔥",
    "Tumhein dekhkar lagta hai duniya hi perfect hai 💘✨",
    "Bas aankhon mein basa lo, phir nasha ho jaayega 😜💞",
    "Yaar, aaj toh tumhe dekh kar dil ki dhadkan tez ho gayi 😘🔥",
    "Jo feel yaha milti hai, wo aur kahin nahi milti 💋💦",
    "Tumhari style hi kuch alag level ka nasha hai 😈🍑",
    "Bas dekhte rehna, samajh aayega asli maza kya hai 😏🔥",
    "Tera look hi full killer hai bhai 😜💥",
    "Aankhon mein aisa jaadu hai, ki control mushkil hai 😘💦",
    "Bas ek baar dekh, aur phir addiction ho jaayega 🔥💖",
    "Jo tum mein charm hai, wo kisi aur mein nahi 😈💘",
    "Yeh dekhne ke baad toh dimag hi fly ho gaya 😜🔥",
    "Aankhon ka nasha sabse strong hota hai 😏💋",
    "Bas ek pal ke liye dekh lo, aur sab bhool jao 💞🔥",
    "Tumhari vibe hi full romantic hai 😘💥",
    "Jo maza tum mein hai, wo duniya mein nahi 😩💖",
    "Dil keh raha hai, bas aur dekhte raho 😜🍑",
    "Bas ek nazar aur, aur dil poora tumhara ho jaayega 😏🔥",
    "Yeh jo killer look hai, yehi sabko fida kar raha hai 😈💦",
    "Tumhein dekhkar lagta hai jaise sapna sach ho gaya 😘💞",
    "Jo tumhari ada hai, wahi sabko pagal bana rahi hai 😏💋",
    "Aaj toh tumhein dekhkar asli fire feel hua 🔥🔥",
    "Bas ek baar dekh, phir toh repeat button tod dega 😏💥",
    "Aankhon mein aisa magic hai ki dil hil jaata hai 😜🔥",
    "Yeh vibe dekhkar toh pura din mast ho gaya 😘💖",
    "Jo look tumhara hai, wo full HD fire hai 🔥💋",
    "Bas ek baar samajh lo, asli maza abhi aayega 😈🍑",
    "Tumhein dekh kar lagta hai life ka best scene hai 😍💞",
    "Yeh jo smile hai, yehi sabko fida kar rahi hai 😏🔥",
    "Bas aankhon mein basa lo, phir nasha ho jaayega 😘💥",
    "Tumhari ada toh pura dil loot leti hai 😜💖",
    "Jo style tumhari hai, wo sab pe heavy hai 😎🔥",
    "Aankhon se hi game khatam kar diya tumne 😈💦",
    "Tumhein dekhkar lagta hai duniya slow-motion ho gayi 😘💞",
    "Bas ek pal ke liye dekh, aur dil tumhara ho gaya 😩💋",
    "Yeh look dekhne ke baad toh control mushkil hai 😜🔥",
    "Tumhari vibe hi sabse classy aur sassy hai 😏💘",
    "Bas dekhte jao, aur pyaar hota jaayega 💞🔥",
    "Yeh scene dekhkar lagta hai full movie chal rahi hai 😎💥",
    "Tumhari aankhon mein pura universe chhupa hai 😘💖",
    "Jo baat tummein hai, wo kahin aur nahi 😈🍑",
    "Bas ek baar samajh lo, asli maza yahi hai 😏🔥",
    "Yeh ada dekhkar toh sab hil jaate hain 😘💥",
    "Tumhein dekhkar lagta hai zindagi successful ho gayi 😍💞",
    "Jo feel tumhari hai, wo bas addictive hai 😜💖",
    "Bas aankhon se hi sab kuch samajh jaata hoon 😈💋",
    "Aaj tumhein dekhkar asli fire nikal gaya 🔥🔥",
    "Yeh dekhkar lagta hai full HD se bhi zyada clear fire hai 😏💥",
    "Bas ek pal tumhein dekh loon, din ban jaata hai 😍💖",
    "Jo swag tumhari vibe mein hai, wo kahin aur nahi 😎🔥",
    "Tumhari aankhon mein jo baat hai, wo words mein nahi 😘💋",
    "Bas ek baar smile karo, sabko fida kar doge 😏💞",
    "Yeh look toh pura game changer hai 😈🍑",
    "Tumhein dekhkar lagta hai asli paradise yehi hai 😘🔥",
    "Bas aankhon se hi sab kuch keh diya tumne 😍💘",
    "Jo feel tumse aati hai, wo addictive hai 😏💥",
    "Tumhari vibe ekdum classy aur sexy hai 😎💋",
    "Bas ek baar nazar lag jaaye toh dil udd jaata hai 😜🔥",
    "Tumhari ada dekhkar lagta hai sab hil jaayega 😘💖",
    "Jo look tumhara hai, wo full fire mode mein hai 🔥🔥",
    "Aankhon se khud hi dil chura leti ho 😏💘",
    "Bas tumhein dekhte hi sab tension gayab ho jaati hai 😍💞",
    "Tumhein dekhkar lagta hai asli beauty tum ho 😘💥",
    "Jo charm tumhara hai, wo kahin aur nahi milega 😈🍑",
    "Yeh vibe toh direct dil mein utar jaati hai 😏💖",
    "Tumhari muskaan hi sabko addict kar deti hai 😜🔥",
    "Bas ek baar tumhein dekh loon, control mushkil ho jaata hai 😩💋",
    "Jo fire tumse nikalti hai, wo sab pe heavy hai 🔥💥",
    "Tumhein dekhkar lagta hai zindagi perfect hai 😍💘",
    "Aankhon se hi ek nasha sa ho jaata hai 😘💞",
    "Jo energy tumhari hai, wo sabko attract karti hai 😏🔥",
    "Bas tumhari vibe dekhkar mood full on ho jaata hai 😎💥"
]

    HEADER_TXT = """<u>**✨ CUSTOM HEADER**</u>

Add a custom header that will appear at the top of every forwarded or posted message."""

    EDIT_HEADER_TXT = """📝 Please send the header text you would like to set.

ℹ️ This text will automatically appear at the **top** of every forwarded or posted message."""

    FOOTER_TXT = """<u>**✨ CUSTOM FOOTER**</u>

Add a custom footer that will appear at the bottom of every forwarded or posted message."""

    EDIT_FOOTER_TXT = """📝 Please send the footer text you would like to set.

ℹ️ This text will automatically appear at the **bottom** of every forwarded or posted message."""

    FSUB_TXT = """<u>**✨ FORCE SUBSCRIBE**</u>

Users must join your required channels before they can use the clone bot.

You can add up to **4 channels**."""

    EDIT_FSUB_TXT = """🔗 Please send me the channel ID or username you want to add for Force Subscribe.

✅ Examples:
`-1001234567890` → private channel ID  
`@YourChannel` → public channel username

⚠️ Note: Make sure I am an **admin** in that channel with permission to invite users."""

    TOKEN_TXT = """<u>**✨ ACCESS TOKEN**</u>

Users must complete a verification link to gain special access to messages from all clone shareable links.

The access remains valid for the configured validity period.

Current Status: {status}"""

    AT_VALIDITY_TXT = """<u>**✨ ACCESS TOKEN VALIDITY**</u>

You can set how long the special access (via access token) will remain valid. 

Once this period ends, users will need to verify again to continue without ads."""

    AT_TUTORIAL_TXT = """<u>**✨ ACCESS TOKEN TUTORIAL**</u>

You can provide a tutorial link to guide users on how the access token works 
and how it removes ads when accessing clone links."""

    AUTO_POST_TXT = """<u>**✨ AUTO POST**</u>

You can enable automatic posting to your channel. 

When enabled, the bot will automatically send posts at the configured interval.

Current Status: {status}"""

    AP_IMG_TXT = """<u>**✨ AUTO POST IMAGE**</u>

Include a photo to be displayed along with your auto post."""

    EDIT_AP_IMG = """🖼️ Please upload the new auto post image you would like to use.

ℹ️ This image will be shown in your auto post."""

    AP_SLEEP_TXT = """<u>**✨ AUTO POST SLEEP**</u>

You can customize the waiting time (sleep) between one auto post and the next.

This controls how long the bot waits before sending another auto post to users."""

    PREMIUM_TXT = """<u>**✨ PREMIUM USERS**</u>

Premium users can access all your clone shareable links without restrictions."""

    DELETE_TXT = """<u>**✨ AUTO DELETE**</u>

You can enable or disable automatic message deletion.

Current Status: {status}"""

    AD_TIME_TXT = """<u>**✨ AUTO DELETE TIME**</u>

Set how long messages will remain before being automatically deleted."""

    AD_MSG_TXT = """<u>**✨ AUTO DELETE MESSAGE**</u>

Customize the warning message shown to users before their messages are auto-deleted."""

    AD_TXT = """<u>⚠️ IMPORTANT</u>

All messages will be deleted after {time} {unit}.  

Please save or forward them to your personal saved messages to avoid losing them!"""

    FORWARD_TXT = """<u>**✨ FORWARD PROTECTION**</u>

Restrict users from forwarding messages received through clone shareable links.

Current Status: {status}"""

    MODERATOR_TXT = """<u>**✨ MODERATOR**</u>

Moderators can manage all clone features and have special access permissions."""

    REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"]

    RESTART_TXT = """
<b>Bot Restarted !

📅 Date : <code>{}</code>
⏰ Time : <code>{}</code>
🌐 Timezone : <code>Asia/Kolkata</code>
🛠️ Build Status : <code>v2.7.1 [ Stable ]</code></b>"""

    LOG_TEXT = """<b>#NewUser
    
Id - <code>{}</code>

Name - {}</b>"""
