from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta
from collections import defaultdict
import calendar
import json

from .forms import CustomUserCreationForm, CustomUserLoginForm
from tests_platform.models import TestResult
import g4f


# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


# Вход пользователя
def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# Домашняя страница с календарем активности
def home(request):
    user = request.user

    # Получение года и месяца из GET-запроса
    year = request.GET.get('year', datetime.now().year)
    month = request.GET.get('month', datetime.now().month)
    year = int(year)
    month = int(month)

    # Ограничение на переход
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Генерация данных для текущего месяца
    activity_calendar = generate_month_activity_calendar(user, year, month)

    return render(request, 'home.html', {
        'activity_calendar': activity_calendar,
        'prev_month': {'year': year if month > 1 else year - 1, 'month': month - 1 if month > 1 else 12},
        'next_month': {'year': year if month < 12 else year + 1, 'month': month + 1 if month < 12 else 1},
    })


# Генерация календаря активности
def generate_month_activity_calendar(user, year, month):
    if not user.is_authenticated:
        calendar_data = {'month': month, 'year': year, 'weeks': []}
        month_days = calendar.Calendar().monthdayscalendar(year, month)
        for week in month_days:
            week_data = [{'date': None, 'color': '#f3f3f3'} if day == 0 else {'date': datetime(year, month, day).date(), 'color': '#f3f3f3'} for day in week]
            calendar_data['weeks'].append(week_data)
        return calendar_data
   
    start_date = datetime(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    end_date = start_date + timedelta(days=days_in_month - 1)

    activity_data = defaultdict(int)
    results = TestResult.objects.filter(user=user, completed_at__range=[start_date, end_date])
    for result in results:
        date = result.completed_at.date()
        activity_data[date] += 1

    calendar_data = {'month': month, 'year': year, 'weeks': []}
    month_days = calendar.Calendar().monthdayscalendar(year, month)
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:  # Пустые ячейки
                week_data.append({'date': None, 'color': '#f3f3f3'})
            else:
                date = datetime(year, month, day).date()
                count = activity_data.get(date, 0)

                # Определение цвета ячеек
                if count > 5:
                    color = "green"
                elif count > 2:
                    color = "yellow"
                elif count > 0:
                    color = "lightblue"
                else:
                    color = "#f3f3f3"

                week_data.append({'date': date, 'color': color})
        calendar_data['weeks'].append(week_data)

    return calendar_data


# Настройки пользователя
@login_required
def settings(request):
    return render(request, 'accounts/settings.html')


# Чат с AI
@csrf_exempt
def chatgpt(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message.strip():
                return JsonResponse({"error": "Сообщение пустое"}, status=400)

            # Используем g4f для получения ответа
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message},
                ]
            )

            if response:
                return JsonResponse({"reply": response}, status=200)
            else:
                return JsonResponse({"error": "Нет ответа от модели"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Метод запроса не поддерживается"}, status=405)

def toprank_view(request):
    # Пример фиктивных данных для рейтинга
    ratings = [
        {"username": "User1", "score": 150},
        {"username": "User2", "score": 130},
        {"username": "User3", "score": 120},
        {"username": "User4", "score": 100},
        {"username": "User5", "score": 80},
    ]

    # Сортируем список пользователей по убыванию баллов
    ratings.sort(key=lambda x: x['score'], reverse=True)

    return render(request, 'toprank.html', {'ratings': ratings})