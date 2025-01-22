from django.urls import path
from . import views

urlpatterns = [
    path('tests/', views.test_list, name='test_list'),  # Страница с тестами
    path('tests/<int:test_id>/', views.test_detail, name='test_detail'),  # Страница теста
    path('tests/results/<int:result_id>/', views.test_result, name='test_result'),  # Страница с результатами
    path('tests/results/detail/<int:result_id>/', views.test_result_detail, name='test_result_detail'),  # Страница с результатами
]
