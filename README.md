# Cheeky Screen

Cheeky Screen watches a webcam feed and saves a desktop screenshot when it detects a
raised-middle-finger gesture. It is intended as a small local prank utility and keeps the
gesture logic separate from the webcam integration so the core behavior can be tested.

## Requirements

- Python 3.11 or newer
- A working webcam

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run

```powershell
cheeky-screen
```

The preview window opens by default. Press `q` or `Esc` to quit.

Screenshots are saved to `screenshots/` and the app waits two seconds before allowing another
screenshot.

Useful options:

```powershell
cheeky-screen --camera-index 1
cheeky-screen --cooldown 3
cheeky-screen --screenshot-dir C:\Temp\cheeky-shots
cheeky-screen --no-preview
```

## Development

```powershell
pytest
ruff check .
mypy
```
