from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol

from PIL import ImageGrab


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now().astimezone()


@dataclass(slots=True)
class ScreenshotService:
    output_dir: Path
    clock: Clock = field(default_factory=SystemClock)

    def capture(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = self._next_path()
        image = ImageGrab.grab()
        image.save(target)
        return target

    def _next_path(self) -> Path:
        timestamp = self.clock.now().strftime("%Y%m%d_%H%M%S")
        candidate = self.output_dir / f"screenshot_{timestamp}.png"
        suffix = 1
        while candidate.exists():
            candidate = self.output_dir / f"screenshot_{timestamp}_{suffix}.png"
            suffix += 1
        return candidate
