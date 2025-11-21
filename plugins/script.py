class script(object):
    RESTART_TXT = """<b><u>BOT RESTARTED !</u></b>

📅 Date : <code>{}</code>
⏰ Time : <code>{}</code>
🌐 Timezone : <code>Asia/Kolkata</code>
🛠️ Build Status : <code>v2.7.1 [ Stable ]</code>"""

    LOG_TEXT = """<b><u>#NewUser</u></b>
    
Id - <code>{}</code>

Name - {}

Username - {}

From - @KMCloneManagerBot"""

    START_TXT = """Hello {user} 👋 

My name is {bot}.

I am a permanent file store bot.  

Users can access stored messages using the shareable links I provide.

To know more, click the **Help** button."""

    HELP_TXT = """<b><u>✨ HELP MENU</u></b>

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
🔻 /ban - Ban a user.
🔻 /unban - Unban a user.
🔻 /list_ban - Show all ban users.
🔻 /stats - View bot statistics.
🔻 /contact - Message the admin."""

    ABOUT_TXT = """<b><u>✨ ABOUT ME</u></b>

🤖 Name: {bot}  
📝 Language: <a href=https://www.python.org>Python 3</a>  
📚 Library: <a href=https://docs.pyrogram.org>Pyrogram</a>  
🧑🏻‍💻 Developer: <a href=https://t.me/DeadxNone>Developer</a>  
👥 Support Group: <a href=https://t.me/+8E9nKxs8Y-Y2OGRl>Support</a>  
📢 Update Channel: <a href=https://t.me/+YczdaoCKP-AxMWFl>Updates</a>"""

    CABOUT_TXT = """<b><u>✨ ABOUT ME</u></b>

🤖 Name: {bot}  
📝 Language: <a href=https://www.python.org>Python 3</a>  
📚 Library: <a href=https://docs.pyrogram.org>Pyrogram</a>  
🧑🏻‍💻 Developer: <a href=tg://user?id={developer}>Developer</a>"""

    MANAGEC_TXT = """<b><u>✨ MANAGE CLONE</u></b>

💎 Premium Status: {premium_status} ({plan_type})
⏰ Premium Expiry: {expiry}

Manage and create your very own clone bot, identical to me, with all the same awesome features.  

Use the buttons below to get started."""

    CLONE_TXT = """1️⃣ Send <code>/newbot</code> to @BotFather.  
2️⃣ Choose a name for your bot.  
3️⃣ Choose a unique username.  
4️⃣ BotFather will give you a token.  

✅ You can now either:  
- **Forward** the BotFather message containing the token, **or**  
- **Type/paste** the token directly here.  

Then I’ll create a clone bot for you 😌"""

    CUSTOMIZEC_TXT = """<b><u>✨ CUSTOMIZE CLONE</u></b>

🖍️ Username: {username}

Modify and customize your clone bot from here."""

    ST_MSG_TXT = """<b><u>✨ START MESSAGE</u></b>

Customize the start message of your clone bot using the options below."""

    ST_TXT_TXT = """<b><u>✨ START TEXT</u></b>

Personalize the start message text of your clone bot to suit your preferences."""

    EDIT_ST_TXT = """<code>{user}</code> → mention user

Example:
Hi {user} 👋  
I am a file store bot.

📝 Now send your new start message text."""

    ST_PIC_TXT = """<b><u>✨ START PHOTO</u></b>

Include a photo to be displayed along with your start message."""

    EDIT_ST_PIC = """🖼️ Please upload the new start photo you would like to use.

ℹ️ This photo will be shown in your bot’s start message."""

    CAPTION_TXT = """<b><u>✨ CUSTOM CAPTION</u></b>

Add a custom caption to your media messages instead of using the original caption.

Available placeholders:
<code>{file_name}</code> → File name  
<code>{file_size}</code> → File size  
<code>{caption}</code> → Original caption"""

    EDIT_CAPTION_TXT = """📝 Please provide the new caption text you want to set.

ℹ️ This caption will be applied to your shareable link messages."""

    BUTTON_TXT = """<b><u>✨ CUSTOM BUTTON</u></b>

Add up to 3 custom buttons to your media messages."""

    EDIT_BUTTON_TXT = """🔘 Please provide the button name and URL you want to add.

ℹ️ The name will be shown on the button, and the URL will open when users click it."""

    CH_MSG_TXT = """<b><u>✨ CHANNEL MESSAGE</u></b>

Customize the channel message of your clone bot using the options below."""

    WORD_FILTER_TXT = """<b><u>✨ OFFENSIVE WORD FILTER</u></b>

Block or filter offensive words in forwarded or posted messages.

Current Status: {status}"""

    WF_STATUS = """🔗 Please send me the channel for Offensive Word Filter.

You can provide it in **any of these ways**:

✅ **Channel ID** (private channels):  
`-1001234567890`

✅ **Username** (public channels):  
`@YourChannel`

✅ **Forward a message** from the channel directly to me.  

This makes it easier to add channels without manually copying IDs or usernames.

⚠️ Note: Make sure I am an **admin** in that channel with all permission."""

    BAD_WORDS = [
        "madarchod", "behenchod", "chutiya", "lund", "chut", "randi", "chod", "gand", "gandi",
        "sala", "suar", "gadha", "hijra", "bhen ki lund", "maa ki chut", "chodai", "luda",
        "randi ka lund", "haramkhor", "haramzada", "chutmar", "gandmar", "chutiyapa", "lundch",
        "lundka", "randiwali", "hori", "kaminey", "kamina", "betichod", "maa chudai",
        "chut ki gand", "nangi", "nangi ladki", "nanga", "bhosdiwala", "bhosdike", "gandfat", "chutfat",
        "lundgand", "gaand", "gaandfat", "chutgand", "lundmar", "chutkala", "lundkala", "bhosdk",
        "bhenchode", "madarchode", "chutwa", "lundwa", "ludka", "lodu", "bc", "mc", "bcch",
        "bcchd", "behench", "bhosdi", "gandu", "madar", "randiya", "chutiyapa", "harami", "chodu",
        "fuck", "fucker", "bastard", "bitch", "asshole", "dickhead", "motherfucker", "sonofabitch",
        "cunt", "slut", "whore", "cock", "pussy", "tits", "boobs", "penis", "vagina", "cum",
        "ejaculate", "masturbate", "jerkoff", "gangbang", "porn", "pornhub", "xvideo", "xxx",
        "18+", "adult", "sexvideo", "pornstar", "fuckboy", "fuckgirl", "sexy", "horny", "naked",
        "nude", "stripper", "prostitute", "callgirl", "hooker", "brothel", "sexworker", "sugarbaby",
        "sugardaddy", "sexually", "boobies", "nipples", "jerking", "fucking", "fucked", "fucks",
        "ass", "anal", "blowjob", "handjob", "cumshot", "orgasm", "threesome", "69", "bdsm",
        "bondage", "fetish", "kinky", "spank", "pussylick", "dildos", "vibrator", "pornvideo",
        "sexgame", "sexchat", "sexcam", "nipple", "slutshaming", "cocktail", "hornytime",
        "idiot", "stupid", "moron", "dumb", "loser", "scumbag", "trash", "asshat", "dipshit", "jerk",
        "fool", "twat", "prick", "imbecile", "dork", "weirdo", "slob", "nerd", "loser", "simp", "sex"
    ]

    MEDIA_FILTER_TXT = """<b><u>✨ OFFENSIVE MEDIA FILTER</u></b>

Automatically block or filter offensive media in forwarded or posted messages.

Current Status: {status}"""

    RANDOM_CAPTION_TXT = """<b><u>✨ RANDOM CAPTION</u></b>

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

    HEADER_TXT = """<b><u>✨ CUSTOM HEADER</u></b>

