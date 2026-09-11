from django.core.management.base import BaseCommand

from landing.block_defaults import (
    BLOCK_CONTENT_TYPES,
    BLOCK_DEFAULTS,
    BLOCK_FIELD_LABELS,
    is_visibility_key,
)
from landing.hero_slides import ensure_default_hero_slides
from landing.models import (
    AdvantageItem,
    CaseItem,
    DesignFeature,
    FAQItem,
    PackageItem,
    ReviewItem,
    SiteBlock,
    SiteSettings,
    StyleItem,
)
from landing.privacy_text import ensure_privacy_html
from landing.brand_colors import BRAND_COLOR_DEFAULTS
from landing.site_content_registry import all_registry_block_keys

_LEGACY_LIME_COLORS = {
    "color_button": {"#dff250"},
    "color_button_text": set(),
    "color_button_hover": {"#eaff6b"},
    "color_fill": {"#dff250"},
    "color_accent_icon": {"#a8bc22"},
    "color_accent_text": {"#7e8f1c", "#5f6e12"},
}


def seed_site_settings() -> None:
    obj = SiteSettings.get_solo()
    updates = {}
    if not obj.phone_display:
        updates["phone_display"] = "+380 44 123 45 67"
    if not obj.phone_tel:
        updates["phone_tel"] = "+380441234567"
    if not obj.email:
        updates["email"] = "hello@kontur.plus"
    if not obj.city:
        updates["city"] = "Одеса"
    if not obj.work_hours:
        updates["work_hours"] = "Пн–Сб · 09:00–19:00"
    # Migrate old lime defaults → taupe once; do not overwrite custom admin colors.
    for key, value in BRAND_COLOR_DEFAULTS.items():
        current = (getattr(obj, key, None) or "").strip().lower()
        legacy = {c.lower() for c in _LEGACY_LIME_COLORS.get(key, set())}
        if not current or current in legacy:
            if current != value.lower():
                updates[key] = value
    if updates:
        for key, value in updates.items():
            setattr(obj, key, value)
        obj.save(update_fields=list(updates.keys()))


def _default_block_text(page: str, key: str) -> str:
    raw = BLOCK_DEFAULTS.get((page, key), "1" if is_visibility_key(key) else "")
    if page == "privacy" and key == "privacy_body":
        return ensure_privacy_html(raw)
    return raw


def seed_site_blocks() -> int:
    created = 0
    for page, key in all_registry_block_keys():
        defaults = {
            "label": BLOCK_FIELD_LABELS.get((page, key), key),
            "content_type": BLOCK_CONTENT_TYPES.get((page, key), "text"),
            "text_html": _default_block_text(page, key),
        }
        _, was_created = SiteBlock.objects.get_or_create(
            page=page, key=key, defaults=defaults
        )
        if was_created:
            created += 1

    # Upgrade plain privacy body → HTML (Vercel/old seeds stored newlines only)
    privacy = SiteBlock.objects.filter(page="privacy", key="privacy_body").first()
    if privacy and privacy.text_html:
        converted = ensure_privacy_html(privacy.text_html)
        if converted != privacy.text_html:
            privacy.text_html = converted
            privacy.save(update_fields=["text_html"])
    return created


