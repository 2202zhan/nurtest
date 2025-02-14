from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    blocked_until = models.DateTimeField(null=True, blank=True, verbose_name="Заблокирован до")
    block_reason = models.TextField(blank=True, verbose_name="Причина блокировки")

    # Добавляем роли пользователей
    can_add_tests = models.BooleanField(default=False, verbose_name="Может добавлять тесты")
    can_edit_tests = models.BooleanField(default=False, verbose_name="Может редактировать тесты")
    can_delete_tests = models.BooleanField(default=False, verbose_name="Может удалять тесты")
    can_add_questions = models.BooleanField(default=False, verbose_name="Может добавлять вопросы")
    can_edit_questions = models.BooleanField(default=False, verbose_name="Может редактировать вопросы")
    can_delete_questions = models.BooleanField(default=False, verbose_name="Может удалять вопросы")
    can_add_answers = models.BooleanField(default=False, verbose_name="Может добавлять ответы")
    can_edit_answers = models.BooleanField(default=False, verbose_name="Может редактировать ответы")
    can_delete_answers = models.BooleanField(default=False, verbose_name="Может удалять ответы")
    can_add_categories = models.BooleanField(default=False, verbose_name="Может добавлять категории")
    can_edit_categories = models.BooleanField(default=False, verbose_name="Может редактировать категории")
    can_delete_categories = models.BooleanField(default=False, verbose_name="Может удалять категории")
    


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"