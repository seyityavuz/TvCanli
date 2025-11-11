import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional

import requests
from yt_dlp import YoutubeDL

BASE_DIR = Path(__file__).resolve().parent
CHANNELS_FILE = BASE_DIR / "channels.json"
OUT_DIR = BASE_DIR / "m3u8"
FINAL_M3U = BASE_DIR / "playlist.m3u"


def load_channels() -> List[Dict[str, str]]:
    if not CHANNELS_FILE.exists():
        return []
    data = json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    return data.get("channels", [])


def slugify(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[<>:\"/\\|?*\n\r\t]+", "-", name)
    name = re.sub(r"\s+", "_", name)
    return name or "channel"


def is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def extract_m3u8_from_youtube(url: str) -> Optional[str]:
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


def download_text(url: str, timeout: int = 12) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
        print(f"HTTP {resp.status_code}: {url}")
    except Exception as e:
        print(f"İndirme hatası: {e} -> {url}")
    return None


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_wrapper_m3u8(name: str, source_url: str, out_path: Path) -> None:
    lines = ["#EXTM3U", f"#EXTINF:-1,{name}", source_url]
    write_text_file(out_path, "\n".join(lines) + "\n")


def build_final_m3u(m3u8_files: List[Path], output_path: Path) -> None:
    lines = ["#EXTM3U"]
    for fp in m3u8_files:
        display_name = fp.stem
        uri = fp.resolve().as_uri()
        lines.append(f"#EXTINF:-1,{display_name}")
        lines.append(uri)
    write_text_file(output_path, "\n".join(lines) + "\n")


def process_once() -> None:
    channels = load_channels()
    if not channels:
        print("channels.json boş. Lütfen kanal {name,url} ekleyin.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    created_files: List[Path] = []
    for ch in channels:
        name = (ch.get("name") or "").strip()
        url = (ch.get("url") or "").strip()
        if not name or not url:
            print(f"Atlandı: Geçersiz kanal girdisi: {ch}")
            continue

        safe_name = slugify(name)
        out_path = OUT_DIR / f"{safe_name}.m3u8"

        print(f"[{name}] işleniyor...")

        m3u8_url: Optional[str] = None
        m3u8_text: Optional[str] = None

        if is_youtube(url):
            m3u8_url = extract_m3u8_from_youtube(url)
            if m3u8_url:
                print(f"[{name}] m3u8 bulundu: {m3u8_url}")
                m3u8_text = download_text(m3u8_url)
                if m3u8_text:
                    write_text_file(out_path, m3u8_text)
                    print(f"[{name}] m3u8 kaydedildi: {out_path}")
                    created_files.append(out_path)
                    continue
                else:
                    print(f"[{name}] m3u8 indirilemedi, wrapper yazılıyor.")
            else:
                print(f"[{name}] YouTube için m3u8 çıkarılamadı, wrapper yazılıyor.")
        else:
            if url.endswith(".m3u8"):
                m3u8_text = download_text(url)
                if m3u8_text:
                    write_text_file(out_path, m3u8_text)
                    print(f"[{name}] m3u8 kaydedildi: {out_path}")
                    created_files.append(out_path)
                    continue
                else:
                    print(f"[{name}] m3u8 indirilemedi, wrapper yazılıyor.")
            else:
                print(f"[{name}] m3u8 olmayan kaynak, wrapper yazılıyor.")

        write_wrapper_m3u8(name, url, out_path)
        print(f"[{name}] wrapper yazıldı: {out_path}")
        created_files.append(out_path)

    if not created_files:
        print("Hiç m3u8 dosyası oluşmadı.")
        return

    build_final_m3u(created_files, FINAL_M3U)
    print(f"Tek M3U üretildi: {FINAL_M3U}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Yayınları yerel m3u8 ve tek M3U playlist olarak üretir.")
    parser.add_argument("--watch", action="store_true", help="Sürekli çalış, belirtilen aralıkta yenile.")
    parser.add_argument("--interval-hours", type=float, default=6.0, help="Yenileme aralığı (saat). Varsayılan: 6")
    args = parser.parse_args()

    if not args.watch:
        process_once()
        return

    interval_sec = max(0.1, args.interval_hours * 3600.0)
    print(f"Sürekli modda çalışıyor. Yenileme her {args.interval_hours} saat.")
    try:
        while True:
            print("=== Yenileme başlıyor ===")
            process_once()
            print("=== Yenileme bitti ===")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("Durduruldu (Ctrl+C). Çıkılıyor...")


if __name__ == "__main__":
    main()