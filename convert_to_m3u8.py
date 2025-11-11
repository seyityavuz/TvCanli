import argparse
from pathlib import Path

from streamlink import Streamlink


def resolve_hls_url(source_url: str) -> str:
    session = Streamlink()
    streams = session.streams(source_url)
    if not streams:
        raise RuntimeError("Bu URL için akış bulunamadı")

    # 'best' akışı tercih et; HLS ise .url verir
    stream = streams.get("best") or next(iter(streams.values()))

    # HLSStream tipinde ise .url mevcuttur
    hls_url = getattr(stream, "url", None)
    if not hls_url:
        # Bazı stream tiplerinde to_url() kullanılabilir
        to_url = getattr(stream, "to_url", None)
        if callable(to_url):
            hls_url = to_url()

    if not hls_url:
        raise RuntimeError("HLS (m3u8) URL’si çıkarılamadı")

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
    parser = argparse.ArgumentParser(description="YouTube URL’sini m3u8 playlist’e dönüştür")
    parser.add_argument("--name", required=True, help="Kanal adı (örn. CNNTurk)")
    parser.add_argument("--url", required=True, help="Kaynak URL (örn. YouTube canlı)")
    parser.add_argument("--output", default="playlist.m3u8", help="Çıkış dosyası (varsayılan: playlist.m3u8)")
    args = parser.parse_args()

    hls_url = resolve_hls_url(args.url)
    write_playlist(Path(args.output), args.name, hls_url)
    print(f"Playlist yazıldı: {args.output}")


if __name__ == "__main__":
    main()