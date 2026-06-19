from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike

SCREENSHOT_NOTIFICATION_WINDOW = "Screenshot taken"


def show_screenshot_notification(path: Path) -> None:
    image = build_notification_image(path)
    cv2.namedWindow(SCREENSHOT_NOTIFICATION_WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(SCREENSHOT_NOTIFICATION_WINDOW, 520, 180)
    cv2.imshow(SCREENSHOT_NOTIFICATION_WINDOW, image)

    while is_window_open(SCREENSHOT_NOTIFICATION_WINDOW):
        if cv2.waitKey(50) != -1:
            break

    cv2.destroyWindow(SCREENSHOT_NOTIFICATION_WINDOW)


def build_notification_image(path: Path) -> MatLike:
    image = np.full((180, 520, 3), 245, dtype=np.uint8)
    cv2.putText(
        image,
        "Screenshot taken",
        (36, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.95,
        (30, 30, 30),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        str(path),
        (36, 112),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (80, 80, 80),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        "Press any key or close this window.",
        (36, 146),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (80, 80, 80),
        1,
        cv2.LINE_AA,
    )
    return image


def is_window_open(window_name: str) -> bool:
    try:
        return cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1
    except cv2.error:
        return False
