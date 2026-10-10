"""Basit uçuş modeli: sensörün ne okuyacağını üretir (BME280 yerine)."""
import random

APOGEE_M = 3000.0
BURN_S = 25.0
DESCENT_MS = 20.0   # paraşütle iniş hızı (m/s), basitleştirilmiş
BATTERY_START_V = 8.4   # 2 hücreli LiPo, tam dolu


def altitude_at(t: float) -> float:
    if t <= BURN_S:   # yükselirken yavaşlayarak apogee'ye çıkar
        return APOGEE_M * (1 - (1 - t / BURN_S) ** 2)
    return max(0.0, APOGEE_M - DESCENT_MS * (t - BURN_S))


def flight_duration() -> float:
    return BURN_S + APOGEE_M / DESCENT_MS


def read_sensors(t: float, rng: random.Random):
    alt = altitude_at(t) + rng.gauss(0, 1.5)             # sensör gürültüsü
    pressure = 1013.25 * (1 - alt / 44330.0) ** 5.255    # barometrik formül (hPa)
    temp = 20.0 - 0.0065 * alt + rng.gauss(0, 0.1)
    battery = BATTERY_START_V - 0.002 * t + rng.gauss(0, 0.01)   # yavaşça boşalır
    return alt, pressure, temp, battery
