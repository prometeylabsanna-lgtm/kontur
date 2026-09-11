from __future__ import annotations

from datetime import datetime, time, timedelta

from django.db.models import QuerySet
from django.utils import timezone

from unfold.contrib.filters.admin import ChoicesDropdownFilter, DropdownFilter


class LabeledChoicesDropdownFilter(ChoicesDropdownFilter):
    """Dropdown без префікса «За …» у лейблі форми."""

    def choices(self, changelist):
        for choice in super().choices(changelist):
            form = choice.get("form")
            if form is not None:
                for field in form.fields.values():
                    field.label = self.title
            yield choice


class DistinctValuesDropdownFilter(DropdownFilter):
    """Dropdown з унікальних значень CharField."""

    field_name: str = ""

    def has_output(self) -> bool:
        # Показувати навіть без значень у БД (лише опція «Всі»).
        return True

    def lookups(self, request, model_admin):
        if not self.field_name:
            return []
        qs = (
            model_admin.get_queryset(request)
            .exclude(**{f"{self.field_name}__exact": ""})
            .values_list(self.field_name, flat=True)
            .distinct()
            .order_by(self.field_name)
        )
        return [(value, value) for value in qs if value]

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value:
            return queryset.filter(**{self.field_name: value})
        return queryset

    def choices(self, changelist):
        for choice in super().choices(changelist):
            form = choice.get("form")
            if form is not None:
                for field in form.fields.values():
                    field.label = self.title
            yield choice


class PackageDropdownFilter(DistinctValuesDropdownFilter):
    title = "Пакет"
    parameter_name = "package"
    field_name = "package"


class ObjectTypeDropdownFilter(DistinctValuesDropdownFilter):
    title = "Тип об’єкта"
    parameter_name = "object_type"
    field_name = "object_type"


class CreatedDateDropdownFilter(DropdownFilter):
    title = "Дата"
    parameter_name = "created"

    def lookups(self, request, model_admin):
        return (
            ("today", "Сьогодні"),
            ("7days", "Останні 7 днів"),
            ("month", "Цього місяця"),
            ("year", "Цього року"),
        )

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if not value:
            return queryset
        now = timezone.localtime(timezone.now())
        today = now.date()
        if value == "today":
            start = timezone.make_aware(datetime.combine(today, time.min))
            return queryset.filter(created_at__gte=start)
        if value == "7days":
            start = timezone.make_aware(
                datetime.combine(today - timedelta(days=7), time.min)
            )
            return queryset.filter(created_at__gte=start)
        if value == "month":
            start = timezone.make_aware(
                datetime.combine(today.replace(day=1), time.min)
            )
            return queryset.filter(created_at__gte=start)
        if value == "year":
            start = timezone.make_aware(
                datetime.combine(today.replace(month=1, day=1), time.min)
            )
            return queryset.filter(created_at__gte=start)
        return queryset

    def choices(self, changelist):
        for choice in super().choices(changelist):
            form = choice.get("form")
            if form is not None:
                for field in form.fields.values():
                    field.label = self.title
            yield choice


class StatusDropdownFilter(LabeledChoicesDropdownFilter):
    """Статус заявки — dropdown зверху."""