Add a custom header that will appear at the top of every forwarded or posted message."""

    EDIT_HEADER_TXT = """📝 Please send the header text you would like to set.

ℹ️ This text will automatically appear at the **top** of every forwarded or posted message."""

    FOOTER_TXT = """<b><u>✨ CUSTOM FOOTER</u></b>

Add a custom footer that will appear at the bottom of every forwarded or posted message."""

    EDIT_FOOTER_TXT = """📝 Please send the footer text you would like to set.

ℹ️ This text will automatically appear at the **bottom** of every forwarded or posted message."""

    FSUB_TXT = """<b><u>✨ FORCE SUBSCRIBE</u></b>

Users must join your required channels before they can use the clone bot.

You can add up to **4 channels**."""

    EDIT_FSUB_TXT = """🔗 Please send me the channel for Force Subscribe.

You can provide it in **any of these ways**:

✅ **Channel ID** (private channels):  
`-1001234567890`

✅ **Username** (public channels):  
`@YourChannel`

✅ **Forward a message** from the channel directly to me.  

This makes it easier to add channels without manually copying IDs or usernames.

⚠️ Note: Make sure I am an **admin** in that channel with permission to invite users."""

    TOKEN_TXT = """<b><u>✨ ACCESS TOKEN</u></b>

Users must complete a verification link to gain special access to messages from all clone shareable links.

