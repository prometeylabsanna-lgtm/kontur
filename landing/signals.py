"""Авто-конвертація ImageField → WebP при збереженні моделей landing."""

from __future__ import annotations

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .image_webp import convert_instance_images


@receiver(pre_save)
def convert_landing_images_to_webp(sender, instance, **kwargs):
    if getattr(sender, "_meta", None) is None:
        return
    if sender._meta.app_label != "landing":
        return
    if sender._meta.proxy:
        return
    convert_instance_images(instance, force=False)
