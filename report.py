from i18n import get_text

def print_report(bat, world, end_reason: str, outcome: str, lang="pl") -> None:
    """
    Drukuje sformatowany raport końcowy misji.
    """
    SEP  = "=" * 65
    SEP2 = "-" * 65

    print()
    print(SEP)
    print(f"              📋  {get_text('report_title', lang)}  📋")
    print(SEP)

    print(f"  {get_text('bat_name_report', lang)} : {bat.name}")
    print(SEP2)

    # ── parametry początkowe ──────────────────────────────────────────────
    print(f"  {get_text('initial_params', lang)}")
    start = bat.path[0]
    print(f"    {get_text('start_pos', lang)}    : ({start[0]:+.1f}, {start[1]:+.1f})")
    print(f"    {get_text('echolocation_level', lang)}   : {bat.max_echolocation:.1f}")
    print(f"    {get_text('world_size', lang)}      : ±{world.limit}")
    print(f"    {get_text('mission_target', lang)}         : ({world.target_x}, {world.target_y})")
    print(SEP2)

    # ── wyniki ────────────────────────────────────────────────────────────
    print(f"  {get_text('results', lang)}")
    end_pos = bat.path[-1]
    print(f"    {get_text('final_pos', lang)}     : ({end_pos[0]:+.1f}, {end_pos[1]:+.1f})")
    dist_to_goal = world.distance_to_target(bat.x, bat.y)
    print(f"    {get_text('dist_to_goal', lang)}   : {dist_to_goal:.1f}")
    print(f"    {get_text('steps_count', lang)}       : {bat.steps}")
    print(f"    {get_text('remaining_echo', lang)}    : {bat.echolocation:.1f} / {bat.max_echolocation:.1f}")
    print(SEP2)

    # ── statystyki terenu ─────────────────────────────────────────────────
    print(f"  {get_text('encountered_elements', lang)}")
    print(f"    {get_text('stalagmite', lang):<20}: {bat.stalagmites_hit}")
    print(f"    {get_text('stalactite', lang):<20}: {bat.stalactites_hit}")
    print(f"    {get_text('stalagnate', lang):<20}: {bat.stalagnates_hit}")
    print(f"    {get_text('mosquito_swarm', lang):<20}: {bat.mosquito_swarms_found}")
    print(f"    {get_text('strong_draft', lang):<20}: {bat.strong_drafts_entered}")
    print(f"    {get_text('safe_crevice', lang):<20}: {bat.safe_crevices_visited}")
    print(SEP2)

    # ── dziennik zdarzeń ─────────────────────────────────────────────────
    print(f"  {get_text('events_log', lang)}")
    if bat.events_log:
        for entry in bat.events_log:
            print(f"    • {entry}")
    else:
        print("    " + ("Brak zdarzeń losowych." if lang == "pl" else "No random events."))
    print(SEP2)

    # ── przyczyna zakończenia i wynik ─────────────────────────────────────
    print(f"  {get_text('termination', lang)}")
    print(f"    {'Przyczyna' if lang == 'pl' else 'Reason'}: {end_reason}")
    print(f"    {'Wynik' if lang == 'pl' else 'Outcome'}: {outcome}")

    # Obliczenie punktacji
    score = _calculate_score(bat, world, outcome)
    print(f"    {get_text('score', lang)}      : {score}")
    print(SEP)
    print()


def _calculate_score(bat, world, outcome: str) -> int:
    """
    Oblicza wynik punktowy na podstawie:
    - pozostałego paliwa,
    - odległości od celu (im bliżej, tym lepiej),
    - liczby kroków (mniej = lepiej),
    - premii za sukces.
    """
    dist   = world.distance_to_target(bat.x, bat.y)
    score  = int(bat.echolocation * 2)
    score += max(0, int((world.limit * 2 - dist) * 3))
    score += max(0, 500 - bat.steps * 5)

    # "SUKCES" or "SUCCESS"
    if "SUKCES" in outcome.upper() or "SUCCESS" in outcome.upper():
        score += 500
    elif "CZĘŚCIOWY" in outcome.upper() or "PARTIAL" in outcome.upper():
        score += 150

    return max(0, score)
