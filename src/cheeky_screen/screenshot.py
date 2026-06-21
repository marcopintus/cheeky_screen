from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol

from cheeky_screen.screen_grab import ScreenGrabber, default_grabber


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now().astimezone()


@dataclass(slots=True)
class ScreenshotService:
    output_dir: Path
    clock: Clock = field(default_factory=SystemClock)
    grabber: ScreenGrabber = field(default_factory=default_grabber)

    def capture(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = self._next_path()
        self.grabber.grab_to(target)
        return target

    def _next_path(self) -> Path:
        timestamp = self.clock.now().strftime("%Y%m%d_%H%M%S")
        candidate = self.output_dir / f"screenshot_{timestamp}.png"
        suffix = 1
        while candidate.exists():
            candidate = self.output_dir / f"screenshot_{timestamp}_{suffix}.png"
            suffix += 1
        return candidate
