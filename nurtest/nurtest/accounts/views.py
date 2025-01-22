from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView


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
