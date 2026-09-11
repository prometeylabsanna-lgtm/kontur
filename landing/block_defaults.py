from __future__ import annotations

BLOCK_CONTENT_TYPES: dict[tuple[str, str], str] = {}
BLOCK_FIELD_LABELS: dict[tuple[str, str], str] = {}
BLOCK_DEFAULTS: dict[tuple[str, str], str] = {}
INLINE_KEYS: frozenset[str] = frozenset()
MULTILINE_KEYS: frozenset[str] = frozenset()

_INLINE: set[str] = set()
_MULTI: set[str] = set()


def _reg(
    page: str,
    key: str,
    *,
    label: str,
    default: str = "",
    content_type: str = "text",
    inline: bool = False,
    multiline: bool = False,
) -> None:
    pair = (page, key)
    BLOCK_CONTENT_TYPES[pair] = content_type
    BLOCK_FIELD_LABELS[pair] = label
    BLOCK_DEFAULTS[pair] = default
    if inline:
        _INLINE.add(key)
    if multiline:
        _MULTI.add(key)


def is_visibility_key(key: str) -> bool:
    return key.endswith("_visible")


def is_inline_key(key: str) -> bool:
    return key in INLINE_KEYS


def is_multiline_key(key: str) -> bool:
    return key in MULTILINE_KEYS


# --- site / header ---
_reg("site", "header_brand_name", label="Назва бренду", default="Kontur+", inline=True)
_reg(
    "site",
    "header_brand_desc",
    label="Підпис бренду",
    default="ремонтна організація",
    inline=True,
)
_reg(
    "site",
    "header_cta_label",
    label="Текст кнопки",
    default="Замовити дзвінок",
    inline=True,
)
_reg("site", "header_cta_visible", label="Показувати кнопку", default="1")
_reg("site", "header_phone_visible", label="Показувати телефон", default="1")

# --- home / hero ---
_reg("home", "hero_section_visible", label="Показувати секцію", default="1")
_reg(
    "home",
    "hero_title",
    label="Заголовок",
    default="Готові пакети ремонту з фіксованою ціною за м²",
    multiline=True,
)
_reg(
    "home",
    "hero_lead",
    label="Короткий опис",
    default=(
        "Повний цикл під ключ: дизайн, матеріали, роботи й здача за 60 робочих днів. "
        "Ставка й строк — у договорі до старту."
    ),
    multiline=True,
)
_reg(
    "home",
    "hero_cta_primary",
    label="Текст головної кнопки",
    default="Замовити дзвінок",
    inline=True,
)
_reg(
    "home",
    "hero_cta_secondary",
    label="Текст другої кнопки",
    default="Порахувати вартість",
    inline=True,
)
_reg("home", "hero_cta_secondary_url", label="Куди веде друга кнопка", default="#calculator", inline=True)
_reg("home", "hero_trust_1", label="Перевага внизу 1", default="460$/м² від", inline=True)
_reg("home", "hero_trust_2", label="Перевага внизу 2", default="60робочих днів", inline=True)
_reg("home", "hero_trust_3", label="Перевага внизу 3", default="5років гарантії", inline=True)

# --- advantages ---
_reg("home", "advantages_section_visible", label="Показувати секцію", default="1")

# --- packages ---
_reg("home", "packages_section_visible", label="Показувати секцію", default="1")
_reg(
    "home",
    "packages_title",
    label="Заголовок",
    default="Три пакети — один рівень контролю",
    multiline=True,
)
_reg(
    "home",
    "packages_lead",
    label="Короткий опис",
    default=(
        "Ціна за м² і строк фіксуються в договорі. «Оптимальний» — баланс складу, "
        "комфорту й бюджету."
    ),
    multiline=True,
)
_reg(
    "home",
    "packages_bg_image",
    label="Фон секції",
    default="",
    content_type="image",
)
_reg(
    "home",
    "packages_bg_url",
    label="Посилання на фон (якщо немає файлу)",
    default=(
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c"
        "?auto=format&fit=crop&w=1280&q=78"
    ),
    inline=True,
)

# --- design ---
_reg("home", "design_section_visible", label="Показувати секцію", default="1")
_reg(
    "home",
    "design_title",
    label="Заголовок",
    default="Дизайн-проєкт під ваш ритм життя",
    multiline=True,
)
_reg(
    "home",
    "design_lead",
    label="Короткий опис",
    default=(
        "Проєкт Kontur+ — стиль і зручність: планування, матеріали й деталі "
        "з урахуванням звичок і сценаріїв у квартирі."
    ),
    multiline=True,
)
_reg(
    "home",
    "design_cta_label",
    label="Текст кнопки",
    default="Замовити проєкт",
    inline=True,
)
_reg("home", "design_image_1", label="Фото 1", default="", content_type="image")
_reg("home", "design_image_2", label="Фото 2", default="", content_type="image")
_reg(
    "home",
    "design_image_1_url",
    label="Посилання на фото 1",
    default=(
        "https://images.unsplash.com/photo-1503387762-592deb58ef4e"
        "?auto=format&fit=crop&w=640&q=78"
    ),
    inline=True,
)
_reg(
    "home",
    "design_image_2_url",
    label="Посилання на фото 2",
    default=(
        "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6"
        "?auto=format&fit=crop&w=640&q=78"
    ),
    inline=True,
)

