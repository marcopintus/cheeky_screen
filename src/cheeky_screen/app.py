from __future__ import annotations

import logging

import cv2

from cheeky_screen.camera import Camera
from cheeky_screen.config import AppConfig
from cheeky_screen.cooldown import Cooldown
from cheeky_screen.gesture_hold import GestureHold
from cheeky_screen.gestures import MiddleFingerGesture
from cheeky_screen.hand_tracking import HandTracker
from cheeky_screen.model_assets import ModelAssetResolver
from cheeky_screen.screenshot import ScreenshotService
from cheeky_screen.ui import is_window_open, show_screenshot_notification

LOGGER = logging.getLogger(__name__)
WINDOW_NAME = "Cheeky Screen"
EXIT_KEYS = {ord("q"), 27}


def run(config: AppConfig) -> None:
    gesture = MiddleFingerGesture()
    cooldown = Cooldown(config.cooldown_seconds)
    gesture_hold = GestureHold(config.gesture_hold_seconds)
    model_path = config.model_path or ModelAssetResolver().resolve()
    screenshots = ScreenshotService(config.screenshot_dir)

    try:
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

                gesture_detected = any(gesture.matches(hand) for hand in tracked.hands)
                if gesture_hold.update(gesture_detected) and cooldown.ready():
                    path = screenshots.capture()
                    cooldown.trigger()
                    gesture_hold.reset()
                    LOGGER.info("Screenshot saved to %s", path)
                    show_screenshot_notification(path)

                if config.preview:
                    cv2.imshow(WINDOW_NAME, tracked.annotated_frame)
                    if _should_exit_preview():
                        break
    except KeyboardInterrupt:
        LOGGER.info("Exiting.")
    finally:
        cv2.destroyAllWindows()


def _should_exit_preview() -> bool:
    key = cv2.waitKey(1) & 0xFF
    return key in EXIT_KEYS or not is_window_open(WINDOW_NAME)
