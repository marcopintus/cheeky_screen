from cheeky_screen.gestures import MiddleFingerGesture
from cheeky_screen.landmarks import HandLandmark, Landmark


def _base_hand() -> dict[HandLandmark, Landmark]:
    return {landmark: Landmark(x=0.5, y=0.5) for landmark in HandLandmark}


def _set_finger(
    hand: dict[HandLandmark, Landmark],
    *,
    mcp: HandLandmark,
    pip: HandLandmark,
    tip: HandLandmark,
    mcp_y: float,
    pip_y: float,
    tip_y: float,
) -> None:
    hand[mcp] = Landmark(x=0.5, y=mcp_y)
    hand[pip] = Landmark(x=0.5, y=pip_y)
    hand[tip] = Landmark(x=0.5, y=tip_y)


def _middle_finger_hand() -> dict[HandLandmark, Landmark]:
    hand = _base_hand()
    _set_finger(
        hand,
        mcp=HandLandmark.INDEX_FINGER_MCP,
        pip=HandLandmark.INDEX_FINGER_PIP,
        tip=HandLandmark.INDEX_FINGER_TIP,
        mcp_y=0.55,
        pip_y=0.56,
        tip_y=0.58,
    )
    _set_finger(
        hand,
        mcp=HandLandmark.MIDDLE_FINGER_MCP,
        pip=HandLandmark.MIDDLE_FINGER_PIP,
        tip=HandLandmark.MIDDLE_FINGER_TIP,
        mcp_y=0.62,
        pip_y=0.43,
        tip_y=0.22,
    )
    _set_finger(
        hand,
        mcp=HandLandmark.RING_FINGER_MCP,
        pip=HandLandmark.RING_FINGER_PIP,
        tip=HandLandmark.RING_FINGER_TIP,
        mcp_y=0.55,
        pip_y=0.57,
        tip_y=0.59,
    )
    _set_finger(
        hand,
        mcp=HandLandmark.PINKY_MCP,
        pip=HandLandmark.PINKY_PIP,
        tip=HandLandmark.PINKY_TIP,
        mcp_y=0.55,
        pip_y=0.58,
        tip_y=0.60,
    )
    return hand


def test_middle_finger_gesture_matches_when_only_middle_finger_is_extended() -> None:
    assert MiddleFingerGesture().matches(_middle_finger_hand())


def test_middle_finger_gesture_does_not_match_open_palm() -> None:
    hand = _middle_finger_hand()
    hand[HandLandmark.INDEX_FINGER_TIP] = Landmark(x=0.5, y=0.25)
    hand[HandLandmark.RING_FINGER_TIP] = Landmark(x=0.5, y=0.30)
    hand[HandLandmark.PINKY_TIP] = Landmark(x=0.5, y=0.35)

    assert not MiddleFingerGesture().matches(hand)


def test_middle_finger_gesture_does_not_match_folded_middle_finger() -> None:
    hand = _middle_finger_hand()
    hand[HandLandmark.MIDDLE_FINGER_TIP] = Landmark(x=0.5, y=0.46)

    assert not MiddleFingerGesture().matches(hand)
