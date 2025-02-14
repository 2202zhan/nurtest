from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from tests_platform.models import Test, Question, AnswerChoice 
from django.db import models
from django.db.models import Avg, Count, Q, Case, When, FloatField
from django.db.models import Count, Avg, Max

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, redirect
from accounts.models import CustomUser



# Управление тестами
class TestListView(PermissionRequiredMixin, ListView):
    model = Test
    template_name = 'admin/test_list.html'
    permission_required = 'tests.view_test'
    context_object_name = 'tests'

class TestCreateView(PermissionRequiredMixin, CreateView):
    model = Test
    template_name = 'admin/test_form.html'
    fields = ['title', 'description', 'category', 'author', 'is_active']
    permission_required = 'tests.add_test'
    success_url = reverse_lazy('test-list')

class TestUpdateView(PermissionRequiredMixin, UpdateView):
    model = Test
    template_name = 'admin/test_form.html'
    fields = ['title', 'description', 'category', 'author', 'is_active']
    permission_required = 'tests.change_test'
    success_url = reverse_lazy('test-list')

class TestDeleteView(PermissionRequiredMixin, DeleteView):
    model = Test
    template_name = 'admin/test_confirm_delete.html'
    permission_required = 'tests.delete_test'
    success_url = reverse_lazy('test-list')

# Управление вопросами
class QuestionListView(PermissionRequiredMixin, ListView):
    model = Question
    template_name = 'admin/question_list.html'
    permission_required = 'tests.view_question'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.filter(test_id=self.kwargs['test_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = Test.objects.get(id=self.kwargs['test_id'])
        return context

class QuestionCreateView(PermissionRequiredMixin, CreateView):
    model = Question
    template_name = 'admin/question_form.html'
    fields = ['test', 'text', 'question_type', 'points']
    permission_required = 'tests.add_question'

    def get_success_url(self):
        return reverse('question-list', kwargs={'test_id': self.object.test.pk})

class QuestionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Question
    template_name = 'admin/question_form.html'
    fields = ['test', 'text', 'question_type', 'points']
    permission_required = 'tests.change_question'
    success_url = reverse_lazy('test-list')

class QuestionDeleteView(PermissionRequiredMixin, DeleteView):
    model = Question
    template_name = 'admin/question_confirm_delete.html'
    permission_required = 'tests.delete_question'
    success_url = reverse_lazy('test-list')
    def get_success_url(self):
        return reverse('question-list', kwargs={'test_id': self.object.test.pk})

# Управление вариантами ответов
class AnswerChoiceListView(PermissionRequiredMixin, ListView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_list.html'
    permission_required = 'tests.view_answerchoice'
    context_object_name = 'answers'

    def get_queryset(self):
        return AnswerChoice.objects.filter(question_id=self.kwargs['question_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(id=self.kwargs['question_id'])
        return context
    def get_success_url(self):
        return reverse('question-list', kwargs={'test_id': self.object.test.pk})

class AnswerChoiceCreateView(PermissionRequiredMixin, CreateView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_form.html'
    fields = ['question', 'text', 'is_correct']
    permission_required = 'tests.add_answerchoice'
    success_url = reverse_lazy('test-list')

    # def get_success_url(self):
    #     return reverse('question-list', kwargs={'test_id': self.object.test.pk})

class AnswerChoiceUpdateView(PermissionRequiredMixin, UpdateView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_form.html'
    fields = ['question', 'text', 'is_correct']
    permission_required = 'tests.change_answerchoice'
    success_url = reverse_lazy('test-list')
    

def get_success_url(self):
        return reverse('question-list', kwargs={'test_id': self.object.test.pk})

class AnswerChoiceDeleteView(PermissionRequiredMixin, DeleteView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_confirm_delete.html'
    permission_required = 'tests.delete_answerchoice'
    success_url = reverse_lazy('test-list')

    # def get_success_url(self):
    #     return reverse('question-list', kwargs={'test_id': self.object.test.pk})

SUCCESS_THRESHOLD = 50  # Порог успешного прохождения

def test_stats(request):
    stats = Test.objects.annotate(
        num_attempts=Count('testresult'),
        avg_score=Avg('testresult__score'),
        unique_users=Count('testresult__user', distinct=True),
        success_rate=Case(
            When(num_attempts=0, then=0.0),
            default=100.0 * Count(
                'testresult', 
                filter=Q(testresult__score__gte=SUCCESS_THRESHOLD)
            ) / Count('testresult'),
            output_field=FloatField()
        )
    ).order_by('-num_attempts')

    return render(request, 'admin/test_stats.html', {'stats': stats})




@login_required
@user_passes_test(lambda u: u.is_superuser)  # Только суперпользователь может изменять роли
def update_user_roles(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user.can_add_tests = 'can_add_tests' in request.POST
        user.can_edit_tests = 'can_edit_tests' in request.POST
        user.can_delete_tests = 'can_delete_tests' in request.POST
        user.save()
        messages.success(request, f'Роли пользователя {user.username} обновлены!')
    users = CustomUser.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})


@user_passes_test(lambda u: u.is_staff)
def block_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    if request.method == 'POST':
        user.is_blocked = True
        user.block_reason = request.POST.get('reason', '')
        user.save()
        messages.success(request, f"Пользователь {user.username} заблокирован")
    users = CustomUser.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})


@user_passes_test(lambda u: u.is_staff)
def unblock_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    user.is_blocked = False
    user.block_reason = ''
    user.save()
    messages.success(request, f"Пользователь {user.username} разблокирован")
    users = CustomUser.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})


class UserListView(ListView):
    model = User = CustomUser
    template_name = 'admin/user_list.html'
    context_object_name = 'users'

def user_list_view(request):
    print('qwdqwdqwdqw', users)
    users = CustomUser.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})