The access remains valid for the configured validity period.

Current Status: {status}"""

    AT_VALIDITY_TXT = """<b><u>✨ ACCESS TOKEN VALIDITY</u></b>

You can set how long the special access (via access token) will remain valid. 

Once this period ends, users will need to verify again to continue without ads."""

    AT_TUTORIAL_TXT = """<b><u>✨ ACCESS TOKEN TUTORIAL</u></b>

You can provide a tutorial link to guide users on how the access token works 
and how it removes ads when accessing clone links."""

    AUTO_POST_TXT = """<b><u>✨ AUTO POST</u></b>

You can enable automatic posting to your channel. 

When enabled, the bot will automatically send posts at the configured interval.

Current Status: {status}"""

    AP_STATUS = """🔗 Please send me the channel for Auto Post.

You can provide it in **any of these ways**:

✅ **Channel ID** (private channels):  
`-1001234567890`

✅ **Username** (public channels):  
`@YourChannel`

✅ **Forward a message** from the channel directly to me.  

This makes it easier to add channels without manually copying IDs or usernames.

⚠️ Note: Make sure I am an **admin** in that channel with all permission."""

    AP_IMG_TXT = """<b><u>✨ AUTO POST IMAGE</u></b>

Include a photo to be displayed along with your auto post."""

    EDIT_AP_IMG = """🖼️ Please upload the new auto post image you would like to use.

ℹ️ This image will be shown in your auto post."""

    AP_SLEEP_TXT = """<b><u>✨ AUTO POST SLEEP</u></b>

You can customize the waiting time (sleep) between one auto post and the next.

