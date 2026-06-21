from pathlib import Path

import pytest

from cheeky_screen.screen_grab import (
    CommandGrabber,
    PillowGrabber,
    PortalGrabber,
    ScreenGrabError,
    default_grabber,
)


class FakeResult:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_command_grabber_builds_argv_and_writes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "shot.png"
    captured: list[list[str]] = []

    def fake_run(argv: list[str], **_: object) -> FakeResult:
        captured.append(argv)
        target.write_bytes(b"png")
        return FakeResult()

    monkeypatch.setattr("cheeky_screen.screen_grab.subprocess.run", fake_run)

    CommandGrabber("grim", ("-t", "{path}")).grab_to(target)

    assert captured == [["grim", "-t", str(target)]]


def test_command_grabber_raises_when_tool_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "cheeky_screen.screen_grab.subprocess.run",
        lambda *a, **k: FakeResult(returncode=1, stderr="no display"),
    )

    with pytest.raises(ScreenGrabError, match="no display"):
        CommandGrabber("maim", ("{path}",)).grab_to(tmp_path / "shot.png")


def test_command_grabber_raises_when_file_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Tool reports success but produces no file (e.g. silently denied).
    monkeypatch.setattr(
        "cheeky_screen.screen_grab.subprocess.run", lambda *a, **k: FakeResult(returncode=0)
    )

    with pytest.raises(ScreenGrabError):
        CommandGrabber("maim", ("{path}",)).grab_to(tmp_path / "shot.png")


def _force_x11(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cheeky_screen.screen_grab.sys.platform", "linux")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")


def test_default_grabber_uses_portal_on_wayland(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cheeky_screen.screen_grab.sys.platform", "linux")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    # X11 tools must never be chosen under Wayland, even if installed.
    monkeypatch.setattr("cheeky_screen.screen_grab.shutil.which", lambda _: "/usr/bin/maim")

    assert isinstance(default_grabber(), PortalGrabber)


def test_default_grabber_falls_back_to_pillow_without_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _force_x11(monkeypatch)
    monkeypatch.setattr("cheeky_screen.screen_grab.shutil.which", lambda _: None)

    assert isinstance(default_grabber(), PillowGrabber)


def test_default_grabber_prefers_detected_command_on_x11(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _force_x11(monkeypatch)
    monkeypatch.setattr(
        "cheeky_screen.screen_grab.shutil.which",
        lambda name: "/usr/bin/maim" if name == "maim" else None,
    )

    grabber = default_grabber()

    assert isinstance(grabber, CommandGrabber)
    assert grabber.program == "maim"
