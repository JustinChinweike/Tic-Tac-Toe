# Tic‑Tac‑Toe

Small game. Clean layers. One engine. Three faces.

## Features
* Unbeatable AI (alpha‑beta minimax)
* Console, Tkinter window, Browser (PyScript)
* Live AI scoring + tree peek (browser)
* Difficulty presets (random → expert)
* Strict rule validation (no impossible boards)
* Keyboard + screen reader friendly
* Fast test suite, type checked, linted

## Quick Start (Browser)
```powershell
cd docs
python -m http.server 8000
# open http://localhost:8000
```
Toggle the brain icon to see scores. Export tree with the disk icon.

## Console
```powershell
ttt-console -h
ttt-console -X human -O minimax --starting X
ttt-console -X minimax -O random --starting O
```
Players: human | random | minimax

## Tkinter Window
```powershell
ttt-window
```
Swap player types in the window frontend if you want AI vs AI.

## Code Layout
```
logic/    models, minimax, validators
game/     engine, players, renderers
frontends console, window, browser (PyScript)
```
Immutable models + pure search keep things predictable.

## Install (Dev)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e tic-tac-toe/library[dev]
```

## Run Checks
```powershell
ruff check tic-tac-toe/library/src
mypy --config-file mypy.ini tic-tac-toe/library/src
pytest -q
```

## Test Notes
Property tests hammer rules. Minimax tests check optimal play and speed.

## Accessibility
Arrows move. Enter / Space places. Live region announces turns and result.

## Export
Click export. Clipboard fallback appears if blocked.



