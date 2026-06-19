from cheeky_screen.gesture_hold import GestureHold


def test_hold_does_not_trigger_on_first_detection() -> None:
    current = 10.0
    hold = GestureHold(seconds=0.5, now=lambda: current)

    assert not hold.update(detected=True)


def test_hold_triggers_after_gesture_is_sustained() -> None:
    current = 10.0
    hold = GestureHold(seconds=0.5, now=lambda: current)

    assert not hold.update(detected=True)

    current = 10.49
    assert not hold.update(detected=True)

    current = 10.5
    assert hold.update(detected=True)


def test_hold_resets_when_gesture_disappears() -> None:
    current = 10.0
    hold = GestureHold(seconds=0.5, now=lambda: current)

    assert not hold.update(detected=True)

    current = 10.4
    assert not hold.update(detected=False)

    current = 10.8
    assert not hold.update(detected=True)
