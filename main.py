import sys
import random

from bat       import Bat
from world     import (
    World,
    ELEMENT_STALAGMITE, ELEMENT_STALACTITE, ELEMENT_STALAGNATE,
    ELEMENT_MOSQUITO_SWARM, ELEMENT_STRONG_DRAFT, ELEMENT_SAFE_CREVICE,
)
from events     import draw_event
from report     import print_report
from visualizer import init_visualizer, draw_update, close_visualizer
from i18n       import get_text




STEP_ECHO_COST   = 5.0     
TURN_ECHO_COST   = 2.0     
WAIT_ECHO_COST   = 1.0     
MOVE_DISTANCE    = 10.0   
EVENT_CHANCE     = 0.30    

MAX_STEPS_DEFAULT = 60



def _input_str(prompt: str, default: str = "") -> str:
    raw = input(prompt).strip()
    return raw if raw else default


def _input_float(prompt: str, default: float,
                 lo: float = -1e9, hi: float = 1e9, lang="pl") -> float:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return default
        try:
            val = float(raw)
            if lo <= val <= hi:
                return val
            if lang == "pl":
                print(f"  ⚠️  Wartość musi być w zakresie [{lo}, {hi}].")
            else:
                print(f"  ⚠️  Value must be in range [{lo}, {hi}].")
        except ValueError:
            if lang == "pl":
                print("  ⚠️  Wymagana liczba.")
            else:
                print("  ⚠️  Number required.")


def _input_int(prompt: str, default: int,
               lo: int = -10_000, hi: int = 10_000, lang="pl") -> int:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return default
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            if lang == "pl":
                print(f"  ⚠️  Wartość musi być w zakresie [{lo}, {hi}].")
            else:
                print(f"  ⚠️  Value must be in range [{lo}, {hi}].")
        except ValueError:
            if lang == "pl":
                print("  ⚠️  Wymagana liczba całkowita.")
            else:
                print("  ⚠️  Integer required.")



def collect_parameters(lang="pl") -> dict:
    SEP = "─" * 60

    print()
    print("═" * 60)
    print(f"  🦇  {get_text('title', lang)}")
    print("═" * 60)
    print()
    print(f"  {get_text('welcome', lang)}")
    print(f"  {get_text('config_params', lang)}")
    print(f"  {get_text('enter_default', lang)}")
    print()

 
    print(SEP)
    print(f"  [1] {get_text('bat_name', lang)}")
    name = _input_str(f"      {get_text('bat_name_prompt', lang)}", "ACE")

 
    print()
    print(SEP)
    print(f"  [2] {get_text('start_pos', lang)}")
    sx = _input_float("      X [0]: ", 0.0, -80.0, 80.0, lang)
    sy = _input_float("      Y [0]: ", 0.0, -80.0, 80.0, lang)

  
    print()
    print(SEP)
    print(f"  [3] {get_text('start_angle', lang)}")
    angle = _input_float("      (0–359°) [45]: ", 45.0, 0.0, 359.0, lang)

 
    print()
    print(SEP)
    print(f"  [4] {get_text('echolocation_level', lang)}")
    fuel = _input_float("      [200]: ", 200.0, 20.0, 500.0, lang)


    print()
    print(SEP)
    print(f"  [5] {get_text('world_size', lang)}")
    world_limit = _input_float("      [100]: ", 100.0, 40.0, 300.0, lang)

 
    print()
    print(SEP)
    print(f"  [6] {get_text('mission_target', lang)}")
    tx = _input_float(f"      X [60]: ", 60.0, -world_limit, world_limit, lang)
    ty = _input_float(f"      Y [60]: ", 60.0, -world_limit, world_limit, lang)

   
    print()
    print(SEP)
    print(f"  [7] {get_text('step_limit', lang)}")
    max_steps = _input_int("      [60]: ", 60, 10, 300, lang)

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



