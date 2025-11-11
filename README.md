# TvCanli (Streamlink sürümü)

CNNTurk YouTube canlı linkini `streamlink` ile çözüp tek bir `playlist.m3u8` dosyası üretir. GitHub Actions ile her 6 saatte otomatik yenilenir.

## Kurulum
- `py -m pip install -r requirements.txt`

## Tek seferlik üretim
```
py convert_to_m3u8.py --name CNNTurk --url https://youtu.be/Wq6Q7Z7wfpQ --output playlist.m3u8
```

## Otomatik Yenileme
- `.github/workflows/refresh.yml` her `6` saatte bir çalışır ve `playlist.m3u8` dosyasını güncelleyip push eder.

## Notlar
- YouTube canlı akışlarının HLS (`.m3u8`) URL’leri süreli olabilir; workflow bu linki periyodik olarak günceller.
- Streamlink bazı bölgelerde ek yapılandırma gerektirebilir.