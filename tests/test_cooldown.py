from cheeky_screen.cooldown import Cooldown


def test_cooldown_is_ready_before_first_trigger() -> None:
    cooldown = Cooldown(seconds=2.0, now=lambda: 10.0)

    assert cooldown.ready()


def test_cooldown_blocks_until_enough_time_passes() -> None:
    current = 10.0
    cooldown = Cooldown(seconds=2.0, now=lambda: current)

    cooldown.trigger()

    assert not cooldown.ready()

    current = 12.0

    assert cooldown.ready()
