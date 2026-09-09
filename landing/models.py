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
    context = models.CharField("Джерело CTA", max_length=255, blank=True)
    package = models.CharField("Пакет", max_length=64, blank=True)
    object_type = models.CharField("Тип об’єкта", max_length=64, blank=True)
    area = models.PositiveSmallIntegerField("Площа, м²", null=True, blank=True)
    calc_summary = models.TextField("Параметри розрахунку", blank=True)
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
        verbose_name = "Лід"
        verbose_name_plural = "Ліди"

    def __str__(self):
        return f"{self.name} · {self.phone} · {self.created_at:%d.%m.%Y %H:%M}"
