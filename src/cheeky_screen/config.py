from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    cooldown_seconds: float = 2.0
    model_path: Path | None = None
    min_detection_confidence: float = 0.6
    min_tracking_confidence: float = 0.6
    preview: bool = True
    screenshot_dir: Path = Path("screenshots")