This controls how long the bot waits before sending another auto post to users."""

    list_image = [
        "https://i.ibb.co/6dxWG0B/IMG-20251006-143409-486.jpg",
        "https://i.ibb.co/0jcyzSQb/IMG-20251006-143418-434.jpg",
        "https://i.ibb.co/qqz8XDb/IMG-20251006-143422-863.jpg",
        "https://i.ibb.co/yFQTNHkQ/IMG-20251006-143440-653.jpg",
        "https://i.ibb.co/vvqmg1dn/IMG-20251006-143450-238.jpg",
        "https://i.ibb.co/wNHd2R6J/IMG-20251006-143503-341.jpg",
        "https://i.ibb.co/8LqgK0NB/IMG-20251006-143529-763.jpg",
        "https://i.ibb.co/0jrwzRTW/IMG-20251006-143550-133.jpg",
        "https://i.ibb.co/yndxcb8V/IMG-20251006-143619-142.jpg",
        "https://i.ibb.co/PGwzMFwc/IMG-20251006-143703-727.jpg",
        "https://i.ibb.co/TqLKLSb5/IMG-20251006-143644-776.jpg",
        "https://i.ibb.co/35SS5ww8/IMG-20251006-143647-176.jpg",
        "https://i.ibb.co/cMLbFp9/IMG-20251006-143655-195.jpg",
        "https://i.ibb.co/bjZrttyF/IMG-20251006-143709-556.jpg",
        "https://i.ibb.co/mw8W2Sf/IMG-20251006-143712-696.jpg",
        "https://i.ibb.co/WWqcmzGF/IMG-20251006-143735-441.jpg",
        "https://i.ibb.co/qM0qwchT/IMG-20251006-143725-504.jpg",
        "https://i.ibb.co/cKNSD1SK/IMG-20251006-143742-454.jpg",
        "https://i.ibb.co/wFjkXVMk/IMG-20251006-143752-407.jpg",
        "https://i.ibb.co/7tkQz1wY/IMG-20251006-143752-520.jpg",
        "https://i.ibb.co/Xx3jZQjV/IMG-20251006-143826-665.jpg",
        "https://i.ibb.co/h1cvgt0B/IMG-20251006-143810-940.jpg",
        "https://i.ibb.co/BHTq9sBx/IMG-20251006-143823-687.jpg",
        "https://i.ibb.co/LXP3RB4T/IMG-20251006-143808-418.jpg",
        "https://i.ibb.co/PzWYS6pm/IMG-20251006-143832-045.jpg",
        "https://i.ibb.co/7F1c6P9/IMG-20251006-143841-441.jpg",
        "https://i.ibb.co/fzRc4r1F/IMG-20251006-143850-543.jpg",
        "https://i.ibb.co/nNGVfN2s/IMG-20251006-143858-648.jpg",
        "https://i.ibb.co/5gsxd25r/IMG-20251006-143850-628.jpg",
        "https://i.ibb.co/zW4DcKGQ/IMG-20251006-143855-900.jpg",
        "https://i.ibb.co/SX555SBT/IMG-20251006-143905-343.jpg",
        "https://i.ibb.co/B2FhHcqq/IMG-20251006-143916-002.jpg",
        "https://i.ibb.co/svCx0mL1/IMG-20251006-143930-518.jpg",
        "https://i.ibb.co/h1mxFFgg/IMG-20251006-143933-041.jpg",
        "https://i.ibb.co/9mSdGtxT/IMG-20251006-143938-684.jpg",
        "https://i.ibb.co/nN7s5fZ8/IMG-20251006-143949-379.jpg",
        "https://i.ibb.co/67X2d9Ck/IMG-20251006-143954-801.jpg",
        "https://i.ibb.co/Y7B2C571/IMG-20251006-143956-169.jpg",
        "https://i.ibb.co/ynhMNLGs/IMG-20251006-144030-761.jpg",
        "https://i.ibb.co/ds8THM82/IMG-20251006-144051-818.jpg",
        "https://i.ibb.co/39XMw3jy/IMG-20251006-144120-788.jpg",
        "https://i.ibb.co/xqcbjZdr/IMG-20251006-144310-980.jpg",
        "https://i.ibb.co/84Rtr7vG/IMG-20251006-144249-932.jpg",
        "https://i.ibb.co/8gsCXRjc/IMG-20251006-144321-569.jpg",
        "https://i.ibb.co/XxT7NZT6/IMG-20251006-144351-578.jpg",
        "https://i.ibb.co/G3R681y0/IMG-20251006-144357-261.jpg",
        "https://i.ibb.co/pBcRY5Tc/IMG-20251006-144410-029.jpg",
        "https://i.ibb.co/cSH41Nfm/IMG-20251006-144426-295.jpg",
        "https://i.ibb.co/nNRtLhrR/IMG-20251006-144518-143.jpg",
        "https://i.ibb.co/jZ8sb5PG/IMG-20251006-144436-016.jpg",
        "https://i.ibb.co/B2xrQCN2/IMG-20251005-193611-432.jpg",
        "https://i.ibb.co/ycrjTnJK/IMG-20251005-193622-442.jpg",
        "https://i.ibb.co/gZ95R1B0/IMG-20251005-193644-917.jpg",
        "https://i.ibb.co/ynMkdwyJ/IMG-20251005-193709-579.jpg",
        "https://i.ibb.co/Z12X1jCk/IMG-20251005-193712-857.jpg",
        "https://i.ibb.co/d9yVt4B/IMG-20251005-193717-965.jpg",
        "https://i.ibb.co/99zPrqGS/IMG-20251005-193747-435.jpg",
        "https://i.ibb.co/Wp0ngq5P/IMG-20251005-193753-343.jpg",
        "https://i.ibb.co/TBgYpctL/IMG-20251005-193755-432.jpg",
        "https://i.ibb.co/1Y4L5ssk/IMG-20251005-193800-698.jpg",
        "https://i.ibb.co/GvbXK8D7/IMG-20251005-193811-575.jpg",
        "https://i.ibb.co/ycH98FZ1/IMG-20251005-193811-207.jpg",
        "https://i.ibb.co/b5CgJgP5/IMG-20251005-193825-280.jpg",
        "https://i.ibb.co/WWq31bqr/IMG-20251005-193837-790.jpg",
        "https://i.ibb.co/Fq6SQ9v3/IMG-20251005-193844-195.jpg",
        "https://i.ibb.co/V00F2bDs/IMG-20251005-193921-745.jpg",
        "https://i.ibb.co/RTx7CmZv/IMG-20251005-193949-593.jpg",
        "https://i.ibb.co/S7BK8yzN/IMG-20251005-193949-324.jpg",
        "https://i.ibb.co/TBBWzF8D/IMG-20251005-194022-795.jpg",
        "https://i.ibb.co/VY2JTPVr/IMG-20251005-194030-261.jpg",
        "https://i.ibb.co/9Hz95DXS/IMG-20251005-194030-144.jpg",
        "https://i.ibb.co/0Vy5zTr9/IMG-20251005-194126-482.jpg",
        "https://i.ibb.co/FbWSwKHr/IMG-20251005-194210-991.jpg",
        "https://i.ibb.co/NnHXT6Tt/IMG-20251005-194145-229.jpg",
        "https://i.ibb.co/7tj98m89/IMG-20251005-194215-705.jpg",
        "https://i.ibb.co/5XDB3wyt/IMG-20251005-194224-488.jpg",
        "https://i.ibb.co/1f12DvkZ/IMG-20251005-194215-505.jpg",
        "https://i.ibb.co/TxbfJn0K/IMG-20251005-192236-290.jpg",
        "https://i.ibb.co/S423GwrM/IMG-20251005-192317-864.jpg",
        "https://i.ibb.co/xSQz7zcD/IMG-20251005-192323-599.jpg",
        "https://i.ibb.co/hR5RwSrx/IMG-20251005-192354-059.jpg",
        "https://i.ibb.co/p6cDPmqb/IMG-20251005-192356-863.jpg",
        "https://i.ibb.co/HTk9BysJ/IMG-20251005-192432-194.jpg",
        "https://i.ibb.co/Xkb1pCC0/IMG-20251005-192435-493.jpg",
        "https://i.ibb.co/Rkp6hDVt/IMG-20251005-192441-629.jpg",
        "https://i.ibb.co/3mMF40gw/IMG-20251005-192518-126.jpg",
        "https://i.ibb.co/vxvP8ccc/IMG-20251005-192614-851.jpg",
        "https://i.ibb.co/VY58FThZ/IMG-20251005-192625-476.jpg",
        "https://i.ibb.co/qL3Lm5Zn/IMG-20251005-192659-833.jpg",
        "https://i.ibb.co/dJk6LY5g/IMG-20251005-192705-949.jpg",
        "https://i.ibb.co/7x5nfQFv/IMG-20251005-192736-351.jpg",
        "https://i.ibb.co/TB6bTMJS/IMG-20251005-192743-245.jpg",
        "https://i.ibb.co/KxvZdG4w/IMG-20251005-192833-222.jpg",
        "https://i.ibb.co/cKjNPX5K/IMG-20251005-192839-664.jpg",
        "https://i.ibb.co/fV35nRb4/IMG-20251005-192842-606.jpg",
        "https://i.ibb.co/zVpRJ9Xj/IMG-20251005-193043-352.jpg",
        "https://i.ibb.co/ksbmzG0F/IMG-20251005-193043-275.jpg",
        "https://i.ibb.co/rfqXD43M/IMG-20251005-193125-639.jpg",
        "https://i.ibb.co/j9dn6jhG/IMG-20251005-193154-706.jpg",
        "https://i.ibb.co/WN74dBpG/IMG-20251005-193208-680.jpg",
        "https://i.ibb.co/Lzs090Gq/IMG-20251005-193258-078.jpg",
        "https://i.ibb.co/8Ds0F6H9/IMG-20251005-193319-299.jpg",
        "https://i.ibb.co/prnZ47GL/IMG-20251005-193331-778.jpg",
        "https://i.ibb.co/PZ0GJSWV/IMG-20251004-204847-256.jpg",
        "https://i.ibb.co/x8cJCNSY/IMG-20251004-204828-994.jpg",
        "https://i.ibb.co/chPyFKdz/IMG-20251005-173538-983.jpg",
        "https://i.ibb.co/d4VnSDXk/IMG-20251004-203733-889.jpg",
        "https://i.ibb.co/PGtk3WKM/IMG-20251004-203735-919.jpg",
        "https://i.ibb.co/CpQcqdvv/IMG-20251004-203738-625.jpg",
        "https://i.ibb.co/7NYGL03Y/IMG-20251004-203739-992.jpg",
        "https://i.ibb.co/RG0NkLdp/IMG-20251004-203742-409.jpg",
        "https://i.ibb.co/mCD8hdGx/IMG-20251004-203752-737.jpg",
        "https://i.ibb.co/BKyMQpN7/IMG-20251004-203806-119.jpg",
        "https://i.ibb.co/9H5GLZxm/IMG-20251004-203807-963.jpg",
        "https://i.ibb.co/MDmX31Rn/IMG-20251004-203809-616.jpg",
        "https://i.ibb.co/35ZzWYr3/IMG-20251004-203811-016.jpg",
        "https://i.ibb.co/FbmV8h4C/IMG-20251004-203812-765.jpg",
        "https://i.ibb.co/4w1R1d59/IMG-20251004-203814-626.jpg",
        "https://i.ibb.co/chmF0cxq/IMG-20251004-203829-160.jpg",
        "https://i.ibb.co/BVtwZ5M4/IMG-20251005-173317-169.jpg",
        "https://i.ibb.co/TxkLBfWB/IMG-20251005-173321-117.jpg",
        "https://i.ibb.co/9mbM5C3Y/IMG-20251005-173511-702.jpg",
        "https://i.ibb.co/9BJb3hw/IMG-20251005-173516-308.jpg",
        "https://i.ibb.co/G4bQdb3p/IMG-20251005-173523-879.jpg",
        "https://i.ibb.co/Vcm9t441/IMG-20251005-173525-667.jpg",
        "https://i.ibb.co/qLSKVBZc/IMG-20251005-173532-417.jpg",
        "https://i.ibb.co/6zVyvgH/IMG-20251005-173534-838.jpg",
        "https://i.ibb.co/MyFkWL1P/IMG-20251005-173541-732.jpg",
        "https://i.ibb.co/zhLZkLHj/IMG-20251005-173543-751.jpg",
        "https://i.ibb.co/XZp1SHYp/IMG-20251005-173552-562.jpg",
        "https://i.ibb.co/SX0HHGvN/IMG-20251005-173601-335.jpg",
        "https://i.ibb.co/4Z38xLSV/IMG-20251005-173617-483.jpg",
        "https://i.ibb.co/8DdvcS1X/IMG-20251005-173707-817.jpg",
        "https://i.ibb.co/Kz7hg2gn/IMG-20251005-173709-780.jpg",
        "https://i.ibb.co/FqNwxkzV/IMG-20251005-173711-833.jpg",
        "https://i.ibb.co/zWGXGDnK/IMG-20251005-173712-756.jpg",
        "https://i.ibb.co/XrR8j8Ld/IMG-20251005-173714-289.jpg",
        "https://i.ibb.co/Kcc19P8b/IMG-20251005-173714-897.jpg",
        "https://i.ibb.co/p6xqwW6H/IMG-20251005-173716-917.jpg",
        "https://i.ibb.co/ZbFxq5v/IMG-20251005-173807-437.jpg",
        "https://i.ibb.co/N6z35t9M/IMG-20251005-173808-600.jpg",
        "https://i.ibb.co/kVMpZ8jQ/IMG-20251005-173810-415.jpg",
        "https://i.ibb.co/whbL6qNb/IMG-20251005-173811-422.jpg",
        "https://i.ibb.co/27WTdxZb/IMG-20251005-173812-825.jpg",
        "https://i.ibb.co/GQZ2vhSw/IMG-20251005-173828-935.jpg",
        "https://i.ibb.co/KQcL7n3/IMG-20251005-173831-261.jpg",
        "https://i.ibb.co/3YMnVGFR/IMG-20251005-173850-285.jpg",
        "https://i.ibb.co/wFJZ9hrN/IMG-20251005-173842-889.jpg",
        "https://i.ibb.co/whdkvSnm/IMG-20251005-173846-962.jpg",
        "https://i.ibb.co/TqrJKzvX/IMG-20251005-173851-022.jpg",
        "https://i.ibb.co/Y9LQ7YY/IMG-20251005-173852-820.jpg",
        "https://i.ibb.co/HTsxRSnT/IMG-20251005-173853-673.jpg",
        "https://i.ibb.co/q351g16p/IMG-20251005-173854-773.jpg",
        "https://i.ibb.co/F4Z5p4NK/IMG-20251005-173857-830.jpg",
        "https://i.ibb.co/jk3WxVn1/IMG-20251005-173900-634.jpg",
        "https://i.ibb.co/GQvkRtj8/IMG-20251005-173859-290.jpg",
        "https://i.ibb.co/7Jsh9xLm/IMG-20251004-203815-543.jpg",
        "https://i.ibb.co/ynx0H6Mt/IMG-20251004-203817-878.jpg",
        "https://i.ibb.co/Mktp8wzY/IMG-20251004-203819-497.jpg",
        "https://i.ibb.co/WWYNycMq/IMG-20251004-203821-384.jpg",
        "https://i.ibb.co/t6SBYFD/IMG-20251004-203823-445.jpg",
        "https://i.ibb.co/73bJccx/IMG-20251004-203825-140.jpg",
        "https://i.ibb.co/9mFmVcKX/IMG-20251004-203827-202.jpg",
        "https://i.ibb.co/bgSd4Q0w/IMG-20251004-203830-892.jpg",
        "https://i.ibb.co/yBNhCShB/IMG-20251004-203832-704.jpg",
        "https://i.ibb.co/GfGWS5jd/IMG-20251004-203835-039.jpg",
        "https://i.ibb.co/fV5HKnWy/IMG-20251004-203836-534.jpg",
        "https://i.ibb.co/tTNk7S0X/IMG-20251004-203838-470.jpg",
        "https://i.ibb.co/Rp3Zy7mq/IMG-20251004-203840-118.jpg",
        "https://i.ibb.co/DHGc5Dz0/IMG-20251004-203842-547.jpg",
        "https://i.ibb.co/F2pGQC6/IMG-20251004-203845-009.jpg",
        "https://i.ibb.co/217wFWpg/IMG-20251004-203848-961.jpg",
        "https://i.ibb.co/Kxcg6bsL/IMG-20251004-203846-750.jpg",
        "https://i.ibb.co/1YCbk8MH/IMG-20251004-203851-276.jpg",
        "https://i.ibb.co/W4d4qsN8/IMG-20251004-203854-444.jpg",
        "https://i.ibb.co/TDkLZmkC/IMG-20251004-203856-164.jpg",
        "https://i.ibb.co/354sYw89/IMG-20251004-203905-225.jpg",
        "https://i.ibb.co/xqQWsfzs/IMG-20251004-203859-007.jpg",
        "https://i.ibb.co/d4JH1CCD/IMG-20251004-203901-445.jpg",
        "https://i.ibb.co/5gFCJZCd/IMG-20251004-203903-736.jpg",
        "https://i.ibb.co/fdyNTrcj/IMG-20251004-203907-934.jpg",
        "https://i.ibb.co/99fd1J99/IMG-20251004-203909-826.jpg",
        "https://i.ibb.co/0jn5wtcq/IMG-20251004-203913-054.jpg",
        "https://i.ibb.co/YTZhfdLD/IMG-20251004-203915-408.jpg",
        "https://i.ibb.co/KjFyh87H/IMG-20251004-203928-542.jpg",
        "https://i.ibb.co/99Zn9Pzs/IMG-20251004-203930-104.jpg",
        "https://i.ibb.co/4wp9GFH1/IMG-20251004-203932-532.jpg",
        "https://i.ibb.co/GQ2q7kVq/IMG-20251004-203933-313.jpg",
        "https://i.ibb.co/qY5J9R1S/IMG-20251004-203935-785.jpg",
        "https://i.ibb.co/G4QKv9Vb/IMG-20251004-203937-218.jpg",
        "https://i.ibb.co/xSktNqbj/IMG-20251004-203939-172.jpg",
        "https://i.ibb.co/cXXyn9PJ/IMG-20251004-194047-512.jpg",
        "https://i.ibb.co/CpxzcrTn/IMG-20251003-192959-414.jpg",
        "https://i.ibb.co/G3NdBhdV/IMG-20251003-192950-476.jpg",
        "https://i.ibb.co/zhfXLJMR/IMG-20251003-192956-626.jpg",
        "https://i.ibb.co/x86zWm0L/IMG-20251004-194312-497.jpg",
        "https://i.ibb.co/fYXDQPXP/IMG-20251004-194244-842.jpg",
        "https://i.ibb.co/PZRzN6SV/IMG-20251004-194038-800.jpg",
        "https://i.ibb.co/Dgkf8RHh/IMG-20251004-194044-654.jpg",
        "https://i.ibb.co/WWm2PdG7/IMG-20251004-194110-177.jpg",
        "https://i.ibb.co/Kjz9Kvhn/IMG-20251004-194052-929.jpg",
        "https://i.ibb.co/k2RfX3ch/IMG-20251004-194057-821.jpg",
        "https://i.ibb.co/PvmHPZfh/IMG-20251004-194105-538.jpg",
        "https://i.ibb.co/KjHrwG6F/IMG-20251004-194224-636.jpg",
        "https://i.ibb.co/Rk0LcMqh/IMG-20251004-194118-602.jpg",
        "https://i.ibb.co/kn6R51k/IMG-20251004-194219-589.jpg",
        "https://i.ibb.co/GQDDJ8yH/IMG-20251004-194228-246.jpg",
        "https://i.ibb.co/tjCqqyn/IMG-20251004-194232-039.jpg",
        "https://i.ibb.co/SwXxQ0H5/IMG-20251004-194237-000.jpg",
        "https://i.ibb.co/TxWFMDsP/IMG-20251004-194248-115.jpg",
        "https://i.ibb.co/mrZ71KVJ/IMG-20251004-194240-108.jpg",
        "https://i.ibb.co/B2Qrrn1c/IMG-20251004-194308-325.jpg",
        "https://i.ibb.co/nMzGBr4Y/IMG-20251004-194259-831.jpg",
        "https://i.ibb.co/N2wrxjGw/IMG-20251004-194303-811.jpg",
        "https://i.ibb.co/cKfvLng3/IMG-20251004-194315-324.jpg",
        "https://i.ibb.co/Y4kqwNVY/IMG-20251004-194332-839.jpg",
        "https://i.ibb.co/mryDQrnk/IMG-20251004-194319-782.jpg",
        "https://i.ibb.co/JL1FqW4/IMG-20251004-194324-388.jpg",
        "https://i.ibb.co/zWPq5t6t/IMG-20251004-194328-788.jpg",
        "https://i.ibb.co/zVkTQY21/IMG-20251004-194341-824.jpg",
        "https://i.ibb.co/rGVfhjxb/IMG-20251004-194337-011.jpg",
        "https://i.ibb.co/fd679B29/IMG-20251004-194345-191.jpg",
        "https://i.ibb.co/tPNhNhSD/IMG-20251004-194350-079.jpg",
        "https://i.ibb.co/vxNZ3w80/IMG-20251004-194353-901.jpg",
        "https://i.ibb.co/rGgcQkyP/IMG-20251004-194357-640.jpg",
        "https://i.ibb.co/m57zV6ff/IMG-20251004-194402-132.jpg",
        "https://i.ibb.co/B2yG2LsJ/IMG-20251004-194405-902.jpg",
        "https://i.ibb.co/ycYC1sZS/IMG-20251004-194554-708.jpg",
        "https://i.ibb.co/gbrzgjjN/IMG-20251004-194414-014.jpg",
        "https://i.ibb.co/GQmbpw9X/IMG-20251004-194410-150.jpg",
        "https://i.ibb.co/Vp0GdvZ0/IMG-20251004-194558-484.jpg",
        "https://i.ibb.co/JWBdZWSJ/IMG-20251004-194602-641.jpg",
        "https://i.ibb.co/nMDc67XW/IMG-20251004-194606-191.jpg",
        "https://i.ibb.co/j9ZNDPk0/IMG-20251004-194612-952.jpg",
        "https://i.ibb.co/spSWT2c8/IMG-20251004-194629-676.jpg",
        "https://i.ibb.co/tP8zD9k6/IMG-20251004-194621-616.jpg",
        "https://i.ibb.co/1Fk3ppK/IMG-20251004-194626-212.jpg",
        "https://i.ibb.co/R4BGXykv/IMG-20251004-194647-268.jpg",
        "https://i.ibb.co/MyCg13CZ/IMG-20251004-194657-670.jpg",
        "https://i.ibb.co/z131FcJ/IMG-20251004-194704-646.jpg",
        "https://i.ibb.co/vCbgrTT1/IMG-20251004-194701-359.jpg",
        "https://i.ibb.co/gFv0Nm8M/IMG-20250904-163513-052.jpg",
    ]

    PREMIUM_TXT = """<b><u>✨ PREMIUM USERS</u></b>

Premium users can access all your clone shareable links without restrictions."""

    EDIT_PU_QR = """🖼️ Please upload the new qr you would like to use.

ℹ️ This image will be shown in your buy premium."""

    DELETE_TXT = """<b><u>✨ AUTO DELETE</u></b>

You can enable or disable automatic message deletion.

Current Status: {status}"""

    AD_TIME_TXT = """<b><u>✨ AUTO DELETE TIME</u></b>

Set how long messages will remain before being automatically deleted."""

    AD_MSG_TXT = """<b><u>✨ AUTO DELETE MESSAGE</u></b>

Customize the warning message shown to users before their messages are auto-deleted."""

    AD_TXT = """<b><u>⚠️ IMPORTANT</u></b>

All messages will be deleted after {time} {unit}.  

Please save or forward them to your personal saved messages to avoid losing them!"""

    FORWARD_TXT = """<b><u>✨ FORWARD PROTECTION</u></b>

Restrict users from forwarding messages received through clone shareable links.

Current Status: {status}"""

    MODERATOR_TXT = """<b><u>✨ MODERATOR</u></b>

Moderators can manage all clone features and have special access permissions."""
