from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView

from datetime import datetime, timedelta
from collections import defaultdict
from tests_platform.models import TestResult

from django.contrib.auth.decorators import login_required


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
    activity_calendar = generate_activity_calendar(user)
    
    return render(request, 'home.html', {
        'activity_calendar': activity_calendar,
    })



def generate_activity_calendar(user):
    """Генерирует данные для календаря активности"""
    today = datetime.today()
    start_date = today - timedelta(days=365)  # Последний год
    activity_data = defaultdict(int)

    # Считаем тесты за год
    results = TestResult.objects.filter(user=user, completed_at__gte=start_date)
    for result in results:
        date = result.completed_at.date()
        activity_data[date] += 1

    # Генерация данных для календаря
    calendar = []
    current_week = []
    day = start_date

    while day <= today:
        count = activity_data.get(day, 0)
        # Определяем цвет активности
        if count > 5:
            color = "green"
        elif count > 2:
            color = "yellow"
        elif count > 0:
            color = "lightblue"
        else:
            color = "#f3f3f3"  # Белый цвет для бездействующих дней

        current_week.append({'date': day.strftime('%Y-%m-%d'), 'count': count, 'color': color})

        # Если конец недели (воскресенье), добавляем текущую неделю в календарь
        if day.weekday() == 6:  
            calendar.append(current_week)
            current_week = []
        
        day += timedelta(days=1)

    # Добавление оставшихся дней в последнюю неделю, если она неполная
    if current_week:  
        calendar.append(current_week)

    return calendar



