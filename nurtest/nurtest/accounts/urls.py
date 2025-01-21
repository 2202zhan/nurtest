from django.urls import path
from .views import register, login_view, home
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login_view'),
    path('', home, name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

