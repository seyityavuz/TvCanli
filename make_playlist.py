import json
import re
from pathlib import Path
from typing import List, Dict, Optional

from yt_dlp import YoutubeDL

BASE_DIR = Path(__file__).resolve().parent
CHANNELS_FILE = BASE_DIR / "channels.json"
PLAYLIST_M3U = BASE_DIR / "playlist.m3u"
PLAYLIST_M3U8 = BASE_DIR / "playlist.m3u8"


def load_channels() -> List[Dict[str, str]]:
    if not CHANNELS_FILE.exists():
        return []
    data = json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    return data.get("channels", [])


def is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def extract_m3u8(url: str) -> Optional[str]:
    """YouTube veya diğer kaynaklardan m3u8 URL’si çıkarmaya çalışır."""
    if is_youtube(url):
        opts = {
            "skip_download": True,
            "quiet": True,
            "nocheckcertificate": True,
            "noprogress": True,
        }
        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if not info:
                return None

            direct_url = info.get("url")
            direct_proto = info.get("protocol")
            if direct_url and (direct_proto == "m3u8" or str(direct_url).endswith(".m3u8")):
                return direct_url

            for f in info.get("formats", []):
                f_url = f.get("url")
                f_proto = f.get("protocol")
                if f_url and (f_proto == "m3u8" or str(f_url).endswith(".m3u8")):
                    return f_url
        except Exception as e:
            print(f"YT-DLP hata: {e}")
        return None
    else:
        # Doğrudan m3u8 ise kullan
        if url.endswith(".m3u8"):
            return url
        return None


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_playlists() -> None:
    channels = load_channels()
    if not channels:
        print("channels.json boş. Lütfen kanal {name,url} ekleyin.")
        return

    lines: List[str] = ["#EXTM3U"]
    for ch in channels:
        name = (ch.get("name") or "").strip()
        url = (ch.get("url") or "").strip()
        if not name or not url:
            print(f"Atlandı: Geçersiz kanal girdisi: {ch}")
            continue

        print(f"[{name}] m3u8 çıkarılıyor...")
        m3u8_url = extract_m3u8(url) or url
        lines.append(f"#EXTINF:-1,{name}")
        lines.append(m3u8_url)

    # M3U yaz
    write_text_file(PLAYLIST_M3U, "\n".join(lines) + "\n")
    print(f"M3U üretildi: {PLAYLIST_M3U}")

    # M3U8 (UTF-8) olarak aynı içeriği yaz
    write_text_file(PLAYLIST_M3U8, "\n".join(lines) + "\n")
    print(f"M3U8 üretildi: {PLAYLIST_M3U8}")


if __name__ == "__main__":
    generate_playlists()