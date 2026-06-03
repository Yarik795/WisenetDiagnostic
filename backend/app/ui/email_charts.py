from __future__ import annotations

from typing import Optional

from .email_history_series import DayPoint


def _scale_series(
    values: list[Optional[int]],
    height: int,
    padding: int,
) -> list[Optional[float]]:
    present = [v for v in values if v is not None]
    if not present:
        return [None] * len(values)
    vmin, vmax = min(present), max(present)
    span = max(vmax - vmin, 1)
    inner = height - 2 * padding
    out: list[Optional[float]] = []
    for v in values:
        if v is None:
            out.append(None)
        else:
            out.append(padding + inner * (1 - (v - vmin) / span))
    return out


def _polyline_points(
    ys: list[Optional[float]],
    width: int,
    padding_x: int,
) -> str:
    n = len(ys)
    if n == 0:
        return ""
    step = (width - 2 * padding_x) / max(n - 1, 1)
    parts: list[str] = []
    for i, y in enumerate(ys):
        if y is None:
            continue
        x = padding_x + i * step
        parts.append(f"{x:.1f},{y:.1f}")
    return " ".join(parts)


def render_trend_sparkline_svg(
    points: list[DayPoint],
    *,
    width: int = 520,
    height: int = 120,
) -> str:
    problems = [p.problem_count for p in points]
    nvr = [p.recorders_with_errors for p in points]
    pad_y = 12
    pad_x = 8
    y_problems = _scale_series(problems, height, pad_y)
    y_nvr = _scale_series(nvr, height, pad_y)
    line_problems = _polyline_points(y_problems, width, pad_x)
    line_nvr = _polyline_points(y_nvr, width, pad_x)

    labels = "".join(
        f'<text x="{pad_x + i * ((width - 2 * pad_x) / max(len(points) - 1, 1)):.0f}" '
        f'y="{height - 2}" text-anchor="middle" font-size="10" fill="#5c6370">'
        f"{p.date_label}</text>"
        for i, p in enumerate(points)
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Динамика за {len(points)} дней">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>',
    ]
    if line_problems:
        parts.append(
            f'<polyline fill="none" stroke="#c0392b" stroke-width="2" '
            f'points="{line_problems}"/>'
        )
    if line_nvr:
        parts.append(
            f'<polyline fill="none" stroke="#1a5fb4" stroke-width="2" '
            f'stroke-dasharray="4 3" points="{line_nvr}"/>'
        )
    parts.append(labels)
    parts.append(
        '<text x="8" y="14" font-size="10" fill="#c0392b">● проблемы</text>'
        '<text x="100" y="14" font-size="10" fill="#1a5fb4">— NVR</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
