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

The preview window opens by default. Press `q` or `Esc`, close the preview window, or use
`Ctrl+C` in the terminal to quit.

Screenshots are saved to `screenshots/`. The gesture must be held for 0.5 seconds before capture,
and the app waits two seconds before allowing another screenshot. After each capture, a small
"Screenshot taken" window appears; press any key or close the window to resume the webcam feed.

On first run, the app downloads the MediaPipe hand landmarker model into
`.cache/cheeky_screen/hand_landmarker.task`. You can also provide a model explicitly with
`--model-path`.

Useful options:

```powershell
cheeky-screen --camera-index 1
cheeky-screen --cooldown 3
cheeky-screen --gesture-hold 0.3
cheeky-screen --screenshot-dir C:\Temp\cheeky-shots
cheeky-screen --model-path C:\models\hand_landmarker.task
cheeky-screen --no-preview
```

## Development

```powershell
pytest
ruff check .
mypy
```
