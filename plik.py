# rover.py
import math


class Rover:
    """
    Reprezentuje łazik marsjański poruszający się po dwuwymiarowej mapie.
    Przechowuje pozycję, kąt skierowania, poziom paliwa oraz historię trasy.
    """

    def __init__(self, name: str, x: float, y: float, angle: float, fuel: float):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle) % 360  # kąt w stopniach, 0 = wschód (oś X+)
        self.fuel = float(fuel)
        self.max_fuel = float(fuel)
        self.steps = 0

        # Historia trasy: lista krotek (x, y)
        self.path: list[tuple[float, float]] = [(self.x, self.y)]

        # Dziennik zdarzeń do raportu końcowego
        self.events_log: list[str] = []

        # Liczniki odwiedzonych elementów świata
        self.craters_hit = 0
        self.ice_found = 0
        self.radiation_entered = 0
        self.base_camps_visited = 0
        self.rock_fields_hit = 0

    # ------------------------------------------------------------------ ruch

    def compute_next_position(self, distance: float = 10.0) -> tuple[float, float]:
        """Oblicza nową pozycję przy ruchu do przodu o zadaną odległość."""
        rad = math.radians(self.angle)
        new_x = self.x + distance * math.cos(rad)
        new_y = self.y + distance * math.sin(rad)
        return round(new_x, 2), round(new_y, 2)

    def apply_position(self, new_x: float, new_y: float) -> None:
        """Zatwierdza nową pozycję i dodaje ją do historii trasy."""
        self.x = round(new_x, 2)
        self.y = round(new_y, 2)
        self.path.append((self.x, self.y))

    def turn(self, degrees: float) -> None:
        """Obraca łazik o podaną liczbę stopni (dodatnia = w lewo, ujemna = w prawo)."""
        self.angle = (self.angle + degrees) % 360

    # --------------------------------------------------------------- zasoby

    def consume_fuel(self, amount: float) -> float:
        """Zużywa paliwo; zwraca faktycznie zużytą ilość."""
        amount = max(0.0, amount)
        actual = min(self.fuel, amount)
        self.fuel = round(self.fuel - actual, 2)
        return actual

    def refuel(self, amount: float) -> float:
        """Uzupełnia paliwo do maksimum; zwraca faktycznie dodaną ilość."""
        amount = max(0.0, amount)
        space = self.max_fuel - self.fuel
        actual = min(space, amount)
        self.fuel = round(self.fuel + actual, 2)
        return actual

    # ------------------------------------------------------- dystans do celu

    def distance_to(self, tx: float, ty: float) -> float:
        return round(math.sqrt((self.x - tx) ** 2 + (self.y - ty) ** 2), 2)

    # ----------------------------------------------------------------- repr

    def status_line(self) -> str:
        return (
            f"Pozycja: ({self.x:+.1f}, {self.y:+.1f})  "
            f"Kąt: {self.angle:.0f}°  "
            f"Paliwo: {self.fuel:.1f}/{self.max_fuel:.1f}"
        )
# world.py
import random
import math


# ─────────────────────────────────────────── typy elementów świata

ELEMENT_CRATER       = "KRATER"
ELEMENT_ICE          = "ZŁOŻE_LODU"
ELEMENT_RADIATION    = "STREFA_RADIACJI"
ELEMENT_BASE_CAMP    = "BAZA_WYPADOWA"
ELEMENT_ROCK_FIELD   = "POLE_SKAŁ"


ELEMENT_SYMBOLS = {
    ELEMENT_CRATER:     "💥",
    ELEMENT_ICE:        "🧊",
    ELEMENT_RADIATION:  "☢️ ",
    ELEMENT_BASE_CAMP:  "🏕️ ",
    ELEMENT_ROCK_FIELD: "🪨",
}

ELEMENT_DESCRIPTIONS = {
    ELEMENT_CRATER:
        "Krater uderzeniowy – gwałtowne hamowanie i uszkodzenie.",
    ELEMENT_ICE:
        "Złoże lodu – można odparować wodę i uzupełnić ogniwa paliwowe.",
    ELEMENT_RADIATION:
        "Strefa radiacji – osłania panele słoneczne, drenaż energii.",
    ELEMENT_BASE_CAMP:
        "Baza wypadowa – można tu uzupełnić zapasy.",
    ELEMENT_ROCK_FIELD:
        "Pole skał – trudny teren blokujący ruch.",
}


