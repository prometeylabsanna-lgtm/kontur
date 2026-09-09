# Kontur+ — Design System & Landing Spec

**Версія:** 1.1 · Mobile First · UA  
**Стиль:** premium utilitarian minimalism / editorial service landing  
**Зона робіт:** Одеса  
**Бренд:** Kontur+

---

## 1) Design Read

Власники квартир в Одесі, які шукають підрядника «під ключ» з фіксованою ціною за м²: атмосфера архітектурної студії й якісного сервісу — стримана сталь, повітря, довіра без маркетингового крику.

---

## 2) Dials + Palette

| Dial | Value |
|------|-------|
| DESIGN_VARIANCE | 5–6 |
| MOTION_INTENSITY | 3–4 |
| VISUAL_DENSITY | 2–3 |

### Color tokens

| Token | Hex | Role |
|-------|-----|------|
| `--canvas` | `#F3F5F7` | Основний фон сторінки (cool mist) |
| `--surface` | `#FFFFFF` | Картки взаємодії, модал, header |
| `--surface-soft` | `#E8ECF0` | Чергування секцій, calc panel inset |
| `--ink` | `#1C2229` | Основний текст (off-black / charcoal) |
| `--muted` | `#5E6874` | Secondary copy, дескриптор, meta |
| `--border` | `#D0D6DE` | Роздільники, інпути, FAQ lines |
| `--accent` | `#4A6478` | Primary CTA / focus (slate-steel, sat. < 80%) |
| `--accent-hover` | `#3A5162` | Hover CTA |
| `--success` | `#2E6B52` | Успіх форми |
| `--error` | `#A13D3D` | Валідація |

**Accent rationale:** приглушений steel — професійний cool-тон без «SaaS-blue» і без теплого terracotta-кліше.

---

## 3) Typography

**Stack**

- Display / UI: `Outfit` (grotesque), fallbacks: `Geist`, `Helvetica Neue`, sans-serif  
- Body: той самий `Outfit` (ваги 400/500), line-height 1.6–1.65, max-width ~65ch

**Scale (Mobile First → clamp)**

| Role | Mobile | Desktop (clamp) |
|------|--------|-----------------|
| Brand wordmark | 28–32px / 600 | 40–48px |
| Hero H1 | 32px / 600 | clamp(40px, 4vw, 56px) |
| Section H2 | 26px / 600 | clamp(28px, 2.5vw, 36px) |
| Card title | 18–20px / 600 | 20–22px |
| Body | 16px / 400 | 16–17px |
| Caption / meta | 13–14px / 400 | 13–14px |
| Price display | 28px / 600 | 32–36px |

- `text-wrap: balance` на заголовках  
- Display tracking: `−0.02em` … `−0.03em` (не тісніше −0.04em)  
- Letter-spacing body: 0

### Hero copy (затверджений варіант)

- **Бренд:** Kontur+  
- **Дескриптор:** ремонтна організація  
- **H1:** Готові пакети ремонту з фіксованою ціною за м²  
- **Supporting:** Kontur+ в Одесі — повний цикл під ключ: дизайн, матеріали, роботи й здача за 60 робочих днів.  
- **Trust:** Фіксована ціна · 60 днів · Гарантія 5 років

**Альтернативи (CMS):**
1. Ремонт під ключ в Одесі — фіксована ціна і строк у договорі  
2. Три пакети: Базовий, Оптимальний, Максимальний — без сюрпризів у кошторисі

---

## 4) Component rules

### Button
- Primary: bg `--accent`, text white, h ≥ 48px (touch), radius 2px (майже прямо), padding 14px 22px, font 500 15–16px  
- Secondary / ghost: transparent, border 1px `--border`, text `--ink`  
- Tel link: muted text, underline on hover only  
- Не pill; не glow; не градієнт

### Input
- h ≥ 48px, border 1px `--border`, bg `--surface`, radius 2px  
- Focus: border `--accent`, outline 2px `--accent` @ 20% opacity  
- Error: border `--error` + caption 13px  
- Label над полем, 13px `--muted`

### Card (лише interaction)
- Пакети / кейси / calc: `--surface`, border 1px `--border`, shadow none або дуже м’який `0 1px 0 rgba(28,34,41,0.04)`  
- Recommended (Оптимальний): border `--accent` 1.5px + тонкий label «Рекомендуємо» текстом 12px `--accent` — без бейджа-стікера  
- Якщо border можна зняти без втрати сенсу — знімаємо (переваги, FAQ)

### Accordion
- Рядки з 1px `--border` top/bottom  
- Chevron / «+» 20px stroke, rotate 45° when open  
- Один відкритий; padding 18–22px 0; без card chrome

### Modal
- Overlay: `rgba(28,34,41,0.48)`  
- Panel: max 420px, `--surface`, padding 28–32px, radius 4px  
- Safe-area padding на mobile; close 44×44  
- Стани: default / error / loading / success — той самий контейнер

