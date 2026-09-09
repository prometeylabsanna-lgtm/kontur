from django.db import models
from django.utils import timezone


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Нова"
        IN_PROGRESS = "in_progress", "В роботі"
        CALLED = "called", "Передзвонили"
        REJECTED = "rejected", "Відмова"
        SUCCESS = "success", "Успіх"

    name = models.CharField("Ім’я", max_length=120)
    phone = models.CharField("Телефон", max_length=32)
    context = models.CharField("Звідки заявка", max_length=255, blank=True)
    package = models.CharField("Пакет", max_length=64, blank=True)
    object_type = models.CharField("Тип об’єкта", max_length=64, blank=True)
    area = models.PositiveSmallIntegerField("Площа, м²", null=True, blank=True)
    calc_summary = models.TextField("Деталі розрахунку", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    utm_source = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField("Створено", default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.name} · {self.phone} · {self.created_at:%d.%m.%Y %H:%M}"


class SiteSettings(models.Model):
    site_name = models.CharField("Назва сайту", max_length=128, default="Kontur+")
    brand_desc = models.CharField(
        "Опис бренду", max_length=128, default="ремонтна організація", blank=True
    )
    phone_display = models.CharField("Телефон на сайті", max_length=32, blank=True)
    phone_tel = models.CharField(
        "Телефон для дзвінка",
        max_length=32,
        blank=True,
        help_text="Лише цифри з +380… — для кнопки «подзвонити»",
    )
    email = models.EmailField("Електронна пошта", blank=True)
    city = models.CharField("Місто", max_length=64, blank=True)
    work_hours = models.CharField("Години роботи", max_length=128, blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)
    meta_description = models.CharField(
        "Опис для Google",
        max_length=255,
        blank=True,
        help_text="Короткий текст у результатах пошуку (до ~160 символів)",
    )

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self):
        return self.site_name or "Kontur+"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def load(cls):
        return cls.get_solo()


