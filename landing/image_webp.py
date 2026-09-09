"""Конвертація ImageField → WebP (заміна оригіналу)."""

from __future__ import annotations

import logging
from io import BytesIO
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from django.db.models import ImageField, Model
from django.db.models.fields.files import FieldFile, ImageFieldFile
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

WEBP_QUALITY = 85
WEBP_MAX_SIDE = 2560
WEBP_METHOD = 6

# Уникаємо рекурсії, якщо save() знову тригерить pre_save.
_CONVERTING: set[tuple[int, str, str]] = set()


def iter_image_fields(model: type[Model]):
    for field in model._meta.get_fields():
        if isinstance(field, ImageField):
            yield field


def is_webp_name(name: str | None) -> bool:
    if not name:
        return False
    return PurePosixPath(name).suffix.lower() == ".webp"


def _open_pil(field_file: FieldFile | ImageFieldFile) -> Image.Image:
    field_file.open("rb")
    try:
        img = Image.open(field_file)
        img.load()
        return ImageOps.exif_transpose(img)
    finally:
        try:
            field_file.close()
        except Exception:
            pass


def _prepare_mode(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA"):
        return img.convert("RGBA")
    if img.mode == "P":
        if "transparency" in img.info:
            return img.convert("RGBA")
        return img.convert("RGB")
    if img.mode != "RGB":
        return img.convert("RGB")
    return img


def _resize_long_side(img: Image.Image, max_side: int) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest <= max_side:
        return img
    ratio = max_side / float(longest)
    new_size = (max(1, int(w * ratio)), max(1, int(h * ratio)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def render_webp_bytes(
    field_file: FieldFile | ImageFieldFile,
    *,
    quality: int = WEBP_QUALITY,
    max_side: int = WEBP_MAX_SIDE,
) -> bytes:
    img = _open_pil(field_file)
    img = _resize_long_side(img, max_side)
    img = _prepare_mode(img)
    buf = BytesIO()
    save_kw: dict = {"format": "WEBP", "quality": quality, "method": WEBP_METHOD}
    if img.mode == "RGBA":
        save_kw["lossless"] = False
    img.save(buf, **save_kw)
    return buf.getvalue()


def webp_filename(original_name: str) -> str:
    path = PurePosixPath(original_name or "image")
    stem = path.stem or "image"
    # Лише basename — upload_to моделі додасть префікс при save().
    return f"{stem}.webp"


def ensure_image_field_webp(
    instance: Model,
    field_name: str,
    *,
    force: bool = False,
    quality: int = WEBP_QUALITY,
    max_side: int = WEBP_MAX_SIDE,
) -> bool:
    """
    Замінює файл у ImageField на .webp.
    force=False: лише новий аплоад (зміна імені) і не .webp.
    force=True: будь-який наявний не-webp (для batch).
    Повертає True, якщо файл замінено (поля інстанса оновлені, без instance.save).
    """
    field_file = getattr(instance, field_name, None)
    if not field_file or not getattr(field_file, "name", None):
        return False

    name = field_file.name
    if is_webp_name(name):
        return False

    if not force and instance.pk:
        old_name = (
            type(instance)
            .objects.filter(pk=instance.pk)
            .values_list(field_name, flat=True)
            .first()
        )
        if old_name == name:
            return False

    guard = (id(instance), field_name, name)
    if guard in _CONVERTING:
        return False
    _CONVERTING.add(guard)
    try:
        data = render_webp_bytes(field_file, quality=quality, max_side=max_side)
        new_name = webp_filename(name)
        storage = field_file.storage
        old_name = name

        content = ContentFile(data, name=new_name)
        # save=False — запис у storage; model.save зробить викликач / Django.
        field_file.save(new_name, content, save=False)

        if old_name and old_name != field_file.name and storage.exists(old_name):
            try:
                storage.delete(old_name)
            except Exception:
                logger.exception("Не вдалося видалити оригінал %s", old_name)
        return True
    except Exception:
        logger.exception(
            "WebP-конвертація не вдалася: %s.%s (%s)",
            instance.__class__.__name__,
            field_name,
            name,
        )
        return False
    finally:
        _CONVERTING.discard(guard)


def convert_instance_images(
    instance: Model,
    *,
    force: bool = False,
) -> list[str]:
    changed: list[str] = []
    for field in iter_image_fields(type(instance)):
        if ensure_image_field_webp(instance, field.name, force=force):
            changed.append(field.name)
    return changed
