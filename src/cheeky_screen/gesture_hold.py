from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class GestureHold:
    seconds: float
    now: Callable[[], float] = monotonic
    _started_at: float | None = None

    def update(self, detected: bool) -> bool:
        if not detected:
            self.reset()
            return False

        current = self.now()
        if self._started_at is None:
            self._started_at = current
            return self.seconds <= 0

        return current - self._started_at >= self.seconds

    def reset(self) -> None:
        self._started_at = None
