from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import cv2
import mediapipe as mp
from cv2.typing import MatLike

from cheeky_screen.landmarks import HandLandmark, HandLandmarks, Landmark


@dataclass(slots=True)
class TrackedHands:
    hands: list[HandLandmarks]
    annotated_frame: MatLike


class HandTracker:
    def __init__(
        self,
        *,
        min_detection_confidence: float,
        min_tracking_confidence: float,
    ) -> None:
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._drawing = mp.solutions.drawing_utils
        self._connections = mp.solutions.hands.HAND_CONNECTIONS

    def process(self, frame: MatLike) -> TrackedHands:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)
        annotated = frame.copy()
        hands = list(self._extract_hands(results))

        for hand_landmarks in getattr(results, "multi_hand_landmarks", None) or []:
            self._drawing.draw_landmarks(annotated, hand_landmarks, self._connections)

        return TrackedHands(hands=hands, annotated_frame=annotated)

    def close(self) -> None:
        self._hands.close()

    def __enter__(self) -> HandTracker:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def _extract_hands(self, results: Any) -> Iterable[HandLandmarks]:
        for hand_landmarks in getattr(results, "multi_hand_landmarks", None) or []:
            yield {
                HandLandmark(index): Landmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                )
                for index, landmark in enumerate(hand_landmarks.landmark)
            }
