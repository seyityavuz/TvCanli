import re
import requests
from pathlib import Path

# Embed URL
embed_url = "https://www.parsatv.com/embed.php?name=Star-TV"

# HTTP isteği
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36"
}

resp = requests.get(embed_url, headers=headers, timeout=10)
resp.raise_for_status()

# Regex ile stream URL yakala
pattern = r'file:\s*["\'](.*?)["\']'
match = re.search(pattern, resp.text)

if match:
    stream_url = match.group(1)
else:
    stream_url = embed_url  # fallback

# M3U8 dosyası oluştur
lines = [
    "#EXTM3U",
    f'#EXTINF:-1 tvg-id="Star-TV" tvg-name="Star-TV" group-title="ParsaTV", Star-TV',
    stream_url
]

Path("Star-TV.m3u8").write_text("\n".join(lines), encoding="utf-8")
print("[INFO] Playlist yazıldı: Star-TV.m3u8")
