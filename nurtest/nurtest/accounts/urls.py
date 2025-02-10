from django.urls import path, include
from .views import register, login_view, home, settings, chatgpt
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from custom_admin.views import UserListView
from django.urls import path
from . import views
import custom_admin.views

from django.views.generic import TemplateView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login_view'),
    path('', home, name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('settings/', settings, name='settings'),
    path('chatgpt/', chatgpt, name='chatgpt'),
    path('toprank/', views.toprank_view, name='toprank'),
    path('custom-admin/', include('custom_admin.urls')),  # Кастомная админ-панель
    path('admin/users/', UserListView.as_view(), name='user_list'),
    
    path('blocked/', TemplateView.as_view(template_name="accounts/blocked.html"), name='blocked'),
    
    
  
   

]

