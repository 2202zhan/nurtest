from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView

from datetime import datetime, timedelta
from collections import defaultdict
import calendar
from tests_platform.models import TestResult

from django.contrib.auth.decorators import login_required




from django.shortcuts import render
from datetime import datetime




def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print(f'Debug: User created, user={user}')  # Debugging line
            return redirect('home')
        else:
            print(f'Debug: form errors={form.errors}')  # Debugging line
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
        print('Debug: GET request, empty form initialized')  # Debugging line
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(f'Debug: username={username}, password={password}')  # Debugging line
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print(f'Debug: user authenticated, user={user}')  # Debugging line
                login(request, user)
                return redirect('home')  # Redirect to the home page
            else:
                print('Debug: authentication failed')  # Debugging line
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            print(f'Debug: form errors={form.errors}')  # Debugging line
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def home(request):
    return render(request, 'home.html')

def settings(request):
    return render(request, 'accounts/settings.html')











@login_required
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




def generate_month_activity_calendar(user, year, month):
    # Получение активности пользователя за указанный месяц
    start_date = datetime(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    end_date = start_date + timedelta(days=days_in_month - 1)

    # Собираем активности за месяц
    activity_data = defaultdict(int)
    results = TestResult.objects.filter(user=user, completed_at__range=[start_date, end_date])
    for result in results:
        date = result.completed_at.date()
        activity_data[date] += 1

    # Формируем данные по неделям
    calendar_data = {
        'month': month,
        'year': year,
        'weeks': []
    }

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

                week_data.append({'date': date, 'color': color, 'count': count})
        calendar_data['weeks'].append(week_data)

    return calendar_data





