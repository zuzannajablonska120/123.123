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
    try:
        turtle.resetscreen()
    except turtle.Terminator:
        # Re-initialize turtle if window was closed
        pass

    screen = turtle.Screen()
    screen.title(f"Symulator Marsjański – trasa: {rover.name}")
    screen.bgcolor("#1a0a00")          # ciemnobrązowe tło (Mars)
    screen.tracer(0)                   # Wyłączamy animację dla szybkiego rysowania

    L = world.limit
    SCALE = min(350 / L, 3.5) if L > 0 else 1.0         # przelicznik jednostek świata → piksele

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
    print("\n[Turtle] Wizualizacja gotowa. Zamknij okno Turtle, aby kontynuować.")
    # turtle.mainloop() zamiast done(), aby uniknąć problemów przy wielokrotnym uruchamianiu
    # Jednak w niektórych środowiskach done() jest lepsze.
    # Aby móc zamknąć okno i wrócić do programu, używamy turtle.exitonclick() lub po prostu czekamy.
    # W większości przypadków turtle.done() wywołuje mainloop.
    try:
        turtle.done()
    except turtle.Terminator:
        pass
