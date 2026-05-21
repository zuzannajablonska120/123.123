# 🦇 Symulator Nietoperza w Jaskini

## Opis
Symulator ucieczki nietoperza z mrocznej, dwuwymiarowej jaskini.
Steruj nietoperzem krok po kroku, zarządzaj zapasem echolokacji (energii), unikaj niebezpiecznych stalagmitów oraz stalaktytów i odnajdź wyjście na wolność.

Projekt oferuje:
- **Dwa języki**: Interfejs w języku polskim i angielskim.
- **Wizualizacja na żywo**: Podgląd trasy nietoperza w czasie rzeczywistym przy użyciu biblioteki `turtle`.
- **Zdarzenia losowe**: Podmuchy wiatru, roje owadów, spadające kamienie i inne wyzwania.
- **Elementy terenu**: Chmary komarów (regeneracja), stalagnaty (blokady), bezpieczne szczeliny.

## Wymagania
- Python 3.11+
- Moduły standardowe: `math`, `random`, `turtle`, `sys`, `tkinter` (wymagany przez turtle do grafiki).

## Uruchomienie
```bash
python main.py
```

Po uruchomieniu program zapyta o preferowany język oraz parametry misji. Jeśli środowisko nie obsługuje grafiki (brak display), symulacja będzie kontynuowana w trybie tekstowym.

## Sterowanie
- **[1]** Lot do przodu
- **[2] / [3]** Obrót o 45 stopni
- **[4]** Obrót o dowolny kąt
- **[5]** Odpoczynek
- **[Q]** Przerwanie misji

---

# 🦇 Bat in a Cave Simulator

## Description
A simulator of a bat escaping from a dark, two-dimensional cave.
Control the bat step by step, manage your echolocation (energy) supply, avoid dangerous stalagmites and stalactites, and find the way to freedom.

The project features:
- **Dual Language**: Polish and English interface.
- **Live Visualization**: Real-time preview of the bat's path using the `turtle` library.
- **Random Events**: Wind gusts, insect swarms, falling rocks, and other challenges.
- **Cave Elements**: Mosquito swarms (regeneration), stalagnates (blockades), safe crevices.

## Requirements
- Python 3.11+
- Standard modules: `math`, `random`, `turtle`, `sys`, `tkinter` (required by turtle for graphics).

## Running
```bash
python main.py
```

After startup, the program will ask for your preferred language and mission parameters. If the environment does not support graphics (no display), the simulation will continue in text mode.

## Controls
- **[1]** Fly forward
- **[2] / [3]** Turn 45 degrees
- **[4]** Turn by any angle
- **[5]** Rest
- **[Q]** Abort mission
