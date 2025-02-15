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
from tests_platform.models import TestResult, CustomUser
import g4f

from django.db.models import Sum

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .models import EmailConfirmationToken

# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Создаем токен подтверждения
            token = EmailConfirmationToken.generate_token()
            EmailConfirmationToken.objects.create(
                user=user,
                token=token
            )
            
            # Отправляем письмо с подтверждением
            current_site = get_current_site(request)
            confirm_url = f"http://{current_site.domain}/accounts/confirm-email/{token}/"
            
            send_mail(
                'Подтверждение регистрации',
                f'Для завершения регистрации перейдите по ссылке: {confirm_url}',
                'kulzhanofff@mail.ru',
                [user.email],
                fail_silently=False,
            )
            
            # Рендерим страницу с уведомлением вместо редиректа
            return render(request, 'accounts/email_confirmation_sent.html', {'user': user})
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def confirm_email(request, token):
    print(f"Получен токен: {token}")  # Проверка, какой токен приходит в функцию

    try:
        token_obj = EmailConfirmationToken.objects.get(token=token)
        print(f"Токен найден в базе: {token_obj}")  # Проверка, найден ли токен

        if token_obj.is_expired():
            print("Токен истёк")  # Проверка, истёк ли токен
            messages.error(request, 'Срок действия ссылки истёк.')
            return redirect('register')
        
        user = token_obj.user
        print(f"Активируем пользователя: {user.email}")  # Проверка, какого пользователя активируем

        user.is_active = True
        user.save()
        token_obj.delete()

        print("Email подтверждён, токен удалён")  # Подтверждение, что всё прошло успешно
        messages.success(request, 'Email успешно подтверждён! Теперь вы можете войти.')
        return redirect('login_view') 

    except EmailConfirmationToken.DoesNotExist:
        print("Ошибка: Токен не найден в базе")  # Если токен не найден
        messages.error(request, 'Неверная ссылка подтверждения.')
        return redirect('register')



def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Проверка на блокировку
            try:
                user = CustomUser.objects.get(username=username)
                if user.is_blocked:
                    return redirect('accounts/blocked.html')
            except CustomUser.DoesNotExist:
                pass
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Аккаунт не активирован. Проверьте вашу почту.')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
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
    top_users = CustomUser.objects.annotate(
        total_score=Sum('testresult__score')
    ).exclude(total_score=None).order_by('-total_score')[:20]

    ratings = [
        {
            'username': user.username,
            'score': user.total_score,
            'position': idx+1
        }
        for idx, user in enumerate(top_users)
    ]

    return render(request, 'toprank.html', {'ratings': ratings})