class WorldElement:
    """Pojedynczy element umieszczony w świecie."""

    def __init__(self, element_type: str, x: float, y: float, radius: float = 8.0):
        self.element_type = element_type
        self.x = x
        self.y = y
        self.radius = radius  # promień oddziaływania

    def distance_to(self, rx: float, ry: float) -> float:
        return math.sqrt((self.x - rx) ** 2 + (self.y - ry) ** 2)

    def contains(self, rx: float, ry: float) -> bool:
        return self.distance_to(rx, ry) <= self.radius

    def symbol(self) -> str:
        return ELEMENT_SYMBOLS.get(self.element_type, "?")

    def description(self) -> str:
        return ELEMENT_DESCRIPTIONS.get(self.element_type, "Nieznany element.")

    def __repr__(self) -> str:
        return f"{self.element_type}@({self.x:.0f},{self.y:.0f})"


class World:
    """
    Dwuwymiarowy świat marsjański.
    Granice: x ∈ [-limit, +limit], y ∈ [-limit, +limit].
    Zawiera losowo rozmieszczone elementy terenu oraz zdefiniowany cel wyprawy.
    """

    def __init__(self, limit: float, target_x: float, target_y: float,
                 num_elements: int = 15, seed: int | None = None):
        self.limit = limit                          # granica świata (jeden bok)
        self.target_x = target_x
        self.target_y = target_y
        self.elements: list[WorldElement] = []
        self._rng = random.Random(seed)
        self._generate_elements(num_elements)

    # -------------------------------------------------- generowanie świata

    def _generate_elements(self, count: int) -> None:
        """Losowo rozmieszcza elementy terenu z zachowaniem minimalnego rozkładu typów."""
        margin = 12.0
        lo = -self.limit + margin
        hi =  self.limit - margin

        # Zapewniamy przynajmniej 2 elementy każdego z 5 typów
        types_pool = (
            [ELEMENT_CRATER]     * 3 +
            [ELEMENT_ICE]        * 3 +
            [ELEMENT_RADIATION]  * 2 +
            [ELEMENT_BASE_CAMP]  * 2 +
            [ELEMENT_ROCK_FIELD] * 3
        )
        self._rng.shuffle(types_pool)

        attempts = 0
        placed = 0
        while placed < count and attempts < count * 20:
            attempts += 1
            ex = round(self._rng.uniform(lo, hi), 1)
            ey = round(self._rng.uniform(lo, hi), 1)

            # Nie kładziemy elementu zbyt blisko startu (0,0) ani celu
            if math.sqrt(ex**2 + ey**2) < 20:
                continue
            if math.sqrt((ex - self.target_x)**2 + (ey - self.target_y)**2) < 15:
                continue

            etype = types_pool[placed % len(types_pool)]
            radius = 10.0 if etype == ELEMENT_RADIATION else 8.0
            self.elements.append(WorldElement(etype, ex, ey, radius))
            placed += 1

    # -------------------------------------------------- sprawdzanie granic

    def is_within_bounds(self, x: float, y: float) -> bool:
        return -self.limit <= x <= self.limit and -self.limit <= y <= self.limit

    def clamp_to_bounds(self, x: float, y: float) -> tuple[float, float]:
        cx = max(-self.limit, min(self.limit, x))
        cy = max(-self.limit, min(self.limit, y))
        return round(cx, 2), round(cy, 2)

    # ----------------------------------------------- wykrywanie elementów

    def get_element_at(self, x: float, y: float) -> WorldElement | None:
        """Zwraca pierwszy element terenu w zasięgu danej pozycji."""
        for el in self.elements:
            if el.contains(x, y):
                return el
        return None

    # -------------------------------------------------- cel wyprawy

    def target_reached(self, x: float, y: float, tolerance: float = 12.0) -> bool:
        return math.sqrt((x - self.target_x)**2 + (y - self.target_y)**2) <= tolerance

    def distance_to_target(self, x: float, y: float) -> float:
        return round(math.sqrt((x - self.target_x)**2 + (y - self.target_y)**2), 2)

    # ----------------------------------------------------------------- repr

    def info(self) -> str:
        return (
            f"Granice świata: X ∈ [{-self.limit}, {self.limit}], "
            f"Y ∈ [{-self.limit}, {self.limit}]\n"
            f"Cel wyprawy: ({self.target_x}, {self.target_y})\n"
            f"Liczba elementów terenu: {len(self.elements)}"
        )
# events.py
import random


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
            import math
            dx = random.uniform(-8, 8)
            dy = random.uniform(-8, 8)
            ox, oy = rover.x, rover.y
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
# visualizer.py
import turtle


