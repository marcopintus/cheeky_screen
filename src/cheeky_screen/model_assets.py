from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlretrieve

HAND_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)


class ModelAssetError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ModelAssetResolver:
    cache_dir: Path = Path(".cache") / "cheeky_screen"
    file_name: str = "hand_landmarker.task"
    url: str = HAND_LANDMARKER_URL

    def resolve(self) -> Path:
        target = self.cache_dir / self.file_name
        if target.exists():
            return target

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            urlretrieve(self.url, target)
        except (OSError, URLError) as exc:
            target.unlink(missing_ok=True)
            raise ModelAssetError(
                "Could not download the MediaPipe hand landmarker model. "
                f"Download it manually from {self.url} and save it as {target}."
            ) from exc

        return target
