from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Protocol

import cv2
import mediapipe as mp
from cv2.typing import MatLike
from mediapipe.tasks.python import BaseOptions, vision

from cheeky_screen.landmarks import HandLandmark, HandLandmarks, Landmark


class NormalizedLandmark(Protocol):
    x: float
    y: float
    z: float


HAND_CONNECTIONS = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (0, 17),
)


@dataclass(slots=True)
class TrackedHands:
    hands: list[HandLandmarks]
    annotated_frame: MatLike


class HandTracker:
    def __init__(
        self,
        *,
        model_path: Path,
        min_detection_confidence: float,
        min_tracking_confidence: float,
    ) -> None:
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._started_at = monotonic()

    def process(self, frame: MatLike) -> TrackedHands:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int((monotonic() - self._started_at) * 1000)
        results = self._landmarker.detect_for_video(image, timestamp_ms)

        annotated = frame.copy()
        hands = [self._extract_hand(hand_landmarks) for hand_landmarks in results.hand_landmarks]

        for hand_landmarks in hands:
            self._draw_landmarks(annotated, hand_landmarks)

        return TrackedHands(hands=hands, annotated_frame=annotated)

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self) -> HandTracker:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def _extract_hand(self, hand_landmarks: Sequence[NormalizedLandmark]) -> HandLandmarks:
        return {
            HandLandmark(index): Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
            )
            for index, landmark in enumerate(hand_landmarks)
        }

    def _draw_landmarks(self, frame: MatLike, hand_landmarks: HandLandmarks) -> None:
        height, width = frame.shape[:2]
        points = {
            landmark_id: (
                int(landmark.x * width),
                int(landmark.y * height),
            )
            for landmark_id, landmark in hand_landmarks.items()
        }

        for start, end in HAND_CONNECTIONS:
            cv2.line(
                frame,
                points[HandLandmark(start)],
                points[HandLandmark(end)],
                color=(80, 220, 120),
                thickness=2,
            )

        for point in points.values():
            cv2.circle(frame, point, radius=3, color=(40, 40, 240), thickness=-1)
