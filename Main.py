from TeraboxDL import TeraboxDL
import requests
import io
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import time

API_ID = 6067591
API_HASH = "94e17044c2393f43fda31d3afe77b26b"
BOT_TOKEN = "7570465536:AAEXqxZ2iIcMni5E5MpCIW_RvmJTvY2HcTI"
TERABOX_COOKIE = "lang=en; ndus=YuTgK3HteHuieoUQBhkEn7b08MXArG0Mvy1KJkf4;"  # Replace with your TeraBox cookie

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Progress Bar (optional — will skip if too fast)
async def progress_bar(current, total, message: Message, start_time):
    percent = current * 100 / total
    speed = current / (time.time() - start_time + 1)
    eta = int((total - current) / (speed + 1))
    bar = f"[{'=' * int(percent / 10)}{' ' * (10 - int(percent / 10))}]"

    try:
        await message.edit_text(
            f"📤 Uploading...\n{bar} {percent:.1f}%\n"
            f"{current // (1024*1024)}MB / {total // (1024*1024)}MB | ETA: {eta}s"
        )
    except:
        pass

@app.on_message(filters.private & filters.text)
async def handle_link(client: Client, message: Message):
    link = message.text.strip()

    # Validate link
    if "terabox" not in link:
        return

    # Delete original message after process
    user_msg = message
    process_msg = await message.reply("🔗 Processing TeraBox link...")

    try:
        terabox = TeraboxDL(TERABOX_COOKIE)
        info = terabox.get_file_info(link)

        if "error" in info:
            err = await message.reply(f"❌ Error: {info['error']}")
            await asyncio.sleep(10)
            await err.delete()
            await process_msg.delete()
            await user_msg.delete()
            return

        # Extract URL and filename
        download_url = info.get("download_url") or info.get("download_link")
        file_name = info.get("file_name") or info.get("filename") or os.path.basename(download_url.split("?")[0])

        if not download_url:
            err = await message.reply("❌ Failed to get download URL.")
            await asyncio.sleep(10)
            await err.delete()
            await process_msg.delete()
            await user_msg.delete()
            return

        downloading_msg = await message.reply(f"⬇️ Downloading `{file_name}` into memory...")

        # Download file into memory
        file_stream = io.BytesIO()
        start = time.time()
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=1048576):  # 1 MB
                if chunk:
                    file_stream.write(chunk)

        file_stream.name = file_name
        file_stream.seek(0)
        file_size = len(file_stream.getvalue())
        size_mb = file_size / (1024 * 1024)

        # Upload to Telegram with progress
        uploading_msg = await message.reply(f"📤 Uploading `{file_name}` ({size_mb:.2f} MB)...")
        start_time = time.time()
        sent = await message.reply_document(
            document=file_stream,
            file_name=file_name,
            caption=f"✅ `{file_name}` ({size_mb:.2f} MB)",
            progress=progress_bar,
            progress_args=(uploading_msg, file_size, start_time)
        )

        # Clean up all messages
        await downloading_msg.delete()
        await uploading_msg.delete()
        await process_msg.delete()
        await user_msg.delete()
        await asyncio.sleep(20)
        await sent.delete()

    except Exception as e:
        err_msg = await message.reply(f"❌ Error: {e}")
        await asyncio.sleep(10)
        await err_msg.delete()
        await process_msg.delete()
        await user_msg.delete()

app.run()
