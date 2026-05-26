import turtle
from i18n import get_text


_screen = None
_pen = None

def init_visualizer(bat, world, lang="pl"):
    global _screen, _pen
    try:
        _screen = turtle.Screen()
        _screen.title(get_text("title", lang))
        _screen.bgcolor("#0a0a0a")  
        _screen.tracer(0)

        _pen = turtle.Turtle()
        _pen.hideturtle()
        _pen.speed(0)

        draw_update(bat, world, lang)
    except Exception as e:
        print(f"\n  [Visualizer] Warning: Could not initialize graphics: {e}")
        _screen = None
        _pen = None

def draw_update(bat, world, lang="pl"):
    global _screen, _pen
    if _pen is None or _screen is None:
        return

    _pen.clear()
    _pen.penup()

    L = world.limit

    SCALE = min(350 / L, 3.5) if L > 0 else 1.0

    def wp(x, y):
        return x * SCALE, y * SCALE

 
    _pen.color("#333333") # Dark grey walls
    _pen.penup()
    sx, sy = wp(-L, -L)
    _pen.goto(sx, sy)
    _pen.pendown()
    for corner in [(-L, L), (L, L), (L, -L), (-L, -L)]:
        _pen.goto(*wp(*corner))
    _pen.penup()

 
    colors_map = {
        "STALAGMITE":      ("#666666", 6),
        "STALACTITE":      ("#888888", 6),
        "STALAGNATE":      ("#444444", 10),
        "MOSQUITO_SWARM":  ("#ff3333", 4),
        "STRONG_DRAFT":    ("#5555ff", 8),
        "SAFE_CREVICE":    ("#00ff00", 7),
    }
    for el in world.elements:
        col, sz = colors_map.get(el.element_type, ("#ffffff", 5))
        _pen.goto(*wp(el.x, el.y))
        _pen.dot(sz, col)


    _pen.color("#ffff00")
    gx, gy = wp(world.target_x, world.target_y)
    _pen.goto(gx, gy)
    _pen.dot(14, "#ffff00")
    _pen.goto(gx + 6, gy + 6)
    _pen.write(get_text("goal", lang), font=("Arial", 9, "bold"))


    if bat.path:
        _pen.color("#aaaaaa")
        _pen.penup()
        _pen.goto(*wp(*bat.path[0]))
        _pen.pendown()
        _pen.pensize(1)
        for px, py in bat.path[1:]:
            _pen.goto(*wp(px, py))
        _pen.penup()


    sx0, sy0 = wp(*bat.path[0])
    _pen.goto(sx0, sy0)
    _pen.dot(10, "#0000ff")
    _pen.color("#0000ff")
    _pen.write(get_text("start", lang), font=("Arial", 8, "bold"))

   
    ex, ey = wp(bat.x, bat.y)
    _pen.goto(ex, ey)
    
    _pen.dot(12, "#ffffff")
    _pen.color("#ffffff")
    _pen.write(bat.name, font=("Arial", 8, "italic"))

 
    legend_items = [
        ("#666666", get_text("stalagmite", lang)),
        ("#888888", get_text("stalactite", lang)),
        ("#444444", get_text("stalagnate", lang)),
        ("#ff3333", get_text("mosquito_swarm", lang)),
        ("#5555ff", get_text("strong_draft", lang)),
        ("#00ff00", get_text("safe_crevice", lang)),
        ("#ffff00", get_text("goal", lang)),
        ("#ffffff", bat.name),
    ]
    lx_start = -L * SCALE - 20
    ly_start =  L * SCALE + 50
    _pen.color("#ffffff")
    _pen.goto(lx_start, ly_start)
    _pen.write(get_text("legend", lang) + ":", font=("Arial", 9, "bold"))
    for i, (col, label) in enumerate(legend_items):
        _pen.goto(lx_start, ly_start - 15 * (i + 1))
        _pen.dot(8, col)
        _pen.goto(lx_start + 12, ly_start - 15 * (i + 1) - 4)
        _pen.color("#ffffff")
        _pen.write(label, font=("Arial", 8, "normal"))


    _pen.color("#ffffff")
    _pen.goto(0, L * SCALE + 20)
    status_txt = f"{bat.name} | Steps: {bat.steps} | Echo: {bat.echolocation:.1f}"
    _pen.write(status_txt, align="center", font=("Arial", 10, "bold"))

    _screen.update()

def close_visualizer():
    try:
        turtle.bye()
    except:
        pass
