from __future__ import annotations

import logging

import cv2

from cheeky_screen.camera import Camera
from cheeky_screen.config import AppConfig
from cheeky_screen.cooldown import Cooldown
from cheeky_screen.gestures import MiddleFingerGesture
from cheeky_screen.hand_tracking import HandTracker
from cheeky_screen.model_assets import ModelAssetResolver
from cheeky_screen.screenshot import ScreenshotService

LOGGER = logging.getLogger(__name__)
WINDOW_NAME = "Cheeky Screen"


def run(config: AppConfig) -> None:
    gesture = MiddleFingerGesture()
    cooldown = Cooldown(config.cooldown_seconds)
    model_path = config.model_path or ModelAssetResolver().resolve()
    screenshots = ScreenshotService(config.screenshot_dir)

    with (
        Camera(config.camera_index) as camera,
        HandTracker(
            model_path=model_path,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        ) as tracker,
    ):
        while True:
            frame = camera.read()
            tracked = tracker.process(frame)

            if any(gesture.matches(hand) for hand in tracked.hands) and cooldown.ready():
                path = screenshots.capture()
                cooldown.trigger()
                LOGGER.info("Screenshot saved to %s", path)

            if config.preview:
                cv2.imshow(WINDOW_NAME, tracked.annotated_frame)
                if cv2.waitKey(1) & 0xFF in {ord("q"), 27}:
                    break

    cv2.destroyAllWindows()
