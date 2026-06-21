from __future__ import annotations

import os
import secrets
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable
from urllib.parse import urlparse
from urllib.request import url2pathname


class ScreenGrabError(RuntimeError):
    pass


@runtime_checkable
class ScreenGrabber(Protocol):
    def grab_to(self, target: Path) -> None:
        """Capture the screen and write it to ``target`` (a .png path)."""


class PillowGrabber:
    """Capture via ``PIL.ImageGrab``.

    Works on Windows and macOS, and on Linux only under a cooperative X11 server. It fails on
    Wayland sessions, which is why Linux selects a session-appropriate backend (see
    ``default_grabber``).
    """

    def grab_to(self, target: Path) -> None:
        from PIL import ImageGrab

        try:
            image = ImageGrab.grab()
        except OSError as exc:  # e.g. "X get_image failed" under Wayland/XWayland
            raise ScreenGrabError(f"PIL.ImageGrab could not capture the screen: {exc}") from exc
        image.save(target)


@dataclass(frozen=True, slots=True)
class CommandGrabber:
    """Capture by invoking an external screenshot tool that writes a file.

    ``args`` is a template; the literal token ``{path}`` is replaced with the target path. These
    tools are X11-only — under Wayland they capture a black frame, so they are selected only for
    genuine X11 sessions.
    """

    program: str
    args: tuple[str, ...]

    def grab_to(self, target: Path) -> None:
        argv = [self.program, *(arg.format(path=str(target)) for arg in self.args)]
        try:
            result = subprocess.run(argv, capture_output=True, text=True)
        except OSError as exc:
            raise ScreenGrabError(f"Could not run {self.program}: {exc}") from exc

        if result.returncode != 0 or not target.exists():
            detail = result.stderr.strip() or result.stdout.strip() or "no output"
            raise ScreenGrabError(
                f"{self.program} failed to capture the screen (exit {result.returncode}): {detail}"
            )


@dataclass(frozen=True, slots=True)
class PortalGrabber:
    """Capture via the ``xdg-desktop-portal`` Screenshot D-Bus interface.

    This is the correct Wayland path: it asks the compositor for the screen contents, so it works
    on GNOME (Mutter), KDE, and wlroots, where the X11 tools only see an empty buffer. The portal
    writes the image to its own location and returns a URI, which we move into ``target``.
    """

    timeout: float = 20.0

    def grab_to(self, target: Path) -> None:
        try:
            from jeepney import DBusAddress, MatchRule, new_method_call
            from jeepney.io.blocking import open_dbus_connection
        except ModuleNotFoundError as exc:
            raise ScreenGrabError(
                "Wayland screenshots need the 'jeepney' package (pip install jeepney)."
            ) from exc

        portal = DBusAddress(
            "/org/freedesktop/portal/desktop",
            bus_name="org.freedesktop.portal.Desktop",
            interface="org.freedesktop.portal.Screenshot",
        )
        try:
            conn = open_dbus_connection(bus="SESSION")
        except Exception as exc:  # no session bus available
            raise ScreenGrabError(f"Could not connect to the session D-Bus: {exc}") from exc

        try:
            unique = conn.unique_name[1:].replace(".", "_")
            token = "cheeky_" + secrets.token_hex(4)
            handle = f"/org/freedesktop/portal/desktop/request/{unique}/{token}"
            rule = MatchRule(
                type="signal",
                interface="org.freedesktop.portal.Request",
                member="Response",
                path=handle,
            )
            conn.send_and_get_reply(
                new_method_call(
                    DBusAddress(
                        "/org/freedesktop/DBus",
                        bus_name="org.freedesktop.DBus",
                        interface="org.freedesktop.DBus",
                    ),
                    "AddMatch",
                    "s",
                    (rule.serialise(),),
                )
            )

            call = new_method_call(
                portal,
                "Screenshot",
                "sa{sv}",
                ("", {"interactive": ("b", False), "handle_token": ("s", token)}),
            )
            conn.send_and_get_reply(call)

            with conn.filter(rule) as queue:
                try:
                    signal = conn.recv_until_filtered(queue, timeout=self.timeout)
                except TimeoutError as exc:
                    raise ScreenGrabError(
                        "Timed out waiting for the screenshot portal to respond."
                    ) from exc

            response_code, results = signal.body
            if response_code != 0:
                raise ScreenGrabError(
                    f"The screenshot portal declined the request (code {response_code})."
                )

            uri = results.get("uri")
            uri_value = uri[1] if isinstance(uri, tuple) else uri
            if not uri_value:
                raise ScreenGrabError("The screenshot portal returned no image URI.")

            source = Path(url2pathname(urlparse(uri_value).path))
            shutil.move(str(source), str(target))
        finally:
            conn.close()


# X11-only CLI fallbacks, ordered by preference. Selected only for real X11 sessions.
_X11_COMMANDS: tuple[CommandGrabber, ...] = (
    CommandGrabber("maim", ("{path}",)),
    CommandGrabber("scrot", ("{path}",)),
    CommandGrabber("gnome-screenshot", ("--file", "{path}")),
    CommandGrabber("spectacle", ("--background", "--nonotify", "--output", "{path}")),
    CommandGrabber("import", ("-window", "root", "{path}")),
)


def _is_wayland() -> bool:
    return bool(os.environ.get("WAYLAND_DISPLAY")) or (
        os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
    )


def _detect_x11_command() -> ScreenGrabber | None:
    for grabber in _X11_COMMANDS:
        if shutil.which(grabber.program) is not None:
            return grabber
    return None


def default_grabber() -> ScreenGrabber:
    """Pick the best screen-capture backend for the current platform and session.

    Windows and macOS use Pillow. On Linux the session type matters: Wayland goes through the
    desktop portal (the X11 tools capture black frames there), while X11 prefers a detected CLI
    tool and falls back to Pillow.
    """
    if sys.platform.startswith("linux"):
        if _is_wayland():
            return PortalGrabber()
        detected = _detect_x11_command()
        if detected is not None:
            return detected
    return PillowGrabber()
