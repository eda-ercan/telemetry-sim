import struct
import unittest

from telemetry.packet import (BODY_FORMAT, PACKET_SIZE, PacketError,
                              build_packet, crc16_ccitt, parse_packet)


class PacketTests(unittest.TestCase):
    def test_crc_bilinen_deger(self):
        # CRC-16/CCITT-FALSE standart test vektörü
        self.assertEqual(crc16_ccitt(b"123456789"), 0x29B1)

    def test_paket_boyutu(self):
        raw = build_packet(1, 100, 10.0, 1000.0, 20.0, 8.25)
        self.assertEqual(len(raw), PACKET_SIZE)
        self.assertEqual(PACKET_SIZE, 26)

    def test_gidis_donus(self):
        p = parse_packet(build_packet(7, 1234, 1500.5, 840.25, 12.5, 8.25))
        self.assertEqual(p["seq"], 7)
        self.assertEqual(p["time_ms"], 1234)
        self.assertAlmostEqual(p["altitude"], 1500.5)
        self.assertAlmostEqual(p["battery"], 8.25)

    def test_tek_bit_bozulma_yakalanir(self):
        raw = build_packet(1, 100, 10.0, 1000.0, 20.0, 8.25)
        for i in range(len(raw)):
            for bit in range(8):
                bozuk = bytearray(raw)
                bozuk[i] ^= 1 << bit
                with self.assertRaises(PacketError):
                    parse_packet(bytes(bozuk))

    def test_yanlis_uzunluk(self):
        with self.assertRaises(PacketError):
            parse_packet(b"\x00" * 5)

    def test_yanlis_header_gecerli_crc_ile(self):
        # Doğru uzunlukta ve geçerli CRC'li, ama header yanlış bir paket
        body = struct.pack(BODY_FORMAT, 0x1234, 0, 0, 0.0, 0.0, 0.0, 0.0)
        raw = body + struct.pack("<H", crc16_ccitt(body))
        self.assertEqual(len(raw), PACKET_SIZE)   # uzunluk testi geçmesin diye
        with self.assertRaises(PacketError) as ctx:
            parse_packet(raw)
        self.assertIn("Header", str(ctx.exception))

    def test_sayac_tasmasi(self):
        raw = build_packet(65536 + 3, 0, 0.0, 0.0, 0.0, 0.0)
        self.assertEqual(parse_packet(raw)["seq"], 3)


if __name__ == "__main__":
    unittest.main()
