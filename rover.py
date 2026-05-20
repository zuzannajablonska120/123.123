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
