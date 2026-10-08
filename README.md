# Telemetri Simülasyonu (donanımsız)

Roketten yer istasyonuna giden telemetri zincirinin yazılım tarafını simüle eder:

    uçuş modeli -> paket oluştur (struct + CRC16) -> bozucu kanal -> ayrıştır + CRC doğrula -> CSV + grafik

**Durum:** Yalnızca simülasyon. Gerçek radyo (LoRa), ESP32 ve sensör testi yok.

## Çalıştırma

    python -m unittest discover -v     # testler
    python run_sim.py                  # simülasyon (varsayılan %10 kayıp, %5 bozulma)
    python run_sim.py --loss 0.3       # kötü kanal

Gereksinim: Python 3.9+, `matplotlib`. Çıktılar `out/` klasöründe.

## Paket formatı (22 byte, little-endian)

| Byte | Alan     | Tip     | Açıklama                         |
|------|----------|---------|----------------------------------|
| 0-1  | header   | uint16  | 0xAA55, paket başlangıcı         |
| 2-3  | seq      | uint16  | sayaç, kayıp tespiti             |
| 4-7  | time_ms  | uint32  | ms cinsinden zaman               |
| 8-11 | altitude | float32 | m                                |
| 12-15| pressure | float32 | hPa                              |
| 16-19| temp     | float32 | °C                               |
| 20-21| crc16    | uint16  | CRC-16/CCITT-FALSE (ilk 20 byte) |

## Bilinen eksikler / sonraki adımlar
- ESP32 + C/C++ firmware (aynı paket yapısı `struct` + `__attribute__((packed))`)
- Gerçek LoRa testi (RSSI, SNR, menzil)
- GPS, SD kart kaydı, FreeRTOS görevleri
- Seri porttan (pyserial) canlı veri okuma
