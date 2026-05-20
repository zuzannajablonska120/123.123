import random
import math


# ─────────────────────────────────────── definicje zdarzeń losowych

EVENT_DUST_STORM        = "BURZA_PIASKOWA"
EVENT_SOLAR_BOOST       = "WZMOCNIENIE_SŁONECZNE"
EVENT_EQUIPMENT_FAILURE = "AWARIA_SPRZĘTU"
EVENT_GROUND_QUAKE      = "TRZĘSIENIE_GRUNTU"
EVENT_METEOR_SHOWER     = "DESZCZ_METEORYTÓW"


EVENT_WEIGHTS = {
    EVENT_DUST_STORM:        20,
    EVENT_SOLAR_BOOST:       15,
    EVENT_EQUIPMENT_FAILURE: 18,
    EVENT_GROUND_QUAKE:      12,
    EVENT_METEOR_SHOWER:     10,
    None:                    25,   # brak zdarzenia
}


class RandomEvent:
    """Opisuje jedno zdarzenie losowe i jego efekty."""

    def __init__(self, event_type: str | None):
        self.event_type = event_type

    # -------------------------------------------- zastosowanie zdarzenia

    def apply(self, rover, world) -> list[str]:
        """
        Modyfikuje stan łazika i/lub świata.
        Zwraca listę komunikatów do wyświetlenia w terminalu.
        """
        if self.event_type is None:
            return []

        msgs: list[str] = []
        msgs.append(f"  ⚡ ZDARZENIE LOSOWE: {self._label()}")

        if self.event_type == EVENT_DUST_STORM:
            shift = random.randint(-60, 60)
            old_angle = rover.angle
            rover.turn(shift)
            fuel_lost = rover.consume_fuel(12)
            msgs.append(
                f"     Silna burza piaskowa! Kąt zmieniony o {shift:+d}° "
                f"({old_angle:.0f}° → {rover.angle:.0f}°). "
                f"Paliwo: -{fuel_lost:.1f}"
            )
            rover.events_log.append(f"Krok {rover.steps}: Burza piaskowa (kąt {shift:+d}°, paliwo -{fuel_lost:.1f})")

        elif self.event_type == EVENT_SOLAR_BOOST:
            gained = rover.refuel(18)
            msgs.append(
                f"     Wyjątkowo dobre nasłonecznienie – panele ładują szybciej! "
                f"Paliwo: +{gained:.1f}"
            )
            rover.events_log.append(f"Krok {rover.steps}: Wzmocnienie słoneczne (+{gained:.1f} paliwa)")

        elif self.event_type == EVENT_EQUIPMENT_FAILURE:
            fuel_lost = rover.consume_fuel(25)
            msgs.append(
                f"     Awaria układu termalnego – zużycie energii wzrosło! "
                f"Paliwo: -{fuel_lost:.1f}"
            )
            rover.events_log.append(f"Krok {rover.steps}: Awaria sprzętu (paliwo -{fuel_lost:.1f})")

        elif self.event_type == EVENT_GROUND_QUAKE:
            dx = random.uniform(-8, 8)
            dy = random.uniform(-8, 8)
            nx = rover.x + dx
            ny = rover.y + dy
            nx, ny = world.clamp_to_bounds(nx, ny)
            rover.apply_position(nx, ny)
            fuel_lost = rover.consume_fuel(8)
            msgs.append(
                f"     Trzęsienie marsjańskiego gruntu! Przesunięcie: "
                f"({dx:+.1f}, {dy:+.1f}). Nowa poz.: ({rover.x}, {rover.y}). "
                f"Paliwo: -{fuel_lost:.1f}"
            )
            rover.events_log.append(
                f"Krok {rover.steps}: Trzęsienie gruntu (przesuniecie ({dx:+.1f},{dy:+.1f}), "
                f"paliwo -{fuel_lost:.1f})"
            )

        elif self.event_type == EVENT_METEOR_SHOWER:
            fuel_lost = rover.consume_fuel(15)
            shift = random.choice([-30, 30, -45, 45])
            rover.turn(shift)
            msgs.append(
                f"     Deszcz meteorytów – konieczny gwałtowny manewr omijający! "
                f"Kąt: {shift:+d}°. Paliwo: -{fuel_lost:.1f}"
            )
            rover.events_log.append(
                f"Krok {rover.steps}: Deszcz meteorytów (kąt {shift:+d}°, paliwo -{fuel_lost:.1f})"
            )

        return msgs

    # ----------------------------------------------------------------- repr

    def _label(self) -> str:
        labels = {
            EVENT_DUST_STORM:        "Burza Piaskowa 🌪️",
            EVENT_SOLAR_BOOST:       "Wzmocnienie Słoneczne ☀️",
            EVENT_EQUIPMENT_FAILURE: "Awaria Sprzętu 🔧",
            EVENT_GROUND_QUAKE:      "Trzęsienie Gruntu 🌍",
            EVENT_METEOR_SHOWER:     "Deszcz Meteorytów ☄️",
        }
        return labels.get(self.event_type, "Nieznane zdarzenie")

    def __bool__(self) -> bool:
        return self.event_type is not None


# ─────────────────────────────────── funkcja losująca zdarzenie

def draw_event(step: int) -> RandomEvent:
    """
    Losuje zdarzenie dla danego kroku.
    Zdarzenia losowane są z wagami; None oznacza brak zdarzenia.
    """
    population = list(EVENT_WEIGHTS.keys())
    weights    = list(EVENT_WEIGHTS.values())
    chosen = random.choices(population, weights=weights, k=1)[0]
    return RandomEvent(chosen)
