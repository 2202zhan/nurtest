# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


class CustomUserBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and not user.is_blocked
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        
        if user and user.is_blocked:
            request.session['block_reason'] = user.block_reason
            return None
            
        return user