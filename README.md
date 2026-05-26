# 🦇 Symulator Nietoperza w Jaskini

## Opis
Symulator ucieczki nietoperza z mrocznej, dwuwymiarowej jaskini.
Steruj nietoperzem krok po kroku, zarządzaj zapasem echolokacji (energii), unikaj niebezpiecznych stalagmitów oraz stalaktytów i odnajdź wyjście na wolność.

Projekt oferuje:
- **Dwa języki**: Interfejs w języku polskim i angielskim.
- **Wizualizacja na żywo**: Podgląd trasy nietoperza w czasie rzeczywistym przy użyciu biblioteki `turtle`.
- **Zdarzenia losowe**: Podmuchy wiatru, roje owadów, spadające kamienie i inne wyzwania.

## Legenda elementów jaskini (Mapa)
Na mapie wizualizacji oraz w komunikatach możesz napotkać następujące elementy:

| Element | Kolor (Mapa) | Symbol | Opis i Efekt |
| :--- | :--- | :---: | :--- |
| **Stalagmit** | Szary | 💥 | Przeszkoda na dnie. Uderzenie cofa nietoperza i zabiera dużo echolokacji (-20). |
| **Stalaktyt** | Jasnoszary | 💥 | Przeszkoda u góry. Uderzenie cofa nietoperza i zabiera dużo echolokacji (-20). |
| **Stalagnat** | Ciemnoszary | 🪨 | Wielka kolumna. Blokuje ruch i zabiera trochę echolokacji przy zderzeniu (-8). |
| **Chmara komarów** | Czerwony | 🦟 | Pożywne śniadanie. Przywraca zapas echolokacji (+25). |
| **Silny przeciąg** | Niebieski | 💨 | Strefa silnego wiatru. Lot przez nią jest męczący i szybciej zużywa echolokację (-15). |
| **Bezpieczna szczelina**| Zielony | 🦇 | Miejsce na odpoczynek. Przywraca znaczny zapas echolokacji (+30). |
| **Wyjście** | Żółty | 🟡 | Twój cel. Dotarcie tutaj kończy misję sukcesem. |

## Wymagania
- Python 3.11+
- Moduły standardowe: `math`, `random`, `turtle`, `sys`.

## Uruchomienie
```bash
python main.py
```

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

## Cave Elements Legend (Map)
The following elements can be found on the map and in the simulation:

| Element | Color (Map) | Symbol | Description and Effect |
| :--- | :--- | :---: | :--- |
| **Stalagmite** | Grey | 💥 | Floor obstacle. Hits push the bat back and consume a lot of echolocation (-20). |
| **Stalactite** | Light Grey | 💥 | Ceiling obstacle. Hits push the bat back and consume a lot of echolocation (-20). |
| **Stalagnate** | Dark Grey | 🪨 | Massive column. Blocks movement and consumes some echolocation on hit (-8). |
| **Mosquito Swarm** | Red | 🦟 | Nutritious breakfast. Restores echolocation (+25). |
| **Strong Draft** | Blue | 💨 | High wind zone. Flying through is tiring and drains echolocation faster (-15). |
| **Safe Crevice** | Green | 🦇 | Resting spot. Restores significant echolocation (+30). |
| **Exit** | Yellow | 🟡 | Your goal. Reaching it ends the mission with success. |

## Requirements
- Python 3.11+
- Standard modules: `math`, `random`, `turtle`, `sys`.

## Running
```bash
python main.py
```

## Controls
- **[1]** Fly forward
- **[2] / [3]** Turn 45 degrees
- **[4]** Turn by any angle
- **[5]** Rest
- **[Q]** Abort mission
