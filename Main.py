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
    """
    Usage: /get <terabox_share_link>
    """
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("❌ Usage: /get <terabox_link>")
        return

    share_url = parts[1].strip()
    if "terabox" not in share_url:
        await message.reply("❌ Invalid TeraBox link")
        return

    await message.reply("🔍 Processing link, please wait...")

    try:
        # ── FETCH METADATA FROM TERABOX BACKEND ──
        terabox = TeraboxDL(TERABOX_COOKIE)
        info = terabox.get_file_info(share_url)  
        # Note: we do NOT pass direct_url=True here anymore.

        # Depending on TeraboxDL version, the returned keys could be:
        #   - 'download_url'  (or)
        #   - 'download_link'
        #   - 'file_name'     (or)
        #   - 'file_name'     (or sometimes 'filename')
        # Let’s pick whichever exists:
        if "error" in info:
            await message.reply(f"❌ Error: {info['error']}")
            return

        # Pull out the actual download URL:
        download_url = info.get("download_url") or info.get("download_link")
        if not download_url:
            await message.reply("❌ Could not find a direct download URL in the TeraboxDL response.")
            return

        # Pull out the filename:
        file_name = info.get("file_name") or info.get("filename")
        if not file_name:
            # As a fallback, derive name from URL
            file_name = os.path.basename(download_url.split("?")[0])

        # ── PERFORM THE HTTP DOWNLOAD ──
        local_path = os.path.join(DOWNLOAD_PATH, file_name)
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        # ── SEND THE FILE IN TELEGRAM ──
        await message.reply_document(local_path, caption=f"✅ Sent: {file_name}")
        os.remove(local_path)

    except Exception as e:
        # If something goes wrong (HTTP error, path error, etc.), report it:
        await message.reply(f"❌ Failed: {e}")

# ── STEP 4: RUN YOUR BOT ──
app.run()
info = terabox.get_file_info(share_url)
print(info)  # Send this to your console or logs to inspect the dictionary
