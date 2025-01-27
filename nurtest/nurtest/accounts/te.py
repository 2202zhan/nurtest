from django.http import HttpResponse

def some_view(request, token):
    print(f"Received token: {token}")  # Логирование токена
    return HttpResponse(f"Token: {token}")