def draw_expedition(rover, world) -> None:
    """
    Rysuje w oknie Turtle:
      - granice świata,
      - osie współrzędnych,
      - punkt startowy i końcowy,
      - trasę łazika,
      - elementy terenu (jako kolorowe kropki),
      - cel wyprawy.
    """

    # ── konfiguracja okna ──────────────────────────────────────────────────
    screen = turtle.Screen()
    screen.title(f"Symulator Marsjański – trasa: {rover.name}")
    screen.bgcolor("#1a0a00")          # ciemnobrązowe tło (Mars)

    L = world.limit
    SCALE = min(350 / L, 3.5)         # przelicznik jednostek świata → piksele

    def wp(x, y):
        """Przelicza współrzędne świata na piksele ekranu."""
        return x * SCALE, y * SCALE

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()

    # ── granice świata ─────────────────────────────────────────────────────
    pen.color("#cc5500")
    pen.penup()
    sx, sy = wp(-L, -L)
    pen.goto(sx, sy)
    pen.pendown()
    for corner in [(-L, L), (L, L), (L, -L), (-L, -L)]:
        pen.goto(*wp(*corner))
    pen.penup()

    # ── osie ──────────────────────────────────────────────────────────────
    pen.color("#553300")
    pen.goto(*wp(-L, 0)); pen.pendown(); pen.goto(*wp(L, 0));  pen.penup()
    pen.goto(*wp(0, -L)); pen.pendown(); pen.goto(*wp(0, L));  pen.penup()

    # Etykiety osi
    pen.color("#aa6633")
    pen.goto(*wp(L + 5, 0)); pen.write("X", font=("Arial", 9, "normal"))
    pen.goto(*wp(0, L + 5)); pen.write("Y", font=("Arial", 9, "normal"))
    pen.goto(*wp(-L - 5, 0)); pen.write(f"{-int(L)}", font=("Arial", 7, "normal"))
    pen.goto(*wp(L,      0)); pen.write(f"+{int(L)}", font=("Arial", 7, "normal"))

    # ── elementy terenu ────────────────────────────────────────────────────
    colors_map = {
        "KRATER":        ("#444444", 6),
        "ZŁOŻE_LODU":    ("#88ddff", 6),
        "STREFA_RADIACJI": ("#aaff00", 8),
        "BAZA_WYPADOWA": ("#ffaa00", 7),
        "POLE_SKAŁ":     ("#886644", 5),
    }
    for el in world.elements:
        col, sz = colors_map.get(el.element_type, ("#ffffff", 5))
        pen.goto(*wp(el.x, el.y))
        pen.dot(sz, col)

    # ── cel wyprawy ────────────────────────────────────────────────────────
    pen.color("#ffff00")
    gx, gy = wp(world.target_x, world.target_y)
    pen.goto(gx, gy)
    pen.dot(14, "#ffff00")
    pen.goto(gx + 6, gy + 6)
    pen.write("CEL", font=("Arial", 9, "bold"))

    # ── trasa łazika ──────────────────────────────────────────────────────
    if rover.path:
        pen.color("#ff6600")
        pen.penup()
        pen.goto(*wp(*rover.path[0]))
        pen.pendown()
        pen.pensize(2)
        for px, py in rover.path[1:]:
            pen.goto(*wp(px, py))
        pen.penup()

    # ── punkt startowy ────────────────────────────────────────────────────
    sx0, sy0 = wp(*rover.path[0])
    pen.goto(sx0, sy0)
    pen.dot(12, "#00ff00")
    pen.goto(sx0 + 5, sy0 + 5)
    pen.color("#00ff00")
    pen.write("START", font=("Arial", 8, "bold"))

    # ── punkt końcowy ─────────────────────────────────────────────────────
    ex, ey = wp(*rover.path[-1])
    pen.goto(ex, ey)
    pen.dot(12, "#ff0000")
    pen.goto(ex + 5, ey + 5)
    pen.color("#ff0000")
    pen.write("KONIEC", font=("Arial", 8, "bold"))

    # ── legenda ───────────────────────────────────────────────────────────
    legend_items = [
        ("#444444", "Krater"),
        ("#88ddff", "Złoże lodu"),
        ("#aaff00", "Strefa radiacji"),
        ("#ffaa00", "Baza wypadowa"),
        ("#886644", "Pole skał"),
        ("#ffff00", "Cel wyprawy"),
        ("#00ff00", "Start"),
        ("#ff0000", "Koniec"),
    ]
    lx_start = -L * SCALE - 10
    ly_start =  L * SCALE + 30
    pen.color("#ffffff")
    pen.goto(lx_start, ly_start)
    pen.write("LEGENDA:", font=("Arial", 9, "bold"))
    for i, (col, label) in enumerate(legend_items):
        pen.goto(lx_start, ly_start - 18 * (i + 1))
        pen.dot(8, col)
        pen.goto(lx_start + 12, ly_start - 18 * (i + 1) - 4)
        pen.color("#ffffff")
        pen.write(label, font=("Arial", 8, "normal"))

    # ── tytuł ─────────────────────────────────────────────────────────────
    pen.color("#ff8800")
    pen.goto(0, L * SCALE + 18)
    pen.write(
        f"Wyprawa: {rover.name}  |  Kroki: {rover.steps}",
        align="center", font=("Arial", 10, "bold")
    )

    screen.update()
    print("\n[Turtle] Wizualizacja gotowa. Zamknij okno Turtle, aby zakończyć program.")
    turtle.done()