def seed_list_items() -> dict[str, int]:
    stats = {}

    icon_by_title = {
        "Фіксована ціна за м²": "price",
        "Усе в пакеті": "package",
        "60 робочих днів": "calendar",
        "Гарантія 5 років": "shield",
        "Працюємо в Одесі": "pin",
        "Ще не визначились?": "none",
    }
    for item in AdvantageItem.objects.all():
        wanted = icon_by_title.get(item.title)
        if wanted and item.icon != wanted:
            item.icon = wanted
            item.save(update_fields=["icon"])

    if not AdvantageItem.objects.exists():
        items = [
            {
                "kind": AdvantageItem.Kind.STANDARD,
                "title": "Фіксована ціна за м²",
                "text": "Ставка й обсяг пакету фіксуються в договорі до старту — без прихованих доплат у процесі.",
                "image_static": "img/advantages/adv-fixed-price.webp",
                "image_alt": "Замір і фіксація вартості ремонту",
                "icon": "price",
                "sort_order": 0,
            },
            {
                "kind": AdvantageItem.Kind.STANDARD,
                "title": "Усе в пакеті",
                "text": "Роботи, матеріали, логістика й вивіз сміття — у складі обраного пакету, без «дрібниць окремо».",
                "image_static": "img/advantages/adv-all-in-package.webp",
                "image_alt": "Матеріали та комплектація ремонтного пакету",
                "icon": "package",
                "sort_order": 1,
            },
            {
                "kind": AdvantageItem.Kind.STANDARD,
                "title": "60 робочих днів",
                "text": "Строк комплексного ремонту квартири прописуємо в договорі після обміру.",
                "image_static": "img/advantages/adv-60-days.webp",
                "image_alt": "Ремонт квартири в процесі за графіком",
                "icon": "calendar",
                "sort_order": 2,
            },
            {
                "kind": AdvantageItem.Kind.STANDARD,
                "title": "Гарантія 5 років",
                "text": "Після здачі — гарантійний сертифікат і сервісний супровід у межах договору.",
                "image_static": "img/advantages/adv-warranty.webp",
                "image_alt": "Готовий інтер’єр після здачі об’єкта",
                "icon": "shield",
                "sort_order": 3,
            },
            {
                "kind": AdvantageItem.Kind.STANDARD,
                "title": "Працюємо в Одесі",
                "text": "Замір, супровід і здача об’єкта — локально, з зрозумілим графіком виїздів.",
                "image_static": "img/advantages/adv-odesa.webp",
                "image_alt": "Інтер’єр квартири в Одесі після ремонту",
                "icon": "pin",
                "sort_order": 4,
            },
            {
                "kind": AdvantageItem.Kind.CTA,
                "title": "Ще не визначились?",
                "text": "Кожен проєкт починається з заміру на об’єкті та фіксованої ціни в договорі — без тиску й зобов’язань.",
                "cta_label": "Дивитись усі пакети",
                "cta_href": "#packages",
                "icon": "none",
                "sort_order": 5,
            },
        ]
        for item in items:
            AdvantageItem.objects.create(**item)
        stats["advantages"] = len(items)
    else:
        stats["advantages"] = 0

    if not PackageItem.objects.exists():
        packages = [
            {
                "name": "Базовий",
                "description": "Чорнові й чистові роботи плюс ключові фінішні позиції для готової квартири.",
                "price": 460,
                "features": "\n".join(
                    [
                        "Підготовка, чорнові роботи, електрика й сантехніка",
                        "Санфаянс, натяжні стелі, двері",
                        "Шпалери, ламінат і плитка, освітлення",
                    ]
                ),
                "sort_order": 0,
            },
            {
                "name": "Оптимальний",
                "description": "Усе з «Базового» плюс кухня та інженерний комфорт для щоденного життя.",
                "price": 580,
                "badge": "Рекомендуємо",
                "is_recommended": True,
                "features": "\n".join(
                    [
                        "Усе з пакету «Базовий»",
                        "Кухня на замовлення, штори, кондиціонери",
                        "Бойлер, рушникосушка, дзеркало з LED",
                    ]
                ),
                "sort_order": 1,
            },
            {
                "name": "Максимальний",
                "description": "Розширена комплектація з технікою та меблями — заїхали й живете.",
                "price": 700,
                "features": "\n".join(
                    [
                        "Усе з пакету «Оптимальний»",
                        "Техніка: ТВ, холодильник, варильна, витяжка, духовка, пральна",
                        "Спальний гарнітур у складі пакету",
                    ]
                ),
                "sort_order": 2,
            },
        ]
        for item in packages:
            PackageItem.objects.create(**item)
        stats["packages"] = len(packages)
    else:
        stats["packages"] = 0

    if not DesignFeature.objects.exists():
        features = [
            "Робочі креслення й відомість оздоблювальних матеріалів",
            "Плани електрики, сантехніки, освітлення",
            "Підбір фінішів спільно з дизайнером і відділом постачання",
            "За потреби — 3D-візуалізація ключових зон",
        ]
        for idx, text in enumerate(features):
            DesignFeature.objects.create(text=text, sort_order=idx)
        stats["design_features"] = len(features)
    else:
        stats["design_features"] = 0

    if not StyleItem.objects.exists():
        styles = [
            {
                "title": "Лофт",
                "text": "Текстури, відкриті акценти, практичність для вторинки й сучасних планувань.",
                "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=900&q=88",
                "sort_order": 0,
            },
            {
                "title": "Мінімалізм",
                "text": "Чисті лінії, спокійна палітра, менше зайвого — більше повітря в просторі.",
                "image_url": "https://images.unsplash.com/photo-1600210492493-0946911123ea?auto=format&fit=crop&w=900&q=88",
                "sort_order": 1,
            },
            {
                "title": "Контемпорарі",
                "text": "Актуальні рішення без моди заради моди: комфорт і довговічність матеріалів.",
                "image_url": "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=900&q=88",
                "sort_order": 2,
            },
            {
                "title": "Скандинавський",
                "text": "Світло, тепло дерева й функціональні деталі для щоденного життя.",
                "image_url": "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=900&q=88",
                "sort_order": 3,
            },
        ]
        for item in styles:
            StyleItem.objects.create(**item)
        stats["styles"] = len(styles)
    else:
        stats["styles"] = 0

    if not ReviewItem.objects.exists():
        reviews = [
            {
                "text": "Ціну зафіксували в договорі. Етапи оплати збіглися з роботами — без тиску «доплатити зараз».",
                "name": "Олена К.",
                "meta": "Одеса · фіксована ціна",
                "sort_order": 0,
            },
            {
                "text": "Новобудова в Одесі: пакет «Оптимальний», строки й приймання — усе по пунктах. Рекомендую.",
                "name": "Андрій М.",
                "meta": "Одеса · Оптимальний",
                "sort_order": 1,
            },
            {
                "text": "Після поганого досвіду з іншою бригадою шукали прозорий кошторис. У Kontur+ саме так і вийшло.",
                "name": "Ірина С.",
                "meta": "Одеса · кошторис",
                "sort_order": 2,
            },
            {
                "text": "Дизайн і матеріали узгодили до старту. На об’єкті все збіглося з планом — без сюрпризів у кошторисі.",
                "name": "Марина П.",
                "meta": "Аркадія · Максимальний",
                "sort_order": 3,
            },
        ]
        for item in reviews:
            ReviewItem.objects.create(**item)
        stats["reviews"] = len(reviews)
    else:
        stats["reviews"] = 0

    if not CaseItem.objects.exists():
        cases = [
            {
                "title": "Новобудова, Одеса",
                "location": "Одеса · новобудова",
                "text": "Повний цикл від дизайн-проєкту до фінального прибирання — квартира готова до заселення.",
                "image_static": "img/cases/case-01-newbuild.webp",
                "image_alt": "Ремонт у новобудові",
                "tags": "Дизайн-проєкт\nРемонт під ключ\nКомплектація\nОптимальний",
                "sort_order": 0,
            },
            {
                "title": "Вторинне житло",
                "location": "Одеса · вторинка",
                "text": "Завдання — оновити стару квартиру. Обрали лофт: практично й добре поєднується з іншими акцентами.",
                "image_static": "img/cases/case-02-secondary.webp",
                "image_alt": "Ремонт вторинного житла",
                "tags": "Демонтаж\nЛофт\nІнженерія\nМаксимальний",
                "sort_order": 1,
            },
            {
                "title": "Під оренду · ЖК Елегія Парк",
                "location": "ЖК Елегія Парк",
                "text": "Комфортне сучасне житло з попитом на довгострокову оренду — без зайвих витрат і втрати якості.",
                "image_static": "img/cases/case-03-rent.webp",
                "image_alt": "Ремонт під оренду",
                "tags": "Базовий пакет\nСантехніка\nЕлектрика\nФініш",
                "sort_order": 2,
            },
            {
                "title": "Студія під ключ · Аркадія",
                "location": "Одеса · студія",
                "text": "Компактне планування з максимумом світла: зонування, вбудовані рішення й фініші, які тримають охайний вигляд щодня.",
                "image_static": "img/cases/case-04-studio.webp",
                "image_alt": "Студія під ключ",
                "tags": "Планування\nМінімалізм\nМеблі\nОптимальний",
                "sort_order": 3,
            },
        ]
        for item in cases:
            CaseItem.objects.create(**item)
        stats["cases"] = len(cases)
    else:
        stats["cases"] = 0

    if not FAQItem.objects.exists():
        faqs = [
            (
                "Чи справді ціна фіксована?",
                "Так — у межах обраного пакету й обсягу, зафіксованих у договорі. Зміни лише письмово, з перерахунком до виконання.",
            ),
            (
                "Що входить у пакет?",
                "Роботи, матеріали й супутні процеси (логістика, замовлення, вивіз сміття) згідно з описом пакету. Детальний склад — після заміру.",
            ),
            (
                "Скільки триває ремонт квартири?",
                "Орієнтир для комплексного пакетного ремонту — 60 робочих днів. Точний строк фіксуємо в договорі після обміру.",
            ),
            (
                "Хто обирає матеріали?",
                "Базовий склад — у пакеті та підбірках стилів. Заміну на аналоги узгоджуємо з вами до закупівлі.",
            ),
            (
                "Як працює оплата 30/30/30/10?",
                "Етапи: договір → матеріали → 75% робіт → акт. Суми видно в калькуляторі як орієнтир.",
            ),
            (
                "Яка гарантія?",
                "Гарантія на роботи — 5 років за договором. Після здачі видаємо гарантійний сертифікат і умови сервісу.",
            ),
        ]
        for idx, (q, a) in enumerate(faqs):
            FAQItem.objects.create(question=q, answer=a, sort_order=idx)
        stats["faq"] = len(faqs)
    else:
        stats["faq"] = 0

    return stats


class Command(BaseCommand):
    help = "Ідемпотентний seed CMS-контенту Kontur+"

    def handle(self, *args, **options):
        seed_site_settings()
        blocks = seed_site_blocks()
        slides = ensure_default_hero_slides()
        lists = seed_list_items()
        self.stdout.write(
            self.style.SUCCESS(
                f"OK blocks={blocks} slides={slides} lists={lists}"
            )
        )
