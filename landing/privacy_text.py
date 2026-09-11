"""Plain text ↔ HTML для політики конфіденційності (без тегів у адмінці)."""

from __future__ import annotations

import re
from html import escape, unescape
from html.parser import HTMLParser


_HEADING_RE = re.compile(r"^\d+[.)]\s+\S")


class _HTMLToPlain(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._buf: list[str] = []
        self._in_heading = False

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3"}:
            self._flush_para()
            self._in_heading = True
        elif tag == "br":
            self._buf.append("\n")
        elif tag in {"p", "div", "li"}:
            self._flush_para()

    def handle_endtag(self, tag):
        if tag in {"h1", "h2", "h3"}:
            text = "".join(self._buf).strip()
            self._buf.clear()
            self._in_heading = False
            if text:
                if self.parts:
                    self.parts.append("")
                self.parts.append(text)
                self.parts.append("")
        elif tag in {"p", "div", "li"}:
            self._flush_para()

    def handle_data(self, data):
        chunk = data.replace("\xa0", " ")
        if chunk:
            self._buf.append(chunk)

    def _flush_para(self):
        text = "".join(self._buf).strip()
        self._buf.clear()
        if not text:
            return
        if self.parts and self.parts[-1] != "":
            self.parts.append("")
        self.parts.append(text)

    def get_text(self) -> str:
        self._flush_para()
        # collapse excess blank lines
        out: list[str] = []
        blank = False
        for line in self.parts:
            if line == "":
                if not blank and out:
                    out.append("")
                    blank = True
            else:
                out.append(line)
                blank = False
        return "\n".join(out).strip()


def html_to_plain(html: str) -> str:
    raw = (html or "").strip()
    if not raw:
        return ""
    if "<" not in raw:
        return unescape(raw)
    parser = _HTMLToPlain()
    try:
        parser.feed(raw)
        parser.close()
    except Exception:
        return re.sub(r"<[^>]+>", "", raw)
    return parser.get_text()


def plain_to_html(text: str) -> str:
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return ""
    # Якщо вже HTML — лишаємо як є (захист від подвійної конвертації)
    if re.search(r"</?(p|h[1-6]|ul|ol|li|br)\b", raw, re.I):
        return raw

    blocks: list[str] = []
    para_lines: list[str] = []

    def flush_para() -> None:
        nonlocal para_lines
        if not para_lines:
            return
        body = " ".join(para_lines).strip()
        para_lines = []
        if body:
            blocks.append(f"<p>{escape(body)}</p>")

    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            flush_para()
            continue
        if _HEADING_RE.match(stripped):
            flush_para()
            blocks.append(f"<h2>{escape(stripped)}</h2>")
        else:
            para_lines.append(stripped)
    flush_para()
    return "".join(blocks)


def ensure_privacy_html(text: str) -> str:
    """Повертає HTML: якщо вже розмітка — як є, інакше plain → h2/p."""
    raw = (text or "").strip()
    if not raw:
        return ""
    if re.search(r"</?(p|h[1-6]|ul|ol|li|br)\b", raw, re.I):
        return raw
    return plain_to_html(raw)


PRIVACY_BODY_HELP = (
    "Пишіть звичайним текстом без тегів. "
    "Заголовок розділу — окремим рядком, наприклад: «1. Оператор даних». "
    "Абзаци розділяйте порожнім рядком."
)

PRIVACY_BODY_PLAIN_DEFAULT = """Спрощена сторінка-каркас. Повний юридичний текст можна відредагувати тут.

1. Оператор даних
Kontur+ (ремонтна організація). Контакт: телефон на сайті.

2. Які дані збираємо
Ім’я, номер телефону, контекст заявки (пакет, параметри розрахунку), технічні дані запиту.

3. Мета обробки
Зв’язок щодо ремонту, підготовка кошторису, покращення сервісу.

4. Зберігання та права
Дані зберігаються стільки, скільки потрібно для обробки звернення. Ви можете запитати доступ, виправлення або видалення."""