# --- styles ---
_reg("home", "styles_section_visible", label="Показувати секцію", default="1")
_reg(
    "home",
    "styles_title",
    label="Заголовок",
    default="Чотири стилі з підбором фінішів",
    multiline=True,
)
_reg(
    "home",
    "styles_lead",
    label="Короткий опис",
    default=(
        "Дизайн і постачання зібрали фінішні матеріали з кращим співвідношенням "
        "ціна–якість у чотирьох напрямках."
    ),
    multiline=True,
)
_reg(
    "home",
    "styles_cta_label",
    label="Текст кнопки",
    default="Отримати підбір матеріалів",
    inline=True,
)

# --- calculator ---
_reg("home", "calculator_section_visible", label="Показувати секцію", default="1")
_reg(
    "home",
    "calculator_title",
    label="Заголовок",
    default="Орієнтовна вартість за 30 секунд",
    multiline=True,
)
_reg(
    "home",
    "calculator_lead",
    label="Короткий опис",
    default=(
        "Для квартири в новобудові — миттєвий орієнтир із графіком оплат. "
        "Для будинку — індивідуальний кошторис після виїзду."
    ),
    multiline=True,
)
_reg(
    "home",
    "calculator_cta_label",
    label="Текст кнопки",
    default="Отримати точний розрахунок",
    inline=True,
)
_reg(
    "home",
    "calculator_note",
    label="Примітка під сумою",
    default="Розрахунок за формулою пакету. Точна ціна — після безкоштовного заміру.",
    multiline=True,
)

# --- proof ---
_reg("home", "proof_section_visible", label="Показувати секцію", default="1")
_reg("home", "proof_title", label="Заголовок", default="Відгуки та кейси", inline=True)
_reg("home", "proof_reviews_badge", label="Підпис над відгуками", default="Відгуки", inline=True)
_reg(
    "home",
    "proof_cases_did_label",
    label="Підпис «Що зробили»",
    default="Що зробили",
    inline=True,
)
_reg(
    "home",
    "proof_reviews_empty",
    label="Текст, якщо немає відгуків",
    default="Відгуки з’являться незабаром. Поки що можете переглянути рейтинг або залишити заявку.",
    multiline=True,
)

# --- faq ---
_reg("home", "faq_section_visible", label="Показувати секцію", default="1")
_reg("home", "faq_badge", label="Підпис над питаннями", default="Питання", inline=True)
_reg("home", "faq_title", label="Заголовок", default="Питання до старту", inline=True)
_reg("home", "faq_image_1", label="Фото 1", default="", content_type="image")
_reg("home", "faq_image_2", label="Фото 2", default="", content_type="image")
_reg(
    "home",
    "faq_image_1_static",
    label="Запасне фото 1 (шлях у сайті)",
    default="img/advantages/adv-odesa.jpg",
    inline=True,
)
_reg(
    "home",
    "faq_image_2_static",
    label="Запасне фото 2 (шлях у сайті)",
    default="img/advantages/adv-warranty.webp",
    inline=True,
)

# --- footer ---
_reg(
    "site",
    "footer_tagline",
    label="Слоган",
    default="Ремонт під ключ в Одесі з фіксованою ціною за м².",
    multiline=True,
)
_reg(
    "site",
    "footer_cta_label",
    label="Текст кнопки",
    default="Замовити дзвінок",
    inline=True,
)
_reg("site", "footer_menu_title", label="Заголовок меню", default="Меню", inline=True)
_reg(
    "site",
    "footer_services_title",
    label="Заголовок послуг",
    default="Послуги",
    inline=True,
)
_reg(
    "site",
    "footer_contacts_title",
    label="Заголовок контактів",
    default="Контакти",
    inline=True,
)
_reg(
    "site",
    "footer_legal",
    label="Юридичний рядок",
    default="© 2026 Kontur+. Усі права захищено.",
    multiline=True,
)
_reg(
    "site",
    "footer_service_1",
    label="Послуга 1",
    default="Ремонт під ключ",
    inline=True,
)
_reg(
    "site",
    "footer_service_2",
    label="Послуга 2",
    default="Дизайн-проєкт",
    inline=True,
)
_reg(
    "site",
    "footer_service_3",
    label="Послуга 3",
    default="Комплектація матеріалів",
    inline=True,
)
_reg("site", "footer_cta_visible", label="Показувати кнопку", default="1")
_reg("site", "footer_socials_visible", label="Показувати соцмережі", default="1")

