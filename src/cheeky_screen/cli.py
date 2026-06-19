from __future__ import annotations

import argparse
import logging
from pathlib import Path

from cheeky_screen.app import run
from cheeky_screen.config import AppConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cheeky-screen",
        description="Take a screenshot when the configured webcam hand gesture is detected.",
    )
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--cooldown", type=float, default=2.0, help="Seconds between screenshots.")
    parser.add_argument(
        "--screenshot-dir",
        type=Path,
        default=Path("screenshots"),
        help="Directory where screenshots are saved.",
    )
    parser.add_argument("--no-preview", action="store_true", help="Run without the preview window.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    run(
        AppConfig(
            camera_index=args.camera_index,
            cooldown_seconds=args.cooldown,
            preview=not args.no_preview,
            screenshot_dir=args.screenshot_dir,
        )
    )
    return 0