# report.py


def print_report(rover, world, end_reason: str, outcome: str) -> None:
    """
    Drukuje sformatowany raport końcowy wyprawy.
    """
    SEP  = "=" * 65
    SEP2 = "-" * 65

    print()
    print(SEP)
    print("              📋  RAPORT KOŃCOWY WYPRAWY  📋")
    print(SEP)

    print(f"  Nazwa łazika/wyprawy : {rover.name}")
    print(SEP2)

    # ── parametry początkowe ──────────────────────────────────────────────
    print("  PARAMETRY POCZĄTKOWE")
    start = rover.path[0]
    print(f"    Pozycja startowa    : ({start[0]:+.1f}, {start[1]:+.1f})")
    print(f"    Kąt startowy        : podany przez użytkownika")
    print(f"    Paliwo początkowe   : {rover.max_fuel:.1f}")
    print(f"    Granice świata      : ±{world.limit}")
    print(f"    Cel wyprawy         : ({world.target_x}, {world.target_y})")
    print(SEP2)

    # ── wyniki ────────────────────────────────────────────────────────────
    print("  WYNIKI WYPRAWY")
    end_pos = rover.path[-1]
    print(f"    Końcowa pozycja     : ({end_pos[0]:+.1f}, {end_pos[1]:+.1f})")
    dist_to_goal = world.distance_to_target(rover.x, rover.y)
    print(f"    Odległość od celu   : {dist_to_goal:.1f} jednostek")
    print(f"    Liczba kroków       : {rover.steps}")
    print(f"    Pozostałe paliwo    : {rover.fuel:.1f} / {rover.max_fuel:.1f}")
    print(SEP2)

    # ── statystyki terenu ─────────────────────────────────────────────────
    print("  NAPOTKANE ELEMENTY TERENU")
    print(f"    Kratery             : {rover.craters_hit}")
    print(f"    Złoża lodu          : {rover.ice_found}")
    print(f"    Strefy radiacji     : {rover.radiation_entered}")
    print(f"    Bazy wypadowe       : {rover.base_camps_visited}")
    print(f"    Pola skał           : {rover.rock_fields_hit}")
    print(SEP2)

    # ── dziennik zdarzeń ─────────────────────────────────────────────────
    print("  DZIENNIK ZDARZEŃ LOSOWYCH")
    if rover.events_log:
        for entry in rover.events_log:
            print(f"    • {entry}")
    else:
        print("    Brak zdarzeń losowych.")
    print(SEP2)

    # ── przyczyna zakończenia i wynik ─────────────────────────────────────
    print("  ZAKOŃCZENIE")
    print(f"    Przyczyna           : {end_reason}")
    print(f"    Wynik               : {outcome}")

    # Obliczenie punktacji
    score = _calculate_score(rover, world, outcome)
    print(f"    Wynik punktowy      : {score} pkt")
    print(SEP)
    print()


def _calculate_score(rover, world, outcome: str) -> int:
    """
    Oblicza wynik punktowy na podstawie:
    - pozostałego paliwa,
    - odległości od celu (im bliżej, tym lepiej),
    - liczby kroków (mniej = lepiej),
    - premii za sukces.
    """
    dist   = world.distance_to_target(rover.x, rover.y)
    score  = int(rover.fuel * 2)
    score += max(0, int((world.limit * 2 - dist) * 3))
    score += max(0, 500 - rover.steps * 5)

    if "SUKCES" in outcome.upper():
        score += 500
    elif "CZĘŚCIOWY" in outcome.upper():
        score += 150

    return max(0, score)
# main.py
"""
╔══════════════════════════════════════════════════════════════╗
║       SYMULATOR MARSJAŃSKIEJ WYPRAWY ŁAZIKA  v1.0           ║
║                                                              ║
║  Prowadź łazika po powierzchni Marsa. Zbieraj zasoby,       ║
║  unikaj niebezpieczeństw i dotrzyj do wyznaczonego celu.    ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import math
import random

from rover      import Rover
from world      import (
    World,
    ELEMENT_CRATER, ELEMENT_ICE, ELEMENT_RADIATION,
    ELEMENT_BASE_CAMP, ELEMENT_ROCK_FIELD,
)
from events     import draw_event
from report     import print_report
from visualizer import draw_expedition


# ═══════════════════════════════════════════════════════════════
#  Stałe symulacji
# ═══════════════════════════════════════════════════════════════

STEP_FUEL_COST   = 5.0     # paliwo za każdy krok ruchu do przodu
TURN_FUEL_COST   = 2.0     # paliwo za obrót
WAIT_FUEL_COST   = 1.0     # paliwo za postój
MOVE_DISTANCE    = 10.0    # odległość jednego kroku do przodu
EVENT_CHANCE     = 0.30    # 30% szans na zdarzenie losowe w danym kroku

MAX_STEPS_DEFAULT = 60     # domyślny limit kroków


# ═══════════════════════════════════════════════════════════════
#  Pomocnicze funkcje wejścia
# ═══════════════════════════════════════════════════════════════

def _input_str(prompt: str, default: str = "") -> str:
    """Wczytuje ciąg znaków; jeśli pusty, zwraca wartość domyślną."""
    raw = input(prompt).strip()
    return raw if raw else default


def _input_float(prompt: str, default: float,
                 lo: float = -1e9, hi: float = 1e9) -> float:
    """Wczytuje liczbę zmiennoprzecinkową z walidacją zakresu."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print(f"  ↳ Przyjęto wartość domyślną: {default}")
            return default
        try:
            val = float(raw)
            if lo <= val <= hi:
                return val
            print(f"  ⚠️  Wartość musi być w zakresie [{lo}, {hi}]. Spróbuj ponownie.")
        except ValueError:
            print("  ⚠️  Podaj liczbę (np. 42 lub -5.5). Spróbuj ponownie.")


