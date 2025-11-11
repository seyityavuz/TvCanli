# TvCanli (Streamlink sürümü)

CNNTurk YouTube canlı linkini `streamlink` ile çözüp tek bir `playlist.m3u8` dosyası üretir. GitHub Actions ile her 6 saatte otomatik yenilenir.

## Kurulum
- `py -m pip install -r requirements.txt`

## Tek seferlik üretim
### Video URL ile
```
py convert_to_m3u8.py --name CNNTurk --url https://youtu.be/Wq6Q7Z7wfpQ --output playlist.m3u8
```

### Kanal canlı sayfası ile (otomatik canlı videoya yönlenir)
```
py convert_to_m3u8.py --name CNNTurk --channel @cnnturk --output playlist.m3u8
```

## Otomatik Yenileme
- `.github/workflows/refresh.yml` her `6` saatte bir çalışır ve `playlist.m3u8` dosyasını güncelleyip push eder.

Workflow kanal handle’ını (`@cnnturk`) kullanır, canlı yayına yönlenerek güncel HLS linkini üretir.

## Notlar
- YouTube canlı akışlarının HLS (`.m3u8`) URL’leri süreli olabilir; workflow bu linki periyodik olarak günceller.
- Streamlink bazı bölgelerde ek yapılandırma gerektirebilir.

### Sorun Giderme
- "akış bulunamadı" hatası alırsanız:
  - O anda kanalda gerçekten canlı yayın olduğundan emin olun.
  - `py -m pip install --upgrade streamlink` ile Streamlink’i güncelleyin.
  - Komutu kanal canlı URL’siyle deneyin: `--channel https://www.youtube.com/@cnnturk/live`.
  - Gelişmiş günlük için Streamlink CLI: `streamlink --loglevel debug https://www.youtube.com/@cnnturk/live best --stream-url`.
  - Bölgesel kısıtlama varsa, tarayıcı çerezleriyle denemek gerekebilir.