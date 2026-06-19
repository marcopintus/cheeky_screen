from __future__ import annotations

from dataclasses import dataclass

from cheeky_screen.landmarks import HandLandmark, HandLandmarks


@dataclass(frozen=True, slots=True)
class MiddleFingerGesture:
    """Detects a raised middle finger from normalized hand landmarks.

    MediaPipe reports y=0 at the top of the frame, so an extended vertical finger has a tip
    with a smaller y value than its PIP/MCP joints.
    """

    extension_margin: float = 0.035
    folded_margin: float = 0.01

    def matches(self, landmarks: HandLandmarks) -> bool:
        return (
            self._finger_extended(
                landmarks,
                tip=HandLandmark.MIDDLE_FINGER_TIP,
                pip=HandLandmark.MIDDLE_FINGER_PIP,
                mcp=HandLandmark.MIDDLE_FINGER_MCP,
            )
            and self._finger_folded(
                landmarks,
                tip=HandLandmark.INDEX_FINGER_TIP,
                pip=HandLandmark.INDEX_FINGER_PIP,
            )
            and self._finger_folded(
                landmarks,
                tip=HandLandmark.RING_FINGER_TIP,
                pip=HandLandmark.RING_FINGER_PIP,
            )
            and self._finger_folded(
                landmarks,
                tip=HandLandmark.PINKY_TIP,
                pip=HandLandmark.PINKY_PIP,
            )
        )

    def _finger_extended(
        self,
        landmarks: HandLandmarks,
        *,
        tip: HandLandmark,
        pip: HandLandmark,
        mcp: HandLandmark,
    ) -> bool:
        tip_y = landmarks[tip].y
        pip_y = landmarks[pip].y
        mcp_y = landmarks[mcp].y
        return tip_y < pip_y - self.extension_margin and pip_y < mcp_y - self.extension_margin

    def _finger_folded(
        self,
        landmarks: HandLandmarks,
        *,
        tip: HandLandmark,
        pip: HandLandmark,
    ) -> bool:
        return landmarks[tip].y >= landmarks[pip].y - self.folded_margin
