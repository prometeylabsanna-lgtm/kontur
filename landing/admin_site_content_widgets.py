from __future__ import annotations

from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget

try:
    from unfold.widgets import INPUT_CLASSES, TEXTAREA_CLASSES
except Exception:  # pragma: no cover
    INPUT_CLASSES = [
        "border",
        "border-base-200",
        "bg-white",
        "font-medium",
        "rounded-default",
        "shadow-sm",
        "text-font-default-light",
        "text-sm",
        "focus:outline-2",
        "focus:-outline-offset-2",
        "focus:outline-primary-600",
        "group-[.errors]:border-red-600",
        "dark:border-base-700",
        "dark:bg-base-900",
        "dark:text-font-default-dark",
        "dark:group-[.errors]:border-red-500",
        "dark:focus:outline-primary-500",
        "px-3",
        "py-2",
        "w-full",
        "max-w-2xl",
    ]
    TEXTAREA_CLASSES = list(INPUT_CLASSES)


# Прибираємо конфліктні класи; далі ставимо theme-aware набір
_SKIP_CLASSES = frozenset(
    {
        "bg-white",
        "bg-base-900",
        "text-font-default-light",
        "text-font-default-dark",
        "text-base-100",
        "text-base-900",
        "border-base-200",
        "border-base-700",
        "dark:bg-base-900",
        "dark:bg-white",
        "dark:border-base-700",
        "dark:border-base-200",
        "dark:text-font-default-dark",
        "dark:text-font-default-light",
        "dark:text-base-100",
        "dark:text-base-900",
    }
)

# Світла тема: білий фон + темний текст; темна: темний фон + світлий текст
_FORCE_CLASSES = (
    "bg-white",
    "text-base-900",
    "border-base-200",
    "placeholder-base-400",
    "dark:bg-base-900",
    "dark:text-base-100",
    "dark:border-base-700",
    "dark:placeholder-base-400",
)


def cms_control_classes(base_classes) -> list[str]:
    cleaned = [cls for cls in list(base_classes) if cls not in _SKIP_CLASSES]
    for cls in _FORCE_CLASSES:
        if cls not in cleaned:
            cleaned.append(cls)
    return cleaned


class CmsAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        classes = cms_control_classes(INPUT_CLASSES)
        existing = attrs.get("class", "")
        attrs["class"] = f"{' '.join(classes)} {existing}".strip()
        super().__init__(attrs=attrs)


class CmsAdminTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        classes = cms_control_classes(TEXTAREA_CLASSES)
        existing = attrs.get("class", "")
        attrs["class"] = f"{' '.join(classes)} {existing}".strip()
        if "rows" not in attrs:
            attrs["rows"] = 3
        super().__init__(attrs=attrs)


def apply_readable_widget(widget) -> None:
    from django.forms.widgets import CheckboxInput, FileInput, Select

    if isinstance(widget, (CheckboxInput, FileInput, Select)):
        return
    name = widget.__class__.__name__
    if "TinyMCE" in name or "Select" in name:
        return
    if isinstance(widget, AdminTextareaWidget) or widget.__class__.__name__.endswith(
        "Textarea"
    ):
        widget.attrs["class"] = " ".join(
            cms_control_classes(
                (widget.attrs.get("class") or "").split() or TEXTAREA_CLASSES
            )
        )
        return
    if isinstance(widget, AdminTextInputWidget) or "TextInput" in name:
        widget.attrs["class"] = " ".join(
            cms_control_classes(
                (widget.attrs.get("class") or "").split() or INPUT_CLASSES
            )
        )
