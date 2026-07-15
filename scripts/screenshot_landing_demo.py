#!/usr/bin/env python3
"""Скриншоты demo/*.html → assets/screens/*.png (без перезаписи HTML)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "landing" / "demo"
SCREENS = ROOT / "landing" / "assets" / "screens"


def screenshot(html_path: Path, png_path: Path, width: int, height: int) -> None:
    from playwright.sync_api import sync_playwright

    url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()


def make_gif(frames: list[Path], out: Path) -> None:
    if len(frames) < 2:
        return
    list_file = out.with_suffix(".txt")
    lines = [f"file '{f.resolve()}'\nduration 2.5" for f in frames]
    lines.append(f"file '{frames[-1].resolve()}'")
    list_file.write_text("\n".join(lines), encoding="utf-8")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                "-vf", "fps=2,scale=1280:-1:flags=lanczos", str(out),
            ],
            check=True,
            capture_output=True,
        )
        print(f"gif: {out.name}")
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"skip gif ({exc})")
    finally:
        list_file.unlink(missing_ok=True)


def main() -> None:
    SCREENS.mkdir(parents=True, exist_ok=True)
    shots = [
        ("dashboard.html", "dashboard-summary.png", 1440, 920),
        ("payments.html", "payments.png", 1440, 1000),
        ("rvr.html", "report-rvr.png", 1440, 900),
        ("ai-chat.html", "ai-chat.png", 1440, 1100),
    ]
    for html_name, png_name, w, h in shots:
        screenshot(DEMO / html_name, SCREENS / png_name, w, h)
        print(f"screenshot: {png_name}")

    screenshot(DEMO / "dashboard.html", SCREENS / "hero-dashboard.png", 1600, 1000)
    make_gif(
        [SCREENS / "dashboard-summary.png", SCREENS / "payments.png", SCREENS / "report-rvr.png"],
        SCREENS / "hero-demo.gif",
    )
    print("done:", SCREENS)


if __name__ == "__main__":
    main()
