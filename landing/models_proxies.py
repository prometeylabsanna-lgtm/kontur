from .models import SiteSettings


class SiteHeaderSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Шапка сайту"
        verbose_name_plural = "Шапка сайту"


class HomeHeroSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Головний банер"
        verbose_name_plural = "Головний банер"


class HomeAdvantagesSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Переваги"
        verbose_name_plural = "Переваги"


class HomePackagesSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Пакети"
        verbose_name_plural = "Пакети"


class HomeDesignSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Дизайн"
        verbose_name_plural = "Дизайн"


class HomeStylesSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Стилі"
        verbose_name_plural = "Стилі"


class HomeCalculatorSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Калькулятор"
        verbose_name_plural = "Калькулятор"


class HomeProofSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Відгуки та кейси"
        verbose_name_plural = "Відгуки та кейси"


class HomeFaqSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Питання та відповіді"
        verbose_name_plural = "Питання та відповіді"


class SiteFooterSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Підвал сайту"
        verbose_name_plural = "Підвал сайту"


class SiteModalSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Форма дзвінка"
        verbose_name_plural = "Форма дзвінка"


class PrivacyPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Політика конфіденційності"
        verbose_name_plural = "Політика конфіденційності"


class BrandColorSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Колір бренду"
        verbose_name_plural = "Колір бренду"
