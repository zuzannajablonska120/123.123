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
