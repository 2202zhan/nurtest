from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    blocked_until = models.DateTimeField(null=True, blank=True, verbose_name="Заблокирован до")
    block_reason = models.TextField(blank=True, verbose_name="Причина блокировки")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"