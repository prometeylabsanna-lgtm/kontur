# Kontur+ — Design System & Landing Spec

**Версія:** 2.0 · Mobile First · UA · Landing v2  
**Стиль:** lime / cream / pill · editorial service landing  
**Зона робіт:** Одеса  
**Бренд:** Kontur+

---

## 1) Design Read

Власники квартир в Одесі, які шукають підрядника «під ключ» з фіксованою ціною за м²: сучасний сервісний лендінг — warm cream, графіт, lime CTA, чітка ієрархія без маркетингового крику.

---

## 2) Dials + Palette

| Dial | Value |
|------|-------|
| DESIGN_VARIANCE | 6–7 |
| MOTION_INTENSITY | 3–4 |
| VISUAL_DENSITY | 2–3 |

### Color tokens

| Token | Hex | Role |
|-------|-----|------|
| `--canvas` | `#F7F6F4` | Основний фон (warm cream) |
| `--surface` | `#FFFFFF` | Білі секції / панелі |
| `--surface-soft` | `#EAE6E0` | Калькулятор / soft sections |
| `--ink` | `#16181A` | Текст / dark panels |
| `--muted` | `#6B6560` | Secondary copy |
| `--border` | `#DCD8D2` | Hairlines / grids |
| `--accent` | `#DFF250` | Primary CTA (lime) |
| `--accent-hover` | `#EAFF6B` | Hover CTA |
| `--accent-mark` | `#A8BC22` | List marks / stars |
| `--accent-deep` | `#7E8F1C` | Indexes / eyebrows |
| `--accent-link` | `#5F6E12` | Links |

**Accent rationale:** lime на dark/cream — високий контраст CTA без SaaS-blue і без terracotta.

---

## 3) Typography

**Stack**

- UI: `Outfit` 300–600  
- Mono / numbers: `Space Grotesk` 500/700  

**Scale**

| Role | Value |
|------|-------|
| Brand | clamp 19–22px / 600 |
| Hero H1 | clamp(34px, 5.6vw, 78px) / 500 |
| Section H2 | clamp(28px, 3.2vw, 46px) / 500 |
| Body | 16–17px / 400 |

---

## 4) Component rules

### Button
- Primary: bg `--accent`, text `--ink`, radius 10px, h ≥ 50px  
- Header tel: pill 999px, lime  
- Ghost: border `--border`, hover mark  
- Dark: bg `--ink`, text cream  

### Header
- Fixed overlay · dark glass pill bar · safe-area top  
- Mobile: brand + lime tel icon + burger  
- Desktop: nav pills + lime tel  

### Card (packages)
- Hairline grid (1px `--border`)  
- Recommended: dark panel + lime price  

### Modal
- Overlay dark 52% · panel cream/white · radius 12px  

---

## 5) Sections (sitemap без змін)

Порядок: `#hero` → `#advantages` → `#packages` → `#design` → `#styles` → `#calculator` → `#proof` → `#faq` → `#contacts`

Hero: full-bleed slider (3 кадри), scrim, trust metrics, dots.  
Advantages: numbered rows + «Дивитись пакети».  
Packages: 460 / **580** / 700.  
Design + Styles: окремі секції (sitemap).  
Calculator: white inputs + dark sum panel.  
Proof / FAQ / Footer: як у мокапі.

---

## 6) Макетні артефакти

| Файл | Viewport |
|------|----------|
| `mockups/landing.html` | Responsive source of truth |
| `mockups/artboards.html` | 390 / 768 / 1440 frames |
| `mockups/modals.html` | Form states |
| `mockups/privacy.html` | /privacy |
| `css/*` + `js/landing.js` | Tokens + UI + logic |

Фото: Unsplash (вільне ліцензування), висока якість, по сенсу блоків.

---

## 7) Anti-slop

Уникати: Inter/Roboto, purple gradients, terracotta cream-кліше, emoji, floating badges на hero, окремої thank-you page.

---

## 8) Rationale

Дорого виглядає через повітря, lime-акцент на графіті, Space Grotesk для цифр і відсутність декоративного шуму.
