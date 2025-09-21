# Steam Play Hours Simulator

A minimal, modern-looking timer window intended to be added to Steam as a **Non-Steam Game** so it accumulates runtime while you play a game purchased elsewhere (e.g. Epic). It simply displays elapsed time in `DD:HH:MM:SS`.

> Disclaimer: Intentionally inflating playtime may breach platform Terms of Service. Use at your own risk. This app sends no data anywhere; it only shows a local timer.

## Features
- Clean dark UI built with PySide6 (Qt 6)
- Large live-updating timer (days:hours:minutes:seconds)
- Optional starting offset (`--offset-hours` or `--offset-seconds`)
- Always-on-top toggle
- Reset (with confirmation)
- Subtle animated pulse (can disable via `--no-accent-pulse`)
- Compact mode (`--compact`)

## Install & Run (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### With an offset
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

## Build a standalone EXE
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
Public domain / Unlicense. Do anything; attribution appreciated but not required.
