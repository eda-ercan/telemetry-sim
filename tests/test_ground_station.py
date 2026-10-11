import unittest

from telemetry.ground_station import GroundStation
from telemetry.packet import build_packet


def paket(seq):
    return build_packet(seq, seq * 100, 10.0, 1000.0, 20.0, 8.25)


def bozuk_paket(seq):
    raw = bytearray(paket(seq))
    raw[8] ^= 0x01   # irtifa baytlarından birinin tek bitini çevir
    return bytes(raw)


def isle(station, seqler):
    for s in seqler:
        station.process(paket(s))


class GroundStationTests(unittest.TestCase):
    def test_kayipsiz_akis(self):
        gs = GroundStation()
        isle(gs, [0, 1, 2, 3, 4])
        self.assertEqual(gs.received, 5)
        self.assertEqual(gs.missing, 0)

    def test_sayac_boslugu_eksik_paket_sayar(self):
        gs = GroundStation()
        isle(gs, [0, 1, 4])   # 2 ve 3 gelmedi
        self.assertEqual(gs.received, 3)
        self.assertEqual(gs.missing, 2)

    def test_bozuk_paket_atilir_ve_bosluk_olarak_gorunur(self):
        gs = GroundStation()
        gs.process(paket(0))
        self.assertIsNone(gs.process(bozuk_paket(1)))
        gs.process(paket(2))
        self.assertEqual(gs.rejected, 1)
        self.assertEqual(gs.received, 2)
        self.assertEqual(gs.missing, 1)   # atılan paket sayaçta boşluk olarak görünür

    def test_sayac_tasmasi_kayip_degil(self):
        gs = GroundStation()
        isle(gs, [65534, 65535, 0, 1])
        self.assertEqual(gs.missing, 0)
        self.assertEqual(gs.received, 4)

    def test_sayac_tasmasi_sirasinda_kayip(self):
        gs = GroundStation()
        isle(gs, [65534, 1])   # 65535 ve 0 gelmedi
        self.assertEqual(gs.missing, 2)

    def test_tekrar_eden_paket_kayip_sayilmaz(self):
        gs = GroundStation()
        isle(gs, [5, 5])
        self.assertEqual(gs.received, 1)
        self.assertEqual(gs.out_of_order, 1)
        self.assertEqual(gs.missing, 0)

    def test_geriden_gelen_paket_kayip_sayilmaz(self):
        gs = GroundStation()
        isle(gs, [5, 3])
        self.assertEqual(gs.out_of_order, 1)
        self.assertEqual(gs.missing, 0)

    def test_sondaki_kayip_gorunmez(self):
        # 3 ve 4 hiç gelmedi ama sonrasında paket olmadığı için istasyon fark edemez
        gs = GroundStation()
        isle(gs, [0, 1, 2])
        self.assertEqual(gs.missing, 0)

    def test_kayip_yuzdesi(self):
        gs = GroundStation()
        isle(gs, [0, 1, 4])   # alınan 3, eksik 2, beklenen 5
        self.assertEqual(gs.expected, 5)
        self.assertAlmostEqual(gs.loss_percent, 40.0)

    def test_bos_istasyon(self):
        gs = GroundStation()
        self.assertEqual(gs.loss_percent, 0.0)


if __name__ == "__main__":
    unittest.main()