def apply_world_element(bat: Bat, world: World,
                        element, pre_x: float, pre_y: float, lang="pl") -> list[str]:
    msgs: list[str] = []
    etype = element.element_type

    if etype == ELEMENT_STALAGMITE:
        echo_lost = bat.consume_echolocation(20)
        bat.apply_position(pre_x, pre_y)
        bat.stalagmites_hit += 1
        msgs.append(f"  {get_text('stalagmite_hit', lang)}")
        bat.events_log.append(f"Step {bat.steps}: Stalagmite -{echo_lost:.1f} echo")

    elif etype == ELEMENT_STALACTITE:
        echo_lost = bat.consume_echolocation(20)
        bat.apply_position(pre_x, pre_y)
        bat.stalactites_hit += 1
        msgs.append(f"  {get_text('stalactite_hit', lang)}")
        bat.events_log.append(f"Step {bat.steps}: Stalactite -{echo_lost:.1f} echo")

    elif etype == ELEMENT_MOSQUITO_SWARM:
        gained = bat.restore_echolocation(25)
        bat.mosquito_swarms_found += 1
        msgs.append(f"  {get_text('mosquito_swarm_found', lang)}")
        bat.events_log.append(f"Step {bat.steps}: Mosquito swarm +{gained:.1f} echo")

    elif etype == ELEMENT_STRONG_DRAFT:
        echo_lost = bat.consume_echolocation(15)
        bat.strong_drafts_entered += 1
        msgs.append(f"  {get_text('strong_draft_entered', lang)}")
        bat.events_log.append(f"Step {bat.steps}: Strong draft -{echo_lost:.1f} echo")

    elif etype == ELEMENT_SAFE_CREVICE:
        gained = bat.restore_echolocation(30)
        bat.safe_crevices_visited += 1
        msgs.append(f"  {get_text('safe_crevice_found', lang)}")
        bat.events_log.append(f"Step {bat.steps}: Safe crevice +{gained:.1f} echo")

    elif etype == ELEMENT_STALAGNATE:
        bat.apply_position(pre_x, pre_y)
        echo_lost = bat.consume_echolocation(8)
        bat.stalagnates_hit += 1
        msgs.append(f"  {get_text('stalagnate_hit', lang)}")
        bat.events_log.append(f"Step {bat.steps}: Stalagnate -{echo_lost:.1f} echo")

    return msgs



def get_player_action(lang="pl") -> str:
    print()
    print(f"  {get_text('choose_action', lang)}")
    print(f"    [1] {get_text('action_forward', lang)}")
    print(f"    [2] {get_text('action_left', lang)}")
    print(f"    [3] {get_text('action_right', lang)}")
    print(f"    [4] {get_text('action_any', lang)}")
    print(f"    [5] {get_text('action_wait', lang)}")
    print(f"    [Q] {get_text('action_quit', lang)}")

    while True:
        choice = input(f"  {get_text('your_choice', lang)}").strip().upper()
        if choice in ("1", "2", "3", "4", "5", "Q"):
            return choice
        print("  ⚠️  1, 2, 3, 4, 5, Q.")



