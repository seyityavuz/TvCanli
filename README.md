# TvCanli
# TvCanli

Canlı yayın linklerini (YouTube dahil) toplayıp yerelde `.m3u8` dosyaları üretir ve hepsini tek bir `playlist.m3u` içinde birleştirir. YouTube canlı yayınlarının gerçek `.m3u8` adresleri süreli olduğundan script 6 saatte bir yenileyebilir.

## Kurulum (GitHub’dan)
- Repo’yu klonla:
  - `git clone https://github.com/seyityavuz/TvCanli.git`
  - `cd TvCanli`
- Gerekli paketleri kur:
  - `py -m pip install -r requirements.txt`

## Hızlı Başlangıç
- Kanal örneği `channels.json` içinde hazır:
  - `CNNTurk` → `https://www.youtube.com/watch?v=Wq6Q7Z7wfpQ`
- Tek seferlik üretim:
  - `py make_playlist.py`
- 6 saatte bir otomatik yenileme:
  - `py make_playlist.py --watch --interval-hours 6`

## Yapılandırma
- Kanallar `channels.json` dosyasına eklenir:
```
{
  "channels": [
    { "name": "KanalAdi", "url": "https://..." }
  ]
}
```
- YouTube URL’leri desteklenir. Script, mümkünse gerçek `.m3u8` adresini çıkarır; çıkaramazsa orijinal URL’yi işaret eden bir “wrapper” `.m3u8` yazılır.

## Üretilen Dosyalar
- Yerel m3u8’ler: `m3u8/<KanalAdi>.m3u8`
  - Örnek: `m3u8/CNNTurk.m3u8`
- Tek playlist: `playlist.m3u`
  - Bu dosya tüm yerel `.m3u8` dosyalarına `file:///` URI ile referans verir ve VLC gibi oynatıcılarla tek seferde açılabilir.

## Notlar
- YouTube canlı `.m3u8` adresleri zamanla geçersiz olabilir; `--watch` ile otomatik yenileme önerilir.
- Çalıştırma sırasında ağ/erişim hataları olursa komut çıktısını kontrol edin; `yt-dlp` bazı bölgesel kısıtlar için ek parametreler gerektirebilir.

## Geliştirme
- Değişiklik yapıp göndermek:
  - `git add .`
  - `git commit -m "Update"`
  - `git push`