from TeraboxDL import TeraboxDL
import time
import requests

TERABOX_COOKIE = "lang=en; ndus=YuTgK3HteHuieoUQBhkEn7b08MXArG0Mvy1KJkf4;"  # Use your cookie here
SHARE_LINK = "https://teraboxlink.com/s/1_gOh4YzXqinDw1hu8IAHVg"

def test_terabox_download():
    terabox = TeraboxDL(TERABOX_COOKIE)
    info = terabox.get_file_info(SHARE_LINK)

    if "error" in info:
        print("Error:", info["error"])
        return

    download_url = info.get("download_url") or info.get("download_link")
    if not download_url:
        print("No direct download URL found.")
        return

    print("File name:", info.get("file_name") or info.get("filename"))
    print("Download URL:", download_url)

    try:
        start = time.time()
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total_bytes = 0
            for chunk in r.iter_content(chunk_size=8192):
                total_bytes += len(chunk)
                if total_bytes > 10*1024*1024:  # Stop after 10MB to test speed
                    break
        end = time.time()
        elapsed = end - start
        speed_mbps = (total_bytes * 8) / (elapsed * 1024 * 1024)
        print(f"Downloaded {total_bytes/(1024*1024):.2f} MB in {elapsed:.2f} seconds ({speed_mbps:.2f} Mbps)")
    except Exception as e:
        print("Download failed:", e)

if __name__ == "__main__":
    test_terabox_download()
  