def run_simulation(params: dict, lang="pl") -> tuple[Bat, World, str, str]:
    SEP  = "═" * 65
    SEP2 = "─" * 65

    bat = Bat(
        name         = params["name"],
        x            = params["sx"],
        y            = params["sy"],
        angle        = params["angle"],
        echolocation = params["fuel"],
    )

    world = World(
        limit     = params["world_limit"],
        target_x  = params["tx"],
        target_y  = params["ty"],
        num_elements = max(10, int(params["world_limit"] / 5)),
        seed      = None,
    )

    max_steps = params["max_steps"]


    init_visualizer(bat, world, lang)

    print()
    print(SEP)
    print(f"  🦇  {get_text('mission_started', lang)}: {bat.name}")
    print(SEP)
    print(world.info(lang))
    print(SEP)

    end_reason = ""
    outcome    = ""

    while True:
        bat.steps += 1
        step_num = bat.steps

        print()
        print(SEP2)
        print(f"  ▶  KROK {step_num}/{max_steps}")
        print(f"     {bat.status_line(lang)}")
        dist = world.distance_to_target(bat.x, bat.y)
        print(f"     {get_text('distance_to_target', lang)}: {dist:.1f}")
        print(SEP2)

        pre_x, pre_y   = bat.x, bat.y
        pre_echo       = bat.echolocation

        action = get_player_action(lang)

        if action == "Q":
            end_reason = get_text('action_quit', lang)
            outcome    = "ABORTED" if lang == "en" else "PRZERWANO"
            break

        print()
        if action == "1":
            new_x, new_y = bat.compute_next_position(MOVE_DISTANCE)

            if not world.is_within_bounds(new_x, new_y):
                clamped_x, clamped_y = world.clamp_to_bounds(new_x, new_y)
                print(f"  ⚠️  {get_text('cave_limit_hit', lang)}")
                new_x, new_y = clamped_x, clamped_y
                bat.consume_echolocation(3)

            bat.apply_position(new_x, new_y)
            echo_used = bat.consume_echolocation(STEP_ECHO_COST)
            print(f"  ➡️  {get_text('flying_forward', lang)} | Echo: {pre_echo:.1f} → {bat.echolocation:.1f}")

            element = world.get_element_at(bat.x, bat.y)
            if element:
                print(f"  📍 {element.description(lang)}")
                for msg in apply_world_element(bat, world, element, pre_x, pre_y, lang):
                    print(msg)

        elif action == "2":
            bat.turn(45)
            echo_used = bat.consume_echolocation(TURN_ECHO_COST)
            print(f"  ↺  {get_text('turned_left', lang)} | Echo: {bat.echolocation:.1f}")

        elif action == "3":
            bat.turn(-45)
            echo_used = bat.consume_echolocation(TURN_ECHO_COST)
            print(f"  ↻  {get_text('turned_right', lang)} | Echo: {bat.echolocation:.1f}")

        elif action == "4":
            prompt = "     Kąt [-180..180]: " if lang == "pl" else "     Angle [-180..180]: "
            deg = _input_float(prompt, 0.0, -180.0, 180.0, lang)
            bat.turn(deg)
            echo_used = bat.consume_echolocation(TURN_ECHO_COST)
            print(f"  🔄 {get_text('turned_any', lang)} {deg}° | Echo: {bat.echolocation:.1f}")

        elif action == "5":
            echo_used = bat.consume_echolocation(WAIT_ECHO_COST)
            print(f"  ⏸  {get_text('hanging', lang)} | Echo: {bat.echolocation:.1f}")

        if random.random() < EVENT_CHANCE:
            event = draw_event(step_num)
            if event:
                for msg in event.apply(bat, world, lang):
                    print(msg)

      
        draw_update(bat, world, lang)

        if bat.echolocation <= 0:
            end_reason = get_text('echolocation_depleted', lang)
            outcome    = "FAILURE" if lang == "en" else "PORAŻKA"
            print(f"\n  ❌ {end_reason}")
            break

        if world.target_reached(bat.x, bat.y):
            end_reason = get_text('target_reached', lang)
            outcome    = "SUCCESS" if lang == "en" else "SUKCES"
            print(f"\n  🎉 {end_reason}")
            break

        if step_num >= max_steps:
            end_reason = get_text('step_limit_reached', lang)
            dist_final = world.distance_to_target(bat.x, bat.y)
            if dist_final < world.limit * 0.25:
                outcome = "PARTIAL SUCCESS" if lang == "en" else "CZĘŚCIOWY SUKCES"
            else:
                outcome = "FAILURE" if lang == "en" else "PORAŻKA"
            print(f"\n  ⏰ {end_reason}")
            break

    return bat, world, end_reason, outcome



def main() -> None:

    print("\n  Wybierz język / Choose language (pl/en) [pl]: ", end="")
    lang_choice = input().strip().lower()
    lang = "en" if lang_choice == "en" else "pl"

    while True:
        params = collect_parameters(lang)
        bat, world, end_reason, outcome = run_simulation(params, lang)

        print_report(bat, world, end_reason, outcome, lang)

        print(f"\n  {get_text('restart_mission', lang)} ", end="")
        again = input().strip().lower()
        if again not in ("tak", "t", "yes", "y"):
            print(f"\n  {get_text('thanks', lang)}")
            close_visualizer()
            sys.exit(0)


if __name__ == "__main__":
    main()
