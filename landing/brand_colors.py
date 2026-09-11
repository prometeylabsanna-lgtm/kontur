from __future__ import annotations

import re

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

DEFAULT_COLOR_BUTTON = "#b1a091"
DEFAULT_COLOR_BUTTON_TEXT = "#16181a"
DEFAULT_COLOR_BUTTON_HOVER = "#b0a091"
DEFAULT_COLOR_FILL = "#b0a091"
DEFAULT_COLOR_ACCENT_ICON = "#b19d91"
DEFAULT_COLOR_ACCENT_TEXT = "#806252"
# Поточний taupe «K+» у static/img/favicon.png
DEFAULT_COLOR_FAVICON = "#92817c"

BRAND_COLOR_DEFAULTS = {
    "color_button": DEFAULT_COLOR_BUTTON,
    "color_button_text": DEFAULT_COLOR_BUTTON_TEXT,
    "color_button_hover": DEFAULT_COLOR_BUTTON_HOVER,
    "color_fill": DEFAULT_COLOR_FILL,
    "color_accent_icon": DEFAULT_COLOR_ACCENT_ICON,
    "color_accent_text": DEFAULT_COLOR_ACCENT_TEXT,
    "color_favicon": DEFAULT_COLOR_FAVICON,
}


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
    icon = normalize_hex(
        getattr(settings_obj, "color_accent_icon", None), DEFAULT_COLOR_ACCENT_ICON
    )
    accent_text = normalize_hex(
        getattr(settings_obj, "color_accent_text", None), DEFAULT_COLOR_ACCENT_TEXT
    )
    favicon = normalize_hex(
        getattr(settings_obj, "color_favicon", None), DEFAULT_COLOR_FAVICON
    )
    return (
        f"--accent-button:{button};"
        f"--accent-button-hover:{hover};"
        f"--accent-button-text:{text};"
        f"--accent-fill:{fill};"
        f"--accent:{fill};"
        f"--on-accent:{text};"
        f"--accent-mark:{icon};"
        f"--accent-deep:{accent_text};"
        f"--accent-link:{accent_text};"
        f"--accent-hover:{hover};"
        f"--favicon-mark:{favicon};"
    )
