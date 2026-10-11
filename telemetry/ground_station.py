"""Yer istasyonu: gelen ham paketleri işler, atılanları ve eksikleri sayar."""
from telemetry.packet import PacketError, parse_packet


class GroundStation:
    def __init__(self):
        self.rows = []           # doğru alınan paketler
        self.received = 0        # doğru alınan paket sayısı
        self.rejected = 0        # CRC/uzunluk/header hatasıyla atılan paket sayısı
        self.out_of_order = 0    # tekrar eden ya da geriden gelen paket sayısı
        self.missing = 0         # sayaç boşluklarından bulunan eksik paket sayısı
        self._prev_seq = None

    def process(self, raw: bytes):
        """Bir ham paketi işler. Geçerliyse sözlüğü, değilse None döner."""
        try:
            p = parse_packet(raw)
        except PacketError:
            self.rejected += 1
            return None

        if self._prev_seq is not None:
            delta = (p["seq"] - self._prev_seq) & 0xFFFF   # 65535'ten 0'a dönüşü de kapsar
            if delta == 0 or delta >= 0x8000:              # tekrar ya da geriden gelen paket
                self.out_of_order += 1
                return None
            self.missing += delta - 1                      # atlanan numaralar = eksik paket

        self._prev_seq = p["seq"]
        self.received += 1
        self.rows.append(p)
        return p

    @property
    def expected(self) -> int:
        """İlk ve son alınan paket arasında gönderilmiş olması gereken paket sayısı."""
        return self.received + self.missing

    @property
    def loss_percent(self) -> float:
        """Yer istasyonunun sayaçlardan tahmin ettiği kayıp yüzdesi."""
        return 100 * self.missing / self.expected if self.expected else 0.0
