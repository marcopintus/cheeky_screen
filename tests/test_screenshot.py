from datetime import datetime
from pathlib import Path

from cheeky_screen.screenshot import ScreenshotService


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 6, 19, 18, 45, 30)


def test_next_path_uses_timestamp(tmp_path: Path) -> None:
    service = ScreenshotService(output_dir=tmp_path, clock=FixedClock())

    assert service._next_path() == tmp_path / "screenshot_20260619_184530.png"


def test_next_path_avoids_overwriting_existing_files(tmp_path: Path) -> None:
    existing = tmp_path / "screenshot_20260619_184530.png"
    existing.touch()
    service = ScreenshotService(output_dir=tmp_path, clock=FixedClock())

    assert service._next_path() == tmp_path / "screenshot_20260619_184530_1.png"
