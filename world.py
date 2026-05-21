import random
import math


# ─────────────────────────────────────────── typy elementów świata

ELEMENT_STALAGMITE      = "STALAGMITE"
ELEMENT_STALACTITE      = "STALACTITE"
ELEMENT_STALAGNATE      = "STALAGNATE"
ELEMENT_MOSQUITO_SWARM  = "MOSQUITO_SWARM"
ELEMENT_STRONG_DRAFT    = "STRONG_DRAFT"
ELEMENT_SAFE_CREVICE    = "SAFE_CREVICE"


ELEMENT_SYMBOLS = {
    ELEMENT_STALAGMITE:     "💥",
    ELEMENT_STALACTITE:     "💥",
    ELEMENT_STALAGNATE:     "🪨",
    ELEMENT_MOSQUITO_SWARM: "🦟",
    ELEMENT_STRONG_DRAFT:   "💨",
    ELEMENT_SAFE_CREVICE:   "🦇",
}

ELEMENT_DESCRIPTIONS = {
    "pl": {
        ELEMENT_STALAGMITE:     "Stalagmit – przeszkoda wyrastająca z dna jaskini.",
        ELEMENT_STALACTITE:     "Stalaktyt – przeszkoda zwisająca ze stropu.",
        ELEMENT_STALAGNATE:     "Stalagnat – potężna kolumna łącząca dno ze stropem.",
        ELEMENT_MOSQUITO_SWARM: "Chmara komarów – pożywne śniadanie dla nietoperza.",
        ELEMENT_STRONG_DRAFT:   "Silny przeciąg – wiatr utrudniający lot.",
        ELEMENT_SAFE_CREVICE:   "Bezpieczna szczelina – idealne miejsce na odpoczynek.",
    },
    "en": {
        ELEMENT_STALAGMITE:     "Stalagmite – an obstacle rising from the cave floor.",
        ELEMENT_STALACTITE:     "Stalactite – an obstacle hanging from the ceiling.",
        ELEMENT_STALAGNATE:     "Stalagnate – a massive column connecting floor and ceiling.",
        ELEMENT_MOSQUITO_SWARM: "Mosquito swarm – a nutritious breakfast for the bat.",
        ELEMENT_STRONG_DRAFT:   "Strong draft – wind making flight difficult.",
        ELEMENT_SAFE_CREVICE:   "Safe crevice – a perfect place for rest.",
    }
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

    def description(self, lang="pl") -> str:
        return ELEMENT_DESCRIPTIONS.get(lang, ELEMENT_DESCRIPTIONS["pl"]).get(self.element_type, "Unknown element.")

    def __repr__(self) -> str:
        return f"{self.element_type}@({self.x:.0f},{self.y:.0f})"


class World:
    """
    Dwuwymiarowy świat jaskini.
    Granice: x ∈ [-limit, +limit], y ∈ [-limit, +limit].
    Zawiera losowo rozmieszczone elementy terenu oraz zdefiniowane wyjście z jaskini.
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

        # Zapewniamy przynajmniej kilka elementów każdego typu
        types_pool = (
            [ELEMENT_STALAGMITE]     * 2 +
            [ELEMENT_STALACTITE]     * 2 +
            [ELEMENT_STALAGNATE]     * 3 +
            [ELEMENT_MOSQUITO_SWARM] * 3 +
            [ELEMENT_STRONG_DRAFT]   * 2 +
            [ELEMENT_SAFE_CREVICE]   * 3
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
            radius = 10.0 if etype == ELEMENT_STRONG_DRAFT else 8.0
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

    def info(self, lang="pl") -> str:
        if lang == "pl":
            return (
                f"Granice jaskini: X ∈ [{-self.limit}, {self.limit}], "
                f"Y ∈ [{-self.limit}, {self.limit}]\n"
                f"Wyjście z jaskini: ({self.target_x}, {self.target_y})\n"
                f"Liczba elementów jaskini: {len(self.elements)}"
            )
        else:
            return (
                f"Cave boundaries: X ∈ [{-self.limit}, {self.limit}], "
                f"Y ∈ [{-self.limit}, {self.limit}]\n"
                f"Cave exit: ({self.target_x}, {self.target_y})\n"
                f"Number of cave elements: {len(self.elements)}"
            )
