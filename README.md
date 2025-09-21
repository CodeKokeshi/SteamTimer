# Steam Play Hours Simulator

> An alternative runnable placeholder for games in your Steam library so you can let the actual game rest while still accumulating play hours in Steam.

This application is a lightweight, distraction-free timer you add to Steam as a **Non-Steam Game** and launch in place of (or alongside) a title installed elsewhere (Epic, GOG, manual install, etc.). While it runs, Steam records active playtime for that entry. The window simply shows an always‑advancing elapsed counter in `DD : HH : MM : SS` with subtle animation and optional offset. It does **not** hook, fake processes, touch the filesystem beyond normal library usage, or communicate over the network.

Use it if you've migrated stores, lost legacy hours, or want to preserve hardware/energy by not keeping a heavy game executable open just to accumulate time. Close it any moment—no state is persisted unless you extend it.

> Disclaimer: Purposefully inflating playtime may violate platform Terms of Service, achievements integrity expectations, or community norms. You alone are responsible for how you use this tool. It transmits nothing; it just counts locally.

---
**Project Meta**

| Item | Value |
|------|-------|
| Language | Python 3.11+ (tested) |
| GUI Toolkit | PySide6 (Qt 6) |
| Primary Dependency | `PySide6>=6.7.0,<7.0.0` |
| Packaging (example) | PyInstaller (`--onefile --windowed`) |
| License | The Unlicense (Public Domain) |
| Platforms | Windows (primary), should also run on macOS / Linux with Qt libs |
| Author Credit | CodeKokeshi |
| Project Type | Single-file utility (no persistence) |

---

## Quick Start
```powershell
python -m venv .venv
.# Activate virtual environment
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
python main.py
```

## Features
- Clean dark UI built with PySide6 (Qt 6)
- Large live-updating timer (days:hours:minutes:seconds)
- Optional starting offset (`--offset-hours` or `--offset-seconds`)
- Always-on-top toggle
- Reset (with confirmation)
- Subtle animated pulse (can disable via `--no-accent-pulse`)
- Compact mode (`--compact`)

## Advanced Run Examples

### Start with an offset (existing hours)
```powershell
python main.py --offset-hours 12.5
# or
python main.py --offset-seconds 4500
```

### Disable pulsing animation
```powershell
python main.py --no-accent-pulse
```

### Compact window
```powershell
python main.py --compact
```

## Build a Standalone EXE
Install PyInstaller:
```powershell
pip install pyinstaller
```
Build:
```powershell
pyinstaller --noconfirm --onefile --windowed --name "Steam Play Hours Simulator" main.py
```
The executable will appear under `dist/Steam Play Hours Simulator.exe`.

(If the name with spaces causes issues adding to Steam, you can rename the EXE.)

## Add to Steam
1. Open Steam > `Games` > `Add a Non-Steam Game to My Library...`
2. Browse to the generated `.exe` (or use `python.exe` with launch options pointing to `main.py`).
3. Launch from Steam when you want hours to accumulate.
4. Leave it running; elapsed time updates each second.

## Command Line Help
```powershell
python main.py --help
```

## Notes / Future Ideas
- Persist elapsed time across restarts by writing a small JSON with `start_epoch` or cumulative seconds.
- System tray integration to minimize clutter.
- Pause/resume functionality.
- Export a simple log of session durations.

## License
Released under **The Unlicense**. Public domain dedication—do anything you want; attribution appreciated but not required.

See `LICENSE` for the full text.
