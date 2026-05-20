"""
╔══════════════════════════════════════════════════════════════╗
║       SYMULATOR MARSJAŃSKIEJ WYPRAWY ŁAZIKA  v1.0           ║
║                                                              ║
║  Prowadź łazika po powierzchni Marsa. Zbieraj zasoby,       ║
║  unikaj niebezpieczeństw i dotrzyj do wyznaczonego celu.    ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
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
