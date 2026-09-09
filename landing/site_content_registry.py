from __future__ import annotations

from dataclasses import dataclass, field

from django.urls import reverse_lazy

from .block_defaults import BLOCK_FIELD_LABELS


@dataclass(frozen=True)
class FieldGroup:
    title: str
    keys: tuple[str, ...]
    description: str = ""


@dataclass(frozen=True)
class ContentSection:
    slug: str
    page_slug: str
    title: str
    blocks: tuple[tuple[str, str], ...]
    sidebar_title: str = ""
    sidebar_icon: str = "edit_note"
    preview_url: str = "/"
    description: str = ""
    visibility_key: str = ""
    field_groups: tuple[FieldGroup, ...] = ()
    admin_model_name: str = ""
    list_hint: str = ""


def _b(page: str, *keys: str) -> tuple[tuple[str, str], ...]:
    return tuple((page, key) for key in keys)


CONTENT_SECTIONS: tuple[ContentSection, ...] = (
    ContentSection(
        slug="header",
        page_slug="site",
        title="Шапка сайту",
        sidebar_title="Шапка",
        sidebar_icon="web",
        preview_url="/#hero",
        description="Бренд, кнопка дзвінка та видимість телефону в шапці.",
        admin_model_name="siteheadersettings",
        blocks=_b(
            "site",
            "header_brand_name",
            "header_brand_desc",
            "header_cta_label",
            "header_cta_visible",
            "header_phone_visible",
        ),
        field_groups=(
            FieldGroup("Бренд", ("header_brand_name", "header_brand_desc")),
            FieldGroup(
                "Дії",
                ("header_cta_label", "header_cta_visible", "header_phone_visible"),
            ),
        ),
    ),
    ContentSection(
        slug="hero",
        page_slug="home",
        title="Головний банер",
        sidebar_title="Головний банер",
        sidebar_icon="image",
        preview_url="/#hero",
        description="Тексти банера та фото каруселі — усе на цій сторінці.",
        visibility_key="hero_section_visible",
        admin_model_name="homeherosettings",
        blocks=_b(
            "home",
            "hero_section_visible",
            "hero_title",
            "hero_lead",
            "hero_cta_primary",
            "hero_cta_secondary",
            "hero_cta_secondary_url",
            "hero_trust_1",
            "hero_trust_2",
            "hero_trust_3",
        ),
        field_groups=(
            FieldGroup("Тексти", ("hero_title", "hero_lead")),
            FieldGroup(
                "Кнопки",
                ("hero_cta_primary", "hero_cta_secondary", "hero_cta_secondary_url"),
            ),
            FieldGroup("Переваги внизу банера", ("hero_trust_1", "hero_trust_2", "hero_trust_3")),
        ),
    ),
    ContentSection(
        slug="advantages",
        page_slug="home",
        title="Переваги",
        sidebar_title="Переваги",
        sidebar_icon="star",
        preview_url="/#advantages",
        description="Увімкніть секцію та редагуйте картки переваг нижче: текст, іконка, фото.",
        visibility_key="advantages_section_visible",
        admin_model_name="homeadvantagessettings",
        blocks=_b("home", "advantages_section_visible"),
        field_groups=(),
    ),
    ContentSection(
        slug="packages",
        page_slug="home",
        title="Пакети",
        sidebar_title="Пакети",
        sidebar_icon="inventory_2",
        preview_url="/#packages",
        description="Заголовки, фон і картки пакетів — усе на цій сторінці.",
        visibility_key="packages_section_visible",
        admin_model_name="homepackagessettings",
        blocks=_b(
            "home",
            "packages_section_visible",
            "packages_title",
            "packages_lead",
            "packages_bg_image",
            "packages_bg_url",
        ),
        field_groups=(
            FieldGroup("Тексти", ("packages_title", "packages_lead")),
            FieldGroup("Фон", ("packages_bg_image", "packages_bg_url")),
        ),
    ),
    ContentSection(
        slug="design",
        page_slug="home",
        title="Дизайн",
        sidebar_title="Дизайн",
        sidebar_icon="palette",
        preview_url="/#design",
        description="Тексти, фото, кнопка та пункти списку — усе на цій сторінці.",
        visibility_key="design_section_visible",
        admin_model_name="homedesignsettings",
        blocks=_b(
            "home",
            "design_section_visible",
            "design_title",
            "design_lead",
            "design_cta_label",
            "design_image_1",
            "design_image_2",
            "design_image_1_url",
            "design_image_2_url",
        ),
        field_groups=(
            FieldGroup("Тексти", ("design_title", "design_lead", "design_cta_label")),
            FieldGroup(
                "Фото",
                (
                    "design_image_1",
                    "design_image_1_url",
                    "design_image_2",
                    "design_image_2_url",
                ),
            ),
        ),
    ),
    ContentSection(
        slug="styles",
        page_slug="home",
        title="Стилі",
        sidebar_title="Стилі",
        sidebar_icon="grid_view",
        preview_url="/#styles",
        description="Заголовки та картки стилів — усе на цій сторінці.",
        visibility_key="styles_section_visible",
        admin_model_name="homestylessettings",
        blocks=_b(
            "home",
            "styles_section_visible",
            "styles_title",
            "styles_lead",
            "styles_cta_label",
        ),
        field_groups=(
            FieldGroup(
                "Тексти", ("styles_title", "styles_lead", "styles_cta_label")
            ),
        ),
    ),
    ContentSection(
        slug="calculator",
        page_slug="home",
        title="Калькулятор",
        sidebar_title="Калькулятор",
        sidebar_icon="calculate",
        preview_url="/#calculator",
        description="Тексти, формула (коефіцієнти, площі, графік оплат). Ставки пакетів — з карток пакетів.",
        visibility_key="calculator_section_visible",
        admin_model_name="homecalculatorsettings",
        blocks=_b(
            "home",
            "calculator_section_visible",
            "calculator_title",
            "calculator_lead",
            "calculator_cta_label",
            "calculator_note",
        ),
        field_groups=(
            FieldGroup(
                "Тексти",
                (
                    "calculator_title",
                    "calculator_lead",
                    "calculator_cta_label",
                    "calculator_note",
                ),
            ),
        ),
    ),
    ContentSection(
        slug="proof",
        page_slug="home",
        title="Відгуки та кейси",
        sidebar_title="Відгуки та кейси",
        sidebar_icon="rate_review",
        preview_url="/#proof",
        description="Заголовки, відгуки, кейси, рейтинг Google і текст порожнього стану.",
        visibility_key="proof_section_visible",
        admin_model_name="homeproofsettings",
        blocks=_b(
            "home",
            "proof_section_visible",
            "proof_title",
            "proof_reviews_badge",
            "proof_cases_did_label",
            "proof_reviews_empty",
        ),
        field_groups=(
            FieldGroup(
                "Тексти",
                (
                    "proof_title",
                    "proof_reviews_badge",
                    "proof_cases_did_label",
                    "proof_reviews_empty",
                ),
            ),
        ),
    ),
    ContentSection(
        slug="faq",
        page_slug="home",
        title="Питання та відповіді",
        sidebar_title="Питання та відповіді",
        sidebar_icon="help",
        preview_url="/#faq",
        description="Заголовки, фото та питання — усе на цій сторінці.",
        visibility_key="faq_section_visible",
        admin_model_name="homefaqsettings",
        blocks=_b(
            "home",
            "faq_section_visible",
            "faq_badge",
            "faq_title",
            "faq_image_1",
            "faq_image_2",
            "faq_image_1_static",
            "faq_image_2_static",
        ),
        field_groups=(
            FieldGroup("Тексти", ("faq_badge", "faq_title")),
            FieldGroup(
                "Фото",
                (
                    "faq_image_1",
                    "faq_image_1_static",
                    "faq_image_2",
                    "faq_image_2_static",
                ),
            ),
        ),
    ),
    ContentSection(
        slug="footer",
        page_slug="site",
        title="Підвал сайту",
        sidebar_title="Підвал сайту",
        sidebar_icon="vertical_align_bottom",
        preview_url="/#contacts",
        description="Слоган, послуги, юридичний рядок і що показувати.",
        admin_model_name="sitefootersettings",
        blocks=_b(
            "site",
            "footer_tagline",
            "footer_cta_label",
            "footer_cta_visible",
            "footer_socials_visible",
            "footer_menu_title",
            "footer_services_title",
            "footer_contacts_title",
            "footer_service_1",
            "footer_service_2",
            "footer_service_3",
            "footer_legal",
        ),
        field_groups=(
            FieldGroup("Бренд", ("footer_tagline", "footer_cta_label", "footer_cta_visible")),
            FieldGroup("Соцмережі", ("footer_socials_visible",)),
            FieldGroup(
                "Заголовки колонок",
                (
                    "footer_menu_title",
                    "footer_services_title",
                    "footer_contacts_title",
                ),
            ),
            FieldGroup(
                "Послуги",
                ("footer_service_1", "footer_service_2", "footer_service_3"),
            ),
            FieldGroup("Юридичний текст", ("footer_legal",)),
        ),
    ),
    ContentSection(
        slug="modal",
        page_slug="site",
        title="Форма дзвінка",
        sidebar_title="Форма дзвінка",
        sidebar_icon="chat",
        preview_url="/",
        description="Тексти форми заявки та екрану успіху.",
        admin_model_name="sitemodalsettings",
        blocks=_b(
            "site",
            "modal_title",
            "modal_sub",
            "modal_submit",
            "modal_success_title",
            "modal_success_sub",
            "modal_success_close",
        ),
        field_groups=(
            FieldGroup("Форма", ("modal_title", "modal_sub", "modal_submit")),
            FieldGroup(
                "Успіх",
                ("modal_success_title", "modal_success_sub", "modal_success_close"),
            ),
        ),
    ),
    ContentSection(
        slug="privacy",
        page_slug="privacy",
        title="Політика конфіденційності",
        sidebar_title="Конфіденційність",
        sidebar_icon="policy",
        preview_url="/privacy/",
        description="Заголовок і текст сторінки політики конфіденційності.",
        admin_model_name="privacypagesettings",
        blocks=_b("privacy", "privacy_title", "privacy_body"),
        field_groups=(FieldGroup("Контент", ("privacy_title", "privacy_body")),),
    ),
)


def get_section(page_slug: str, section_slug: str) -> ContentSection | None:
    for section in CONTENT_SECTIONS:
        if section.page_slug == page_slug and section.slug == section_slug:
            return section
    return None


def all_registry_block_keys() -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for section in CONTENT_SECTIONS:
        for pair in section.blocks:
            if pair not in seen:
                seen.add(pair)
                keys.append(pair)
    return keys


def iter_section_blocks(section: ContentSection):
    for page, key in section.blocks:
        yield page, key, BLOCK_FIELD_LABELS.get((page, key), key)


def build_content_sidebar_items() -> list[dict]:
    return [
        {
            "title": section.sidebar_title or section.title,
            "icon": section.sidebar_icon,
            "link": reverse_lazy(
                f"admin:landing_{section.admin_model_name}_changelist"
            ),
        }
        for section in CONTENT_SECTIONS
    ]
