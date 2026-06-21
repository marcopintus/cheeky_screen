# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Cheeky Screen watches a webcam feed and saves a desktop screenshot when it detects a sustained
raised-middle-finger gesture. It is a small local prank utility; the design goal is to keep the
gesture/timing logic pure and testable, isolated from the OpenCV/MediaPipe/PIL side effects.

## Commands

```bash
pip install -e ".[dev]"   # install with dev tooling
cheeky-screen             # run the app (entry point -> cheeky_screen.cli:main)

pytest                    # run all tests (config in pyproject: -q, testpaths=tests)
pytest tests/test_gestures.py::test_name   # run a single test
ruff check .              # lint
mypy                      # type-check (strict mode, files = src + tests)
```

Note: the README uses PowerShell/Windows paths, but the package is cross-platform. `PIL.ImageGrab`
(screenshot capture) requires a display server; on Linux it needs X11 with `scrot`/`gnome-screenshot`.

## Architecture

`app.run(config)` is the single orchestration loop. Everything else is a small single-responsibility
unit it composes. The loop: read frame → track hands → check gesture → gate on hold + cooldown →
capture + notify → optionally draw preview.

**Pipeline boundary (impure vs. pure).** This split is the main thing to preserve when editing:

- *Impure / I/O-bound* — touch hardware or the OS, hard to unit-test, generally not covered:
  `camera.py` (OpenCV VideoCapture), `hand_tracking.py` (MediaPipe landmarker + drawing),
  `screenshot.py` (PIL ImageGrab), `ui.py` (OpenCV windows), `model_assets.py` (model download).
- *Pure / logic* — deterministic, fully unit-tested: `gestures.py`, `gesture_hold.py`,
  `cooldown.py`, plus the data types in `landmarks.py` and `config.py`.

**Landmark contract.** `hand_tracking.HandTracker.process()` converts MediaPipe's per-hand
landmark lists into `HandLandmarks` (a `Mapping[HandLandmark, Landmark]`, see `landmarks.py`).
Everything downstream — especially `gestures.py` — depends only on this mapping, never on MediaPipe
types. `HandLandmark` is an `IntEnum` matching MediaPipe's 21-point hand model. Keep this boundary:
gesture logic should stay testable with hand-built `Landmark` dicts.

**Gesture detection convention.** MediaPipe normalizes coordinates with y=0 at the *top* of the
frame, so an extended vertical finger has a tip y *smaller* than its joints. `MiddleFingerGesture`
encodes this: middle finger extended (tip < pip < mcp by `extension_margin`) while index/ring/pinky
are folded. Any new gesture follows the same y-orientation logic and exposes a `matches(landmarks)`
method.

**Timing gates.** A capture requires both to pass, in order:
1. `GestureHold.update(detected)` — gesture must be continuously present for `gesture_hold_seconds`
   (any non-detection frame resets it). Returns True once the hold is satisfied.
2. `Cooldown.ready()` / `.trigger()` — enforces `cooldown_seconds` between captures.

Both take an injectable `now` callable (defaults to `time.monotonic`), which is how the tests drive
time deterministically. `ScreenshotService` similarly takes an injectable `Clock`. Preserve this
dependency-injection pattern when adding time- or clock-dependent behavior.

**Config flow.** CLI args (`cli.py`) → frozen `AppConfig` (`config.py`) → `app.run`. Add a new
option by extending all three; defaults live in both `AppConfig` and the argparse parser (keep them
in sync).

**Screen capture backend.** `ScreenshotService` delegates the actual grab to an injected
`ScreenGrabber` (`screen_grab.py`). `default_grabber()` is **session-aware**, not just
platform-aware: Pillow's `ImageGrab` on Windows/macOS; on Linux/Wayland the `PortalGrabber`
(xdg-desktop-portal Screenshot via D-Bus/`jeepney`); on Linux/X11 the first detected CLI tool
(`CommandGrabber`: maim → scrot → gnome-screenshot → spectacle → import), falling back to Pillow.
The Wayland distinction is essential: `PIL.ImageGrab` raises under Wayland, and the X11 CLI tools
*succeed but capture an all-black frame* — so they must never be selected for a Wayland session
(`_is_wayland()` gates this). Keep capture going through this abstraction rather than calling any
backend directly.

**Model asset.** On first run `ModelAssetResolver` downloads `hand_landmarker.task` to
`.cache/cheeky_screen/`. `--model-path` bypasses the download. A failed download deletes the partial
file and raises `ModelAssetError` with manual-download instructions.

## Conventions

- Python 3.11+, `from __future__ import annotations` at the top of every module.
- mypy runs in **strict** mode over `src` and `tests`; third-party stubs for `cv2`, `mediapipe`,
  `PIL` are ignored via overrides in `pyproject.toml`.
- Prefer frozen/slotted dataclasses for value types and small services.