def _input_int(prompt: str, default: int,
               lo: int = -10_000, hi: int = 10_000) -> int:
    """Wczytuje liczbę całkowitą z walidacją zakresu."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print(f"  ↳ Przyjęto wartość domyślną: {default}")
            return default
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(f"  ⚠️  Wartość musi być w zakresie [{lo}, {hi}]. Spróbuj ponownie.")
        except ValueError:
            print("  ⚠️  Podaj liczbę całkowitą. Spróbuj ponownie.")


# ═══════════════════════════════════════════════════════════════
#  Zbieranie parametrów
# ═══════════════════════════════════════════════════════════════

def collect_parameters() -> dict:
    """Interaktywnie zbiera od użytkownika parametry wyprawy."""

    SEP = "─" * 60

    print()
    print("═" * 60)
    print("  🚀  SYMULATOR MARSJAŃSKIEJ WYPRAWY ŁAZIKA")
    print("═" * 60)
    print()
    print("  Witaj, Dowódco Misji!")
    print("  Skonfigurujesz teraz parametry wyprawy łazika po Marsie.")
    print("  (Naciśnij ENTER, aby zaakceptować wartość domyślną.)")
    print()

    # ── nazwa ─────────────────────────────────────────────────────────────
    print(SEP)
    print("  [1] NAZWA ŁAZIKA")
    print("      Dowolna nazwa identyfikująca Twojego łazika.")
    name = _input_str("      Nazwa łazika [ARES-1]: ", "ARES-1")

    # ── pozycja startowa ──────────────────────────────────────────────────
    print()
    print(SEP)
    print("  [2] POZYCJA STARTOWA")
    print("      Współrzędne (x, y) punktu startowego łazika.")
    print("      Zalecany zakres: od -30 do +30 (centrum mapy).")
    sx = _input_float("      Pozycja X startowa [0]: ", 0.0, -80.0, 80.0)
    sy = _input_float("      Pozycja Y startowa [0]: ", 0.0, -80.0, 80.0)

    # ── kąt startowy ──────────────────────────────────────────────────────
    print()
    print(SEP)
    print("  [3] KĄT STARTOWY")
    print("      Kierunek, w którym łazik jest zwrócony na starcie.")
    print("        0°  = wschód (oś X+)")
    print("       90°  = północ (oś Y+)")
    print("      180°  = zachód (oś X-)")
    print("      270°  = południe (oś Y-)")
    angle = _input_float("      Kąt startowy (0–359°) [45]: ", 45.0, 0.0, 359.0)

    # ── paliwo ────────────────────────────────────────────────────────────
    print()
    print(SEP)
    print("  [4] POZIOM PALIWA")
    print("      Początkowy zapas paliwa łazika.")
    print("      Każdy ruch kosztuje paliwo. Gdy paliwo = 0, misja kończy się.")
    print("      Zalecany zakres: 100–300.")
    fuel = _input_float("      Poziom paliwa [200]: ", 200.0, 20.0, 500.0)

    # ── granice świata ────────────────────────────────────────────────────
    print()
    print(SEP)
    print("  [5] ROZMIAR ŚWIATA")
    print("      Określa granicę kwadratowej mapy od środka do krawędzi.")
    print("      Np. 100 → mapa X ∈ [-100, 100], Y ∈ [-100, 100].")
    world_limit = _input_float("      Granica świata [100]: ", 100.0, 40.0, 300.0)

    # ── cel wyprawy ───────────────────────────────────────────────────────
    print()
    print(SEP)
    print("  [6] CEL WYPRAWY")
    print("      Współrzędne celu, do którego łazik musi dotrzeć.")
    print(f"      Zakres: od {-world_limit:.0f} do {world_limit:.0f}.")
    tx = _input_float(f"      Cel X [60]: ", 60.0, -world_limit, world_limit)
    ty = _input_float(f"      Cel Y [60]: ", 60.0, -world_limit, world_limit)

    # ── limit kroków ─────────────────────────────────────────────────────
    print()
    print(SEP)
    print("  [7] LIMIT KROKÓW")
    print("      Maksymalna liczba kroków misji. Po jej przekroczeniu")
    print("      misja kończy się niezależnie od pozycji łazika.")
    max_steps = _input_int("      Limit kroków [60]: ", 60, 10, 300)

    print()
    print(SEP)
    print()

    return {
        "name":        name,
        "sx":          sx,
        "sy":          sy,
        "angle":       angle,
        "fuel":        fuel,
        "world_limit": world_limit,
        "tx":          tx,
        "ty":          ty,
        "max_steps":   max_steps,
    }


# ═══════════════════════════════════════════════════════════════
#  Obsługa efektów elementu świata
# ═══════════════════════════════════════════════════════════════

def apply_world_element(rover: Rover, world: World,
                        element, pre_x: float, pre_y: float) -> list[str]:
    """
    Stosuje efekty elementu terenu na łazika.
    Zwraca listę komunikatów do wypisania.
    """
    msgs: list[str] = []
    etype = element.element_type

    if etype == ELEMENT_CRATER:
        fuel_lost = rover.consume_fuel(20)
        # łazik wraca do poprzedniej pozycji
        rover.apply_position(pre_x, pre_y)
        rover.craters_hit += 1
        msgs.append(f"  💥 KRATER! Łazik wpadł w krater i musi się wycofać.")
        msgs.append(f"     Utrata paliwa: {fuel_lost:.1f}. Powrót do ({pre_x}, {pre_y}).")
        rover.events_log.append(f"Krok {rover.steps}: Krater – cofnięcie, -{fuel_lost:.1f} paliwa")

    elif etype == ELEMENT_ICE:
        gained = rover.refuel(25)
        rover.ice_found += 1
        msgs.append(f"  🧊 ZŁOŻE LODU! Łazik napełnia ogniwa paliwowe.")
        msgs.append(f"     Uzupełnienie paliwa: +{gained:.1f}.")
        rover.events_log.append(f"Krok {rover.steps}: Złoże lodu – +{gained:.1f} paliwa")

    elif etype == ELEMENT_RADIATION:
        fuel_lost = rover.consume_fuel(15)
        rover.radiation_entered += 1
        msgs.append(f"  ☢️  STREFA RADIACJI! Panele słoneczne osłabione.")
        msgs.append(f"     Utrata paliwa: {fuel_lost:.1f}.")
        rover.events_log.append(f"Krok {rover.steps}: Strefa radiacji – -{fuel_lost:.1f} paliwa")

    elif etype == ELEMENT_BASE_CAMP:
        gained = rover.refuel(30)
        rover.base_camps_visited += 1
        msgs.append(f"  🏕️  BAZA WYPADOWA! Uzupełnienie zapasów.")
        msgs.append(f"     Uzupełnienie paliwa: +{gained:.1f}.")
        rover.events_log.append(f"Krok {rover.steps}: Baza wypadowa – +{gained:.1f} paliwa")

    elif etype == ELEMENT_ROCK_FIELD:
        rover.apply_position(pre_x, pre_y)  # łazik zostaje w miejscu
        fuel_lost = rover.consume_fuel(8)
        rover.rock_fields_hit += 1
        msgs.append(f"  🪨 POLE SKAŁ! Teren nieprzejezdny – łazik zatrzymany.")
        msgs.append(f"     Utrata paliwa: {fuel_lost:.1f}. Łazik wrócił do ({pre_x}, {pre_y}).")
        rover.events_log.append(f"Krok {rover.steps}: Pole skał – blokada, -{fuel_lost:.1f} paliwa")

    return msgs


# ═══════════════════════════════════════════════════════════════
#  Wyświetlanie menu akcji i obsługa wyboru
# ═══════════════════════════════════════════════════════════════

def get_player_action() -> str:
    """Pyta użytkownika o akcję w danym kroku."""
    print()
    print("  Wybierz akcję:")
    print("    [1] Jedź do przodu")
    print("    [2] Obróć w lewo  (o 45°)")
    print("    [3] Obróć w prawo (o 45°)")
    print("    [4] Obróć o dowolny kąt")
    print("    [5] Stój w miejscu (odpoczynek)")
    print("    [Q] Przerwij wyprawę")

    while True:
        choice = input("  Twój wybór: ").strip().upper()
        if choice in ("1", "2", "3", "4", "5", "Q"):
            return choice
        print("  ⚠️  Wpisz 1, 2, 3, 4, 5 lub Q.")


# ═══════════════════════════════════════════════════════════════
#  Główna pętla symulacji
# ═══════════════════════════════════════════════════════════════

def run_simulation(params: dict) -> tuple[Rover, World, str, str]:
    """
    Prowadzi główną pętlę symulacji.
    Zwraca (rover, world, przyczyna_zakończenia, wynik_tekstowy).
    """

    SEP  = "═" * 65
    SEP2 = "─" * 65

    # ── inicjalizacja ─────────────────────────────────────────────────────
    rover = Rover(
        name  = params["name"],
        x     = params["sx"],
        y     = params["sy"],
        angle = params["angle"],
        fuel  = params["fuel"],
    )

    world = World(
        limit     = params["world_limit"],
        target_x  = params["tx"],
        target_y  = params["ty"],
        num_elements = max(10, int(params["world_limit"] / 5)),
        seed      = None,
    )

    max_steps = params["max_steps"]

    # ── nagłówek misji ────────────────────────────────────────────────────
    print()
    print(SEP)
    print(f"  🚀  MISJA ROZPOCZĘTA: {rover.name}")
    print(SEP)
    print(f"  Pozycja startowa : ({rover.x:+.1f}, {rover.y:+.1f})")
    print(f"  Kąt startowy     : {rover.angle:.0f}°")
    print(f"  Paliwo początkowe: {rover.fuel:.1f}")
    print(world.info())
    print(f"  Limit kroków     : {max_steps}")
    print()
    print("  LEGENDA ELEMENTÓW TERENU:")
    print("    💥 Krater       – cofnięcie, utrata 20 paliwa")
    print("    🧊 Złoże lodu   – uzupełnienie 25 paliwa")
    print("    ☢️  Strefa radiacji – utrata 15 paliwa")
    print("    🏕️  Baza wypadowa  – uzupełnienie 30 paliwa")
    print("    🪨 Pole skał    – blokada, utrata 8 paliwa")
    print()
    print("  ZDARZENIA LOSOWE (szansa 30%/krok):")
    print("    🌪️  Burza piaskowa, ☀️  Wzmocnienie słoneczne,")
    print("    🔧 Awaria sprzętu, 🌍 Trzęsienie, ☄️  Meteoryty")
    print()
    print("  Powodzenia, Dowódco!")
    print(SEP)

    end_reason = ""
    outcome    = ""

    # ── pętla kroków ──────────────────────────────────────────────────────
    while True:
        rover.steps += 1
        step_num = rover.steps

        print()
        print(SEP2)
        print(f"  ▶  KROK {step_num}/{max_steps}")
        print(f"     {rover.status_line()}")
        dist = world.distance_to_target(rover.x, rover.y)
        print(f"     Odległość od celu: {dist:.1f} jednostek")
        print(SEP2)

        # Zapamiętanie stanu przed krokiem
        pre_x, pre_y   = rover.x, rover.y
        pre_fuel       = rover.fuel
        pre_angle      = rover.angle

        # ── akcja gracza ────────────────────────────────────────────────
        action = get_player_action()

        if action == "Q":
            end_reason = "Użytkownik przerwał wyprawę."
            outcome    = "PRZERWANIE – częściowy sukces"
            break

        # ── wykonanie akcji ─────────────────────────────────────────────
        print()
        if action == "1":   # jazda do przodu
            new_x, new_y = rover.compute_next_position(MOVE_DISTANCE)

            # Sprawdzenie granic
            if not world.is_within_bounds(new_x, new_y):
                clamped_x, clamped_y = world.clamp_to_bounds(new_x, new_y)
                print(f"  ⚠️  GRANICA ŚWIATA! Łazik zatrzymany na krawędzi.")
                print(f"     Planowana poz.: ({new_x:.1f}, {new_y:.1f}) → "
                      f"({clamped_x:.1f}, {clamped_y:.1f})")
                new_x, new_y = clamped_x, clamped_y
                rover.consume_fuel(3)

            rover.apply_position(new_x, new_y)
            fuel_used = rover.consume_fuel(STEP_FUEL_COST)
            print(f"  ➡️  Jazda do przodu ({MOVE_DISTANCE:.0f} j.) "
                  f"| Kąt: {rover.angle:.0f}°")
            print(f"     Pozycja: ({pre_x:+.1f}, {pre_y:+.1f}) → "
                  f"({rover.x:+.1f}, {rover.y:+.1f})")
            print(f"     Paliwo: {pre_fuel:.1f} → {rover.fuel:.1f}  "
                  f"(zużyto {fuel_used:.1f})")

            # Sprawdzenie elementu terenu
            element = world.get_element_at(rover.x, rover.y)
            if element:
                print(f"  📍 Wkroczono w: {element.element_type}  "
                      f"({element.description()})")
                for msg in apply_world_element(rover, world, element, pre_x, pre_y):
                    print(msg)

        elif action == "2":   # obrót lewo
            rover.turn(45)
            fuel_used = rover.consume_fuel(TURN_FUEL_COST)
            print(f"  ↺  Obrót w lewo 45° | Nowy kąt: {rover.angle:.0f}°")
            print(f"     Paliwo: {pre_fuel:.1f} → {rover.fuel:.1f}  "
                  f"(zużyto {fuel_used:.1f})")

        elif action == "3":   # obrót prawo
            rover.turn(-45)
            fuel_used = rover.consume_fuel(TURN_FUEL_COST)
            print(f"  ↻  Obrót w prawo 45° | Nowy kąt: {rover.angle:.0f}°")
            print(f"     Paliwo: {pre_fuel:.1f} → {rover.fuel:.1f}  "
                  f"(zużyto {fuel_used:.1f})")

        elif action == "4":   # obrót o dowolny kąt
            deg = _input_float(
                "     Podaj kąt obrotu (+ lewo, - prawo) [-180..180]: ",
                default=0.0, lo=-180.0, hi=180.0
            )
            rover.turn(deg)
            fuel_used = rover.consume_fuel(TURN_FUEL_COST)
            print(f"  🔄 Obrót o {deg:+.0f}° | Nowy kąt: {rover.angle:.0f}°")
            print(f"     Paliwo: {pre_fuel:.1f} → {rover.fuel:.1f}  "
                  f"(zużyto {fuel_used:.1f})")

        elif action == "5":   # postój
            fuel_used = rover.consume_fuel(WAIT_FUEL_COST)
            print(f"  ⏸  Postój. Łazik przeprowadza diagnostykę.")
            print(f"     Paliwo: {pre_fuel:.1f} → {rover.fuel:.1f}  "
                  f"(zużyto {fuel_used:.1f})")

        # ── zdarzenie losowe ────────────────────────────────────────────
        if random.random() < EVENT_CHANCE:
            event = draw_event(step_num)
            if event:
                for msg in event.apply(rover, world):
                    print(msg)

        # ── warunki zakończenia ─────────────────────────────────────────

        # 1. Brak paliwa
        if rover.fuel <= 0:
            end_reason = "Paliwo wyczerpane – łazik unieruchomiony."
            outcome    = "PORAŻKA – brak paliwa"
            print()
            print("  ❌ PALIWO WYCZERPANE! Misja zakończona niepowodzeniem.")
            break

        # 2. Dotarcie do celu
        if world.target_reached(rover.x, rover.y):
            end_reason = "Łazik dotarł do celu misji."
            outcome    = "SUKCES – cel osiągnięty!"
            print()
            print("  🎉 CEL MISJI OSIĄGNIĘTY! Gratulacje, Dowódco!")
            break

        # 3. Przekroczenie limitu kroków
        if step_num >= max_steps:
            end_reason = f"Przekroczono limit {max_steps} kroków."
            dist_final = world.distance_to_target(rover.x, rover.y)
            if dist_final < world.limit * 0.25:
                outcome = "CZĘŚCIOWY SUKCES – blisko celu, czas wyczerpany"
            else:
                outcome = "PORAŻKA – czas misji przekroczony"
            print()
            print(f"  ⏰ LIMIT KROKÓW ({max_steps}) OSIĄGNIĘTY. Misja zakończona.")
            break

    return rover, world, end_reason, outcome


# ═══════════════════════════════════════════════════════════════
#  Punkt wejścia
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    print(__doc__)

    while True:
        params = collect_parameters()
        rover, world, end_reason, outcome = run_simulation(params)

        print_report(rover, world, end_reason, outcome)

        print("  Czy chcesz uruchomić wizualizację trasy w oknie Turtle? (tak/nie) [tak]: ",
              end="")
        vis_ans = input().strip().lower()
        if vis_ans in ("", "tak", "t", "yes", "y"):
            try:
                draw_expedition(rover, world)
            except Exception as e:
                print(f"  [Turtle] Nie udało się otworzyć wizualizacji: {e}")

        print()
        print("═" * 65)
        print("  Czy chcesz rozpocząć nową wyprawę? (tak/nie) [nie]: ", end="")
        again = input().strip().lower()
        if again not in ("tak", "t", "yes", "y"):
            print()
            print("  Dziękujemy za udział w Marsjańskiej Ekspedycji!")
            print("  Do zobaczenia na Marsie! 🚀")
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()
# 🚀 Symulator Marsjańskiej Wyprawy Łazika

## Opis
Symulator ekspedycji łazika po dwuwymiarowej powierzchni Marsa.
Steruj łazikiem krok po kroku, zarządzaj paliwem, reaguj na zdarzenia
losowe i dotrzyj do wyznaczonego celu misji.

## Wymagania
- Python 3.11 (bez dodatkowych bibliotek)
- Moduły standardowe: `math`, `random`, `turtle`, `sys`

## Uruchomienie
```bash
python main.py
