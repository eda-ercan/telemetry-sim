"""Telemetri paketi: oluşturma, ayrıştırma ve CRC16.

Paket yapısı (toplam 22 byte, little-endian):
  0-1   header   uint16  sabit 0xAA55 (paketin başlangıcını işaretler)
  2-3   seq      uint16  paket sayacı (kayıp tespiti için)
  4-7   time_ms  uint32  uçuş bilgisayarının açılışından beri ms
  8-11  altitude float32 metre
  12-15 pressure float32 hPa
  16-19 temp     float32 derece C
  20-21 crc16    uint16  ilk 20 byte üzerinden hesaplanır
"""
import struct

HEADER = 0xAA55
BODY_FORMAT = "<HHIfff"            # "<" = little-endian, boşluk (padding) yok
BODY_SIZE = struct.calcsize(BODY_FORMAT)   # 20
PACKET_SIZE = BODY_SIZE + 2                # 22


class PacketError(Exception):
    """Paket bozuk veya geçersiz."""


def crc16_ccitt(data: bytes, crc: int = 0xFFFF) -> int:
    """CRC-16/CCITT-FALSE (polinom 0x1021, başlangıç 0xFFFF).

    Veriyi bit bit kaydırarak bölme işlemi yapar. Tek bir bit değişse
    sonuç değişir, bu yüzden bozulmayı yakalar.
    """
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def build_packet(seq, time_ms, altitude, pressure, temperature) -> bytes:
    body = struct.pack(BODY_FORMAT, HEADER, seq & 0xFFFF, time_ms & 0xFFFFFFFF,
                       altitude, pressure, temperature)
    return body + struct.pack("<H", crc16_ccitt(body))


def parse_packet(raw: bytes) -> dict:
    if len(raw) != PACKET_SIZE:
        raise PacketError(f"Uzunluk hatalı: {len(raw)} byte (beklenen {PACKET_SIZE})")
    body = raw[:-2]
    (crc_rx,) = struct.unpack("<H", raw[-2:])
    if crc16_ccitt(body) != crc_rx:
        raise PacketError("CRC hatası")
    header, seq, time_ms, alt, pres, temp = struct.unpack(BODY_FORMAT, body)
    if header != HEADER:
        raise PacketError(f"Header hatalı: {header:#06x}")
    return {"seq": seq, "time_ms": time_ms, "altitude": alt,
            "pressure": pres, "temperature": temp}
