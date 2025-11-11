import argparse
from pathlib import Path

from streamlink import Streamlink


def resolve_live_watch_url(channel_ref: str) -> str:
    """@handle veya kanal URL’sinden YouTube canlı sayfa URL’sini üretir.
    Streamlink `.../live` sayfasını doğrudan çözer; canlı yoksa stream listesi boş döner.
    """
    url = channel_ref.strip()
    if url.startswith("@"):
        return f"https://www.youtube.com/{url}/live"
    if "youtube.com" in url:
        base = url.rstrip("/")
        if not base.endswith("live"):
            base = base + "/live"
        return base
    # Varsayılan olarak handle gibi ele al
    return f"https://www.youtube.com/@{url}/live"


def resolve_hls_url(source_url: str) -> str | None:
    session = Streamlink()
    streams = session.streams(source_url)
    if not streams:
        return None

    stream = streams.get("best") or next(iter(streams.values()))

    hls_url = getattr(stream, "url", None)
    if not hls_url:
        to_url = getattr(stream, "to_url", None)
        if callable(to_url):
            hls_url = to_url()

    if not hls_url:
        return None

    return hls_url


def write_playlist(output_path: Path, channel_name: str, hls_url: str) -> None:
    content = "\n".join([
        "#EXTM3U",
        f"#EXTINF:-1,{channel_name}",
        hls_url,
        "",
    ])
    output_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="YouTube canlı yayını m3u8 playlist’e dönüştür")
    parser.add_argument("--name", required=True, help="Kanal adı (örn. CNNTurk)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Kaynak URL (örn. YouTube video/watch)")
    group.add_argument("--channel", help="Kanal handle veya URL (örn. @cnnturk veya https://youtube.com/@cnnturk)")
    parser.add_argument("--output", default="playlist.m3u8", help="Çıkış dosyası (varsayılan: playlist.m3u8)")
    parser.add_argument("--fail-on-empty", action="store_true", help="Canlı bulunamazsa hata ver (varsayılan: hata verme)")
    args = parser.parse_args()

    source = args.url
    if not source and args.channel:
        source = resolve_live_watch_url(args.channel)

    hls_url = resolve_hls_url(source)
    if not hls_url:
        if args.fail_on_empty:
            raise RuntimeError("Bu URL için akış bulunamadı")
        else:
            print("Canlı yayın bulunamadı; mevcut playlist korunuyor.")
            return
    write_playlist(Path(args.output), args.name, hls_url)
    print(f"Playlist yazıldı: {args.output}")


if __name__ == "__main__":
    main()