class SiteBlock(models.Model):
    class Page(models.TextChoices):
        HOME = "home", "Головна"
        SITE = "site", "Сайт"
        PRIVACY = "privacy", "Конфіденційність"

    class ContentType(models.TextChoices):
        TEXT = "text", "Текст"
        IMAGE = "image", "Фото"
        URL = "url", "Посилання"

    page = models.CharField(max_length=32, choices=Page.choices)
    key = models.CharField(max_length=64)
    label = models.CharField(max_length=128)
    content_type = models.CharField(
        max_length=16, choices=ContentType.choices, default=ContentType.TEXT
    )
    text_html = models.TextField(blank=True)
    image = models.ImageField(upload_to="blocks/", blank=True)
    link_url = models.CharField(max_length=512, blank=True)
    link_label = models.CharField(max_length=128, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("page", "sort_order", "key")
        verbose_name = "Блок контенту"
        verbose_name_plural = "Блоки контенту"
        constraints = [
            models.UniqueConstraint(
                fields=["page", "key"], name="unique_site_block_page_key"
            ),
        ]

    def __str__(self):
        return f"{self.page}.{self.key}"

    @property
    def cache_key(self) -> str:
        return f"{self.page}.{self.key}"


class HeroSlide(models.Model):
    image = models.ImageField("Фото", upload_to="hero/", blank=True)
    image_url = models.URLField(
        "Посилання на фото",
        blank=True,
        help_text="Якщо файл не завантажено — можна вставити посилання на зображення",
    )
    alt_text = models.CharField(
        "Короткий опис фото",
        max_length=200,
        blank=True,
        help_text="Для доступності: що зображено на фото",
    )
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Фото банера"
        verbose_name_plural = "Фото банера"

    def __str__(self):
        return self.alt_text or f"Слайд {self.pk or self.sort_order}"

    @property
    def src(self) -> str:
        if self.image:
            return self.image.url
        return self.image_url or ""


class AdvantageItem(models.Model):
    class Kind(models.TextChoices):
        STANDARD = "standard", "Звичайна картка"
        CTA = "cta", "Картка з кнопкою"

    kind = models.CharField(
        "Тип картки", max_length=16, choices=Kind.choices, default=Kind.STANDARD
    )
    icon = models.CharField(
        "Іконка",
        max_length=32,
        choices=[
            ("price", "Документ / ціна"),
            ("package", "Пакет / коробка"),
            ("calendar", "Календар / строк"),
            ("shield", "Щит / гарантія"),
            ("pin", "Мітка / локація"),
            ("none", "Без іконки"),
        ],
        default="price",
        blank=True,
    )
    title = models.CharField("Заголовок", max_length=160)
    text = models.TextField("Текст", blank=True)
    image = models.ImageField("Фото", upload_to="advantages/", blank=True)
    image_static = models.CharField(
        "Запасний шлях до фото",
        max_length=255,
        blank=True,
        help_text="Службове поле. Зазвичай достатньо завантажити фото вище.",
    )
    image_alt = models.CharField("Короткий опис фото", max_length=200, blank=True)
    cta_label = models.CharField("Текст посилання", max_length=120, blank=True)
    cta_href = models.CharField("Куди веде посилання", max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Перевага"
        verbose_name_plural = "Переваги"

    def __str__(self):
        return self.title


class PackageItem(models.Model):
    name = models.CharField("Назва", max_length=80)
    description = models.TextField("Опис", blank=True)
    price = models.PositiveIntegerField("Ціна $/м²", default=0)
    price_unit = models.CharField("Одиниця ціни", max_length=32, default="$/м²")
    features = models.TextField(
        "Що входить у пакет",
        blank=True,
        help_text="Кожен рядок — окремий пункт у списку на сайті",
    )
    badge = models.CharField(
        "Мітка на картці",
        max_length=64,
        blank=True,
        help_text="Наприклад: «Рекомендуємо»",
    )
    cta_label = models.CharField("Текст кнопки", max_length=64, default="Замовити")
    is_recommended = models.BooleanField("Рекомендований пакет", default=False)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Пакет"
        verbose_name_plural = "Пакети"

    def __str__(self):
        return self.name

    def feature_list(self) -> list[str]:
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class DesignFeature(models.Model):
    text = models.CharField("Пункт", max_length=255)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Пункт дизайну"
        verbose_name_plural = "Пункти дизайну"

    def __str__(self):
        return self.text


class StyleItem(models.Model):
    title = models.CharField("Назва", max_length=80)
    text = models.TextField("Опис", blank=True)
    image = models.ImageField("Фото", upload_to="styles/", blank=True)
    image_url = models.URLField(
        "Посилання на фото",
        blank=True,
        help_text="Якщо файл не завантажено — можна вставити посилання",
    )
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Стиль"
        verbose_name_plural = "Стилі"

    def __str__(self):
        return self.title

    @property
    def src(self) -> str:
        if self.image:
            return self.image.url
        return self.image_url or ""


class ReviewItem(models.Model):
    text = models.TextField("Відгук")
    name = models.CharField("Ім’я", max_length=80)
    meta = models.CharField("Підпис", max_length=120, blank=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"

    def __str__(self):
        return self.name


class CaseItem(models.Model):
    title = models.CharField("Заголовок", max_length=160)
    location = models.CharField("Місце / район", max_length=120, blank=True)
    text = models.TextField("Опис", blank=True)
    image = models.ImageField("Фото", upload_to="cases/", blank=True)
    image_static = models.CharField(
        "Запасний шлях до фото",
        max_length=255,
        blank=True,
        help_text="Службове поле. Зазвичай достатньо завантажити фото вище.",
    )
    image_alt = models.CharField("Короткий опис фото", max_length=200, blank=True)
    tags = models.TextField(
        "Теги робіт",
        blank=True,
        help_text="Кожен рядок — окремий тег під описом кейсу",
    )
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Кейс"
        verbose_name_plural = "Кейси"

    def __str__(self):
        return self.title

    def tag_list(self) -> list[str]:
        return [line.strip() for line in self.tags.splitlines() if line.strip()]


class FAQItem(models.Model):
    question = models.CharField("Питання", max_length=255)
    answer = models.TextField("Відповідь")
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показувати на сайті", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "Питання та відповідь"
        verbose_name_plural = "Питання та відповіді"

    def __str__(self):
        return self.question
