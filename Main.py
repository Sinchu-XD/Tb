from TeraboxDL import TeraboxDL
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import os

API_ID = 6067591
API_HASH = "94e17044c2393f43fda31d3afe77b26b"
BOT_TOKEN = "7570465536:AAEXqxZ2iIcMni5E5MpCIW_RvmJTvY2HcTI"  # <-- Replace with your bot token
TERABOX_COOKIE = "lang=en; ndus=YuTgK3HteHuieoUQBhkEn7b08MXArG0Mvy1KJkf4;"  # <-- Replace with your TeraBox cookie

# Setup download path
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Setup Pyrogram bot
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# /get command handler
@app.on_message(filters.command("get") & filters.private)
async def get_file(client: Client, message: Message):
    if len(message.text.split()) != 2:
        await message.reply("❌ Usage: /get <terabox_link>")
        return

    share_url = message.text.split()[1]
    if "terabox" not in share_url:
        await message.reply("❌ Invalid TeraBox link")
        return

    await message.reply("🔍 Processing link, please wait...")

    try:
        # Get download info using TeraboxDL
        terabox = TeraboxDL(TERABOX_COOKIE)
        info = terabox.get_file_info(share_url, direct_url=True)

        if "error" in info:
            await message.reply(f"❌ Error: {info['error']}")
            return

        file_url = info["download_link"]
        file_name = info["file_name"]

        # Download the file
        local_path = os.path.join(DOWNLOAD_PATH, file_name)
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        await message.reply_document(local_path, caption=f"✅ {file_name} sent")
        os.remove(local_path)

    except Exception as e:
        await message.reply(f"❌ Failed: {str(e)}")

# Start the bot
app.run()
