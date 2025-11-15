import re
import requests
import sys
import os
import json
import traceback
from pathlib import Path

def fetch_stream_url(url, slug):
    """Embed sayfasını çekip regex ile stream URL çıkarır."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        match = re.search(r'file:\s*["\'](.*?)["\']', resp.text)
        if match:
            return match.group(1)
        else:
            print(f"[WARN] {slug} için stream bulunamadı, embed URL kullanılacak.")
            return url
    except Exception as e:
        print(f"[ERROR] {slug} için hata: {e}")
        return url

def write_m3u(stream_url, slug, folder):
    """Tek kanal için M3U8 dosyası oluşturur."""
    lines = [
        "#EXTM3U",
        f'#EXTINF:-1 tvg-id="{slug}" tvg-name="{slug}" group-title="ParsaTV", {slug}',
        stream_url
    ]
    file_path = os.path.join(folder, slug + ".m3u8")
    Path(file_path).write_text("\n".join(lines), encoding="utf-8")
    return file_path

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    print(f"Loading config from: {config_file}")

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ ERROR loading config file: {e}")
        sys.exit(1)

    root_folder = os.path.join(os.getcwd(), config["output"]["folder"])
    best_folder = os.path.join(root_folder, config["output"]["bestFolder"])
    master_folder = os.path.join(root_folder, config["output"]["masterFolder"])
    os.makedirs(best_folder, exist_ok=True)
    os.makedirs(master_folder, exist_ok=True)

    success_count, fail_count = 0, 0

    for channel in config["channels"]:
        slug = channel.get("slug", "unknown")
        url = channel.get("url", "")
        print(f"Processing {slug} -> {url}")

        try:
            stream_url = fetch_stream_url(url, slug)
            best_file = write_m3u(stream_url, slug, best_folder)
            master_file = write_m3u(stream_url, slug, master_folder)
            print(f"  ✅ {slug} yazıldı: {best_file}, {master_file}")
            success_count += 1
        except Exception:
            print(f"  ❌ ERROR processing {slug}")
            traceback.print_exc()
            fail_count += 1

    print("\n=== Summary ===")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"Total: {len(config['channels'])}")

if __name__ == "__main__":
    main()
