import json
import re
import requests
from pathlib import Path

# JSON yapılandırması (istersen ayrı bir dosyadan da okuyabilirsin)
config = {
    "name": "ParsaTV",
    "slug": "parsatv",
    "url": "https://www.parsatv.com/embed.php?name=CHANNEL_NAME",
    "method": "GET",
    "pattern": r'file:\s*["\'](.*?)["\']',
    "expire_duration": "2H",
    "mode": "variant",
    "output_filter": "token",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0 Safari/537.36"
    },
    "channels": [
        {
            "name": "Star-TV",
            "variables": [
                {"name": "CHANNEL_NAME", "value": "Star-TV"}
            ]
        }
    ]
}

def fetch_stream_url(channel):
    """Embed sayfasını çekip regex ile stream URL çıkarır."""
    # URL’deki placeholder’ı değiştir
    url = config["url"].replace("CHANNEL_NAME", channel["variables"][0]["value"])
    try:
        resp = requests.get(url, headers=config["headers"], timeout=10)
        resp.raise_for_status()
        match = re.search(config["pattern"], resp.text)
        if match:
            return match.group(1)
        else:
            print(f"[WARN] {channel['name']} için stream bulunamadı.")
            return url  # fallback: embed URL
    except Exception as e:
        print(f"[ERROR] {channel['name']} için hata: {e}")
        return url

def generate_m3u(channels, output_file="parsatv.m3u8"):
    """Kanalları M3U playlist dosyasına yazar."""
    lines = ["#EXTM3U"]
    for ch in channels:
        stream_url = fetch_stream_url(ch)
        lines.append(f'#EXTINF:-1 tvg-id="{ch["name"]}" tvg-name="{ch["name"]}" '
                     f'group-title="{config["name"]}", {ch["name"]}')
        lines.append(stream_url)
    Path(output_file).write_text("\n".join(lines), encoding="utf-8")
    print(f"[INFO] Playlist yazıldı: {output_file}")

if __name__ == "__main__":
    generate_m3u(config["channels"])
