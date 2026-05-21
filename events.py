import random
import math
from i18n import get_text


# ─────────────────────────────────────── definicje zdarzeń losowych

EVENT_WIND_GUST       = "WIND_GUST"
EVENT_FALLING_ROCKS   = "FALLING_ROCKS"
EVENT_INSECT_SWARM    = "INSECT_SWARM"
EVENT_CAVE_QUAKE      = "CAVE_QUAKE"
EVENT_OTHER_BAT       = "OTHER_BAT"


EVENT_WEIGHTS = {
    EVENT_WIND_GUST:      20,
    EVENT_FALLING_ROCKS:  15,
    EVENT_INSECT_SWARM:   18,
    EVENT_CAVE_QUAKE:     12,
    EVENT_OTHER_BAT:      10,
    None:                 25,   # brak zdarzenia
}


class RandomEvent:
    """Opisuje jedno zdarzenie losowe i jego efekty."""

    def __init__(self, event_type: str | None):
        self.event_type = event_type

    # -------------------------------------------- zastosowanie zdarzenia

    def apply(self, bat, world, lang="pl") -> list[str]:
        """
        Modyfikuje stan nietoperza i/lub jaskini.
        Zwraca listę komunikatów do wyświetlenia w terminalu.
        """
        if self.event_type is None:
            return []

        msgs: list[str] = []
        msgs.append(f"  ⚡ {get_text('random_event', lang)}: {self._label(lang)}")

        if self.event_type == EVENT_WIND_GUST:
            shift = random.randint(-60, 60)
            old_angle = bat.angle
            bat.turn(shift)
            echo_lost = bat.consume_echolocation(12)
            if lang == "pl":
                msgs.append(
                    f"     Silny podmuch wiatru! Kąt zmieniony o {shift:+d}° "
                    f"({old_angle:.0f}° → {bat.angle:.0f}°). "
                    f"Echolokacja: -{echo_lost:.1f}"
                )
            else:
                msgs.append(
                    f"     Strong wind gust! Angle changed by {shift:+d}° "
                    f"({old_angle:.0f}° → {bat.angle:.0f}°). "
                    f"Echolocation: -{echo_lost:.1f}"
                )
            bat.events_log.append(f"Step {bat.steps}: Wind gust (angle {shift:+d}°, echo -{echo_lost:.1f})")

        elif self.event_type == EVENT_INSECT_SWARM:
            gained = bat.restore_echolocation(18)
            if lang == "pl":
                msgs.append(
                    f"     Trafiłeś na rój owadów – pożywne śniadanie! "
                    f"Echolokacja: +{gained:.1f}"
                )
            else:
                msgs.append(
                    f"     You found a swarm of insects – a nutritious breakfast! "
                    f"Echolocation: +{gained:.1f}"
                )
            bat.events_log.append(f"Step {bat.steps}: Insect swarm (+{gained:.1f} echo)")

        elif self.event_type == EVENT_FALLING_ROCKS:
            echo_lost = bat.consume_echolocation(25)
            if lang == "pl":
                msgs.append(
                    f"     Spadające kamienie – konieczne gwałtowne manewry! "
                    f"Echolokacja: -{echo_lost:.1f}"
                )
            else:
                msgs.append(
                    f"     Falling rocks – emergency maneuvers required! "
                    f"Echolocation: -{echo_lost:.1f}"
                )
            bat.events_log.append(f"Step {bat.steps}: Falling rocks (echo -{echo_lost:.1f})")

        elif self.event_type == EVENT_CAVE_QUAKE:
            dx = random.uniform(-8, 8)
            dy = random.uniform(-8, 8)
            nx = bat.x + dx
            ny = bat.y + dy
            nx, ny = world.clamp_to_bounds(nx, ny)
            bat.apply_position(nx, ny)
            echo_lost = bat.consume_echolocation(8)
            if lang == "pl":
                msgs.append(
                    f"     Drżenie jaskini! Przesunięcie: "
                    f"({dx:+.1f}, {dy:+.1f}). Nowa poz.: ({bat.x}, {bat.y}). "
                    f"Echolokacja: -{echo_lost:.1f}"
                )
            else:
                msgs.append(
                    f"     Cave quake! Shift: "
                    f"({dx:+.1f}, {dy:+.1f}). New pos.: ({bat.x}, {bat.y}). "
                    f"Echolocation: -{echo_lost:.1f}"
                )
            bat.events_log.append(
                f"Step {bat.steps}: Cave quake (shift ({dx:+.1f},{dy:+.1f}), "
                f"echo -{echo_lost:.1f})"
            )

        elif self.event_type == EVENT_OTHER_BAT:
            echo_lost = bat.consume_echolocation(15)
            shift = random.choice([-30, 30, -45, 45])
            bat.turn(shift)
            if lang == "pl":
                msgs.append(
                    f"     Spotkanie z innym nietoperzem – zakłócenia echolokacji i unik! "
                    f"Kąt: {shift:+d}°. Echolokacja: -{echo_lost:.1f}"
                )
            else:
                msgs.append(
                    f"     Encounter with another bat – echolocation interference and dodge! "
                    f"Angle: {shift:+d}°. Echolocation: -{echo_lost:.1f}"
                )
            bat.events_log.append(
                f"Step {bat.steps}: Other bat encounter (angle {shift:+d}°, echo -{echo_lost:.1f})"
            )

        return msgs

    # ----------------------------------------------------------------- repr

    def _label(self, lang="pl") -> str:
        labels = {
            EVENT_WIND_GUST:      get_text("wind_gust", lang) + " 💨",
            EVENT_INSECT_SWARM:   get_text("insect_swarm", lang) + " 🦟",
            EVENT_FALLING_ROCKS:  get_text("falling_rocks", lang) + " 🪨",
            EVENT_CAVE_QUAKE:     get_text("cave_quake", lang) + " 🌍",
            EVENT_OTHER_BAT:      get_text("other_bat", lang) + " 🦇",
        }
        return labels.get(self.event_type, "Unknown event")

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
