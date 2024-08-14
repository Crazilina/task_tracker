from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя с кастомизацией для использования email в качестве уникального идентификатора.
    """

    username = None
    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Укажите почту")
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name="Телефон", help_text="Укажите телефон")

    # Указываем, что для аутентификации будет использоваться email, а не username.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
