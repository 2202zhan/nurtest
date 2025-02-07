from django.urls import path
from .views import (
    TestListView, TestCreateView, TestUpdateView, TestDeleteView,
    QuestionListView, QuestionCreateView, QuestionUpdateView, QuestionDeleteView,
    AnswerChoiceListView, AnswerChoiceCreateView, AnswerChoiceUpdateView, AnswerChoiceDeleteView, test_stats, block_user, unblock_user, UserListView,
)

urlpatterns = [
    # Управление тестами
    path('tests/', TestListView.as_view(), name='test-list'),
    path('tests/add/', TestCreateView.as_view(), name='test-add'),
    path('tests/<int:pk>/edit/', TestUpdateView.as_view(), name='test-edit'),
    path('tests/<int:pk>/delete/', TestDeleteView.as_view(), name='test-delete'),
    path('stats/', test_stats, name='test-stats'),
    path('user/<int:user_id>/block/', block_user, name='block_user'),
    path('user/<int:user_id>/unblock/', unblock_user, name='unblock_user'),
    path('users/', UserListView.as_view(), name='user-list'),  # Должно быть 'user-list'


    # Управление вопросами
    path('tests/<int:test_id>/questions/', QuestionListView.as_view(), name='question-list'),
    path('tests/<int:test_id>/questions/add/', QuestionCreateView.as_view(), name='question-add'),
    path('questions/<int:pk>/edit/', QuestionUpdateView.as_view(), name='question-edit'),
    path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question-delete'),

    # Управление вариантами ответов
    path('questions/<int:question_id>/answers/', AnswerChoiceListView.as_view(), name='answerchoice-list'),
    path('questions/<int:question_id>/answers/add/', AnswerChoiceCreateView.as_view(), name='answerchoice-add'),
    path('answers/<int:pk>/edit/', AnswerChoiceUpdateView.as_view(), name='answerchoice-edit'),
    path('answers/<int:pk>/delete/', AnswerChoiceDeleteView.as_view(), name='answerchoice-delete'),
]