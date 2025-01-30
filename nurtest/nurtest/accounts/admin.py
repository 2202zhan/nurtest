from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Поля для отображения в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    # Поля для фильтрации
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    # Поля для редактирования в админке
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Поля, которые отображаются при создании нового пользователя 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

# Регистрация модели CustomUser в админке
admin.site.register(CustomUser, CustomUserAdmin)