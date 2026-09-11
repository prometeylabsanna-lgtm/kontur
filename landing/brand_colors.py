"""Brand accent colors — defaults and CSS variable mapping."""

from __future__ import annotations

import re

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

DEFAULT_COLOR_BUTTON = "#dff250"
DEFAULT_COLOR_BUTTON_TEXT = "#16181a"
DEFAULT_COLOR_BUTTON_HOVER = "#eaff6b"
DEFAULT_COLOR_FILL = "#dff250"


def normalize_hex(value: str | None, fallback: str) -> str:
    raw = (value or "").strip()
    if HEX_COLOR_RE.match(raw):
        return raw.lower()
    return fallback.lower()


def build_brand_theme_css(settings_obj) -> str:
    button = normalize_hex(
        getattr(settings_obj, "color_button", None), DEFAULT_COLOR_BUTTON
    )
    text = normalize_hex(
        getattr(settings_obj, "color_button_text", None), DEFAULT_COLOR_BUTTON_TEXT
    )
    hover = normalize_hex(
        getattr(settings_obj, "color_button_hover", None), DEFAULT_COLOR_BUTTON_HOVER
    )
    fill = normalize_hex(
        getattr(settings_obj, "color_fill", None), DEFAULT_COLOR_FILL
    )
    return (
        f"--accent-button:{button};"
        f"--accent-button-hover:{hover};"
        f"--accent-button-text:{text};"
        f"--accent-fill:{fill};"
        f"--accent:{fill};"
        f"--on-accent:{text};"
    )