# --- modal ---
_reg("site", "modal_title", label="Заголовок форми", default="Замовити дзвінок", inline=True)
_reg(
    "site",
    "modal_sub",
    label="Підзаголовок",
    default="Залиште контакти — передзвонимо в робочий час.",
    multiline=True,
)
_reg(
    "site",
    "modal_submit",
    label="Кнопка відправки",
    default="Надіслати",
    inline=True,
)
_reg(
    "site",
    "modal_success_title",
    label="Заголовок успіху",
    default="Дякуємо",
    inline=True,
)
_reg(
    "site",
    "modal_success_sub",
    label="Текст успіху",
    default="Заявку отримано. Очікуйте дзвінок протягом 30 хвилин у робочий час.",
    multiline=True,
)
_reg(
    "site",
    "modal_success_close",
    label="Кнопка закриття",
    default="Закрити",
    inline=True,
)

# --- privacy ---
_reg(
    "privacy",
    "privacy_title",
    label="Заголовок",
    default="Політика конфіденційності",
    inline=True,
)
_reg(
    "privacy",
    "privacy_body",
    label="Текст сторінки",
    default=(
        "Ця Політика конфіденційності пояснює, які персональні дані збирає Kontur+ "
        "(ремонтна організація) через сайт і форму заявки, з якою метою їх обробляє "
        "та які права має користувач. Користуючись сайтом і залишаючи заявку, ви "
        "підтверджуєте, що ознайомлені з цією Політикою.\n\n"
        "1. Оператор даних\n"
        "Оператором персональних даних є Kontur+ — ремонтна організація, що надає "
        "послуги ремонту під ключ, дизайн-проєкту та комплектації матеріалів в Одесі "
        "та області. З питань обробки даних звертайтесь за телефоном або електронною "
        "поштою, зазначеними в розділі «Контакти» на сайті.\n\n"
        "2. Які дані ми збираємо\n"
        "Через форму «Замовити дзвінок» та інші форми на сайті ми можемо отримувати: "
        "ім’я; номер телефону; контекст звернення; обраний пакет ремонту; тип об’єкта "
        "та площу; параметри орієнтовного розрахунку; інші відомості, які ви "
        "добровільно вкажете. Також можуть збиратися технічні дані запиту "
        "(IP-адреса, браузер, UTM-мітки).\n\n"
        "3. Мета та підстави обробки\n"
        "Дані обробляємо, щоб зв’язатися щодо заявки, підготувати кошторис і "
        "пропозицію, узгодити замір, виконати договірні зобов’язання та покращувати "
        "сервіс. Підстава — ваша згода та/або заходи до укладення договору на ваш запит.\n\n"
        "4. Кому можуть передаватися дані\n"
        "Доступ мають уповноважені співробітники Kontur+ і технічні підрядники "
        "(хостинг, пошта, CRM) за дорученням. Ми не продаємо персональні дані і не "
        "передаємо їх для стороннього маркетингу.\n\n"
        "5. Строк зберігання\n"
        "Дані зберігаються стільки, скільки потрібно для звернення та співпраці, "
        "або довше — лише за вимогами законодавства. Після цього дані знеособлюються "
        "або видаляються.\n\n"
        "6. Захист даних\n"
        "Застосовуємо організаційні та технічні заходи захисту (обмеження доступу, "
        "HTTPS, контроль облікових записів). Повна безпека передачі через інтернет "
        "не гарантується.\n\n"
        "7. Ваші права\n"
        "Ви можете дізнатися про обробку своїх даних, вимагати уточнення чи "
        "видалення, відкликати згоду та звернутися до уповноваженого органу. "
        "Запити надсилайте за контактами на сайті.\n\n"
        "8. Файли cookie та аналітика\n"
        "Сайт може використовувати технічні cookie та сервіси статистики. "
        "Cookie можна обмежити в браузері.\n\n"
        "9. Зміни Політики\n"
        "Актуальна версія завжди на цій сторінці. Дата оновлення: вересень 2026 року.\n\n"
        "10. Контакти\n"
        "Kontur+, Одеса. Телефон, пошта та години роботи — у блоці «Контакти» "
        "на головній сторінці сайту."
    ),
    multiline=True,
)

INLINE_KEYS = frozenset(_INLINE)
MULTILINE_KEYS = frozenset(_MULTI)
