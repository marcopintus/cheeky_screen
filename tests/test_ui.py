from pathlib import Path

from cheeky_screen.ui import build_notification_image


def test_notification_image_is_created() -> None:
    image = build_notification_image(Path("screenshots/screenshot.png"))

    assert image.shape == (180, 520, 3)
    assert image.min() < 245
