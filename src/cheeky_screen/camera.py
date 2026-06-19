from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

import cv2
from cv2.typing import MatLike


class CameraError(RuntimeError):
    pass


@dataclass(slots=True)
class Camera:
    index: int = 0
    _capture: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._capture = cv2.VideoCapture(self.index)
        if not self._capture.isOpened():
            raise CameraError(f"Could not open webcam at index {self.index}.")

    def read(self) -> MatLike:
        ok, frame = self._capture.read()
        if not ok:
            raise CameraError("Could not read a frame from the webcam.")
        return cast(MatLike, frame)

    def release(self) -> None:
        self._capture.release()

    def __enter__(self) -> Camera:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.release()
