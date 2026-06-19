from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class Cooldown:
    seconds: float
    now: Callable[[], float] = monotonic
    _last_triggered_at: float | None = None

    def ready(self) -> bool:
        return (
            self._last_triggered_at is None
            or self.now() - self._last_triggered_at >= self.seconds
        )

    def trigger(self) -> None:
        self._last_triggered_at = self.now()