### Header sticky (scrolled)
- bg `--surface` @ 92% + blur 12px  
- border-bottom 1px `--border`  
- Висота: 64px mobile / 72px desktop; `padding-top: env(safe-area-inset-top)`

---

## 5) Section-by-section (mobile → desktop)

### Sticky Header
- **390:** logo Kontur+ + дескриптор в 1 рядок (дескриптор 11–12px) | tel icon / CTA 44px | burger  
- Menu: full-screen sheet, якорі + CTA  
- **768+:** горизонтальні якорі (Переваги / Пакети / Дизайн / Стилі / Розрахунок / Роботи / FAQ)  
- **1440:** wordmark + дескриптор зліва; nav center-left; tel + CTA справа

### #hero
- Full-bleed фото процесу ремонту (бригада / деталі), `object-fit: cover`, filter: saturate(0.72) contrast(1.05)  
- Gradient scrim знизу/ліворуч для читабельності тексту (не бейджі)  
- Контент: brand → H1 → supporting → CTA group  
- Під CTA або одразу під секцією 1 рядок trust: «Фіксована ціна · 60 днів · Гарантія 5 років»  
- **Desktop:** текст у лівій третині/половині поверх full-bleed; без inset card

### #advantages
- 5 тез, stroke-іконки 24px, колір `--ink` / `--muted`  
- **Mobile:** вертикальний список, іконка зліва, без коробочок  
- **Desktop:** асиметрична 2-col zig-zag (не 3 рівні feature cards)

Тези:
1. Фіксована ціна за м² до старту робіт  
2. Повний склад робіт і матеріалів у пакеті  
3. 60 робочих днів у договорі  
4. Гарантія 5 років  
5. Робота в Одесі

### #packages
- 3 пакети: Базовий 460$ / **Оптимальний 580$** (рекомендований) / Максимальний 700$  
- Склад карток узгоджений з пакетною моделлю (Базовий → Оптимальний → Максимальний)  
- Ціна як editable-looking: великий numeric + «$/м²» muted caption (CMS-відчуття)  
- **Mobile:** stack  
- **Desktop:** 3 col; Оптимальний — accent border

### #design
- Одна колонка тексту + список складу проєкту + CTA  
- **Desktop:** feature-split 50/50 текст | full-bleed фото (не card)

### #styles
- 4 стилі: лофт / мінімалізм / контемпорарі / скандинавський  
- Список з hairline-роздільниками (не cards)  
- CTA «Отримати підбір матеріалів»  
- **Mobile:** 1 col → **768:** 2 col → **1024:** 4 col

### #calculator
- Панель `--surface` на `--surface-soft` секції  
- Segmented: тип об’єкта; select/radio пакети; slider 20–150 + numeric  
- Output: велика сума; breakdown 30/30/30/10  
- Будинок: текст «індивідуальний кошторис» + CTA без автосуми  
- CTA: «Отримати точний розрахунок»
- Default пакет у калькуляторі: Оптимальний 580 $/м²

### #proof
- Google rating row (зірки текстом/SVG, не emoji)  
- Reviews: horizontal snap carousel  
- Cases: photo + локація/тип + пакет + короткий опис; 1 col → 2–3 col  
- Кейси: новобудова, вторинка (лофт), під оренду

### #faq
- 6 питань; акордеон; max-width ~720px center на desktop  
- Строк 60 днів, гарантія 5 років — у відповідях

### Footer / #contacts
- Тел, Одеса, графік, CTA, /privacy, юр. рядок

### Modal states
- Default / validation / loading / success (відповідь до 30 хв у робочий час)

---

## 6) Макетні артефакти

| Файл | Viewport |
|------|----------|
| `mockups/landing.html` | Responsive source of truth |
| `mockups/artboards.html` | 390 / 768 / 1440 frames |
| `mockups/modals.html` | Form states |
| `mockups/privacy.html` | Спрощений /privacy |
| `css/tokens.css` … `motion.css` | Токени + компоненти + секції |

Open Design daemon (`OD_DAEMON_URL`) зараз недоступний — HTML/CSS лежать локально в `design/` і готові до імпорту після старту daemon.

---

## 7) Anti-slop self-check

Свідомо уникав:
- Inter / Roboto / Arial / system як «преміум»
- Purple / indigo / neon gradients
- Cream #F4F1EA + terracotta
- Pure #000
- Emoji, scroll chevrons, floating badges
- 3 рівні feature-cards як головний патерн переваг
- Nested cards, side-stripes, gradient text
- Pill clusters, stat strips
- Marble / gold / serif luxury
- Cards у hero; promo stickers на медіа

---

## 8) Rationale

Дорого виглядає через повітря, чітку ієрархію, один steel-акцент і відсутність декоративного шуму: інтерфейс як інструмент підрядника, а не як банер нерухомості.
