"""Sahte radyo kanalı: paket düşürür ve bit bozar (gerçek LoRa'yı taklit eder)."""
import random


class Channel:
    def __init__(self, loss_rate=0.10, corrupt_rate=0.05, seed=None):
        self.loss_rate = loss_rate
        self.corrupt_rate = corrupt_rate
        self.rng = random.Random(seed)

    def transmit(self, raw: bytes):
        """Paketi kanaldan geçirir. Kaybolduysa None döner."""
        if self.rng.random() < self.loss_rate:
            return None
        if self.rng.random() < self.corrupt_rate:
            data = bytearray(raw)
            i = self.rng.randrange(len(data))
            data[i] ^= 1 << self.rng.randrange(8)   # rastgele tek bit çevir
            return bytes(data)
        return raw
