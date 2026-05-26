import math


class Bat:
    """
    Reprezentuje nietoperza poruszającego się po dwuwymiarowej jaskini.
    Przechowuje pozycję, kąt skierowania, poziom echolokacji oraz historię trasy.
    """

    def __init__(self, name: str, x: float, y: float, angle: float, echolocation: float):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle) % 360  
        self.echolocation = float(echolocation)
        self.max_echolocation = float(echolocation)
        self.steps = 0

        
        self.path: list[tuple[float, float]] = [(self.x, self.y)]

        
        self.events_log: list[str] = []

        
        self.stalagmites_hit = 0
        self.stalactites_hit = 0
        self.stalagnates_hit = 0
        self.mosquito_swarms_found = 0
        self.strong_drafts_entered = 0
        self.safe_crevices_visited = 0

   

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
        """Obraca nietoperza o podaną liczbę stopni (dodatnia = w lewo, ujemna = w prawo)."""
        self.angle = (self.angle + degrees) % 360

   

    def consume_echolocation(self, amount: float) -> float:
        """Zużywa echolokację; zwraca faktycznie zużytą ilość."""
        amount = max(0.0, amount)
        actual = min(self.echolocation, amount)
        self.echolocation = round(self.echolocation - actual, 2)
        return actual

    def restore_echolocation(self, amount: float) -> float:
        """Uzupełnia echolokację do maksimum; zwraca faktycznie dodaną ilość."""
        amount = max(0.0, amount)
        space = self.max_echolocation - self.echolocation
        actual = min(space, amount)
        self.echolocation = round(self.echolocation + actual, 2)
        return actual

    

    def distance_to(self, tx: float, ty: float) -> float:
        return round(math.sqrt((self.x - tx) ** 2 + (self.y - ty) ** 2), 2)

    

    def status_line(self, lang="pl") -> str:
        if lang == "pl":
            return (
                f"Pozycja: ({self.x:+.1f}, {self.y:+.1f})  "
                f"Kąt: {self.angle:.0f}°  "
                f"Echolokacja: {self.echolocation:.1f}/{self.max_echolocation:.1f}"
            )
        else:
            return (
                f"Position: ({self.x:+.1f}, {self.y:+.1f})  "
                f"Angle: {self.angle:.0f}°  "
                f"Echolocation: {self.echolocation:.1f}/{self.max_echolocation:.1f}"
            )
