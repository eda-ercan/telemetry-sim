"""Uçtan uca simülasyon: verici -> bozucu kanal -> yer istasyonu -> CSV + grafik."""
import argparse
import csv
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from telemetry.channel import Channel
from telemetry.flight_sim import flight_duration, read_sensors
from telemetry.ground_station import GroundStation
from telemetry.packet import build_packet

RATE_HZ = 10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loss", type=float, default=0.10, help="paket kayıp oranı")
    ap.add_argument("--corrupt", type=float, default=0.05, help="bozulma oranı")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    rng = random.Random(a.seed)
    channel = Channel(a.loss, a.corrupt, a.seed)
    station = GroundStation()
    out = Path("out"); out.mkdir(exist_ok=True)

    sent = 0
    n = int(flight_duration() * RATE_HZ)
    for i in range(n):
        t = i / RATE_HZ
        alt, pres, temp, batt = read_sensors(t, rng)
        raw = build_packet(i, int(t * 1000), alt, pres, temp, batt)   # VERİCİ
        sent += 1
        rx = channel.transmit(raw)                                    # RADYO
        if rx is not None:
            station.process(rx)                                       # YER İSTASYONU

    rows = station.rows
    fields = ["seq", "time_ms", "altitude", "pressure", "temperature", "battery"]
    with open(out / "telemetry.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    t_s = [r["time_ms"] / 1000 for r in rows]
    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(8, 9))
    for axis, key, label in zip(ax, ["altitude", "pressure", "temperature", "battery"],
                                ["İrtifa (m)", "Basınç (hPa)", "Sıcaklık (°C)", "Pil (V)"]):
        axis.plot(t_s, [r[key] for r in rows], ".", markersize=2)
        axis.set_ylabel(label); axis.grid(True)
    ax[-1].set_xlabel("Zaman (s)")
    fig.suptitle("Simüle edilmiş uçuş telemetrisi")
    fig.savefig(out / "flight.png", dpi=120)

    gercek = 100 * (sent - station.received) / sent
    print(f"Gönderilen        : {sent}")
    print(f"Doğru alınan      : {station.received}")
    print(f"CRC ile atılan    : {station.rejected}")
    print(f"Sayaç boşluğu (kayıp + CRC ile atılan): {station.missing}")
    print(f"Gerçek başarısız  : {sent - station.received}  (%{gercek:.1f})   <- simülasyon biliyor")
    print(f"İstasyon tahmini  : %{station.loss_percent:.1f}   <- sadece sayaçlara bakarak")
    print(f"Maks. irtifa (alınan veride): {max(r['altitude'] for r in rows):.0f} m")
    print(f"Pil voltajı (ilk -> son alınan): {rows[0]['battery']:.2f} V -> {rows[-1]['battery']:.2f} V")


if __name__ == "__main__":
    main()
