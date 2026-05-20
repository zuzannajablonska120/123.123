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
