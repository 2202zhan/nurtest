from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from tests_platform.models import Test, Question, AnswerChoice

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
    success_url = reverse_lazy('test-list')

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

class AnswerChoiceCreateView(PermissionRequiredMixin, CreateView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_form.html'
    fields = ['question', 'text', 'is_correct']
    permission_required = 'tests.add_answerchoice'
    success_url = reverse_lazy('test-list')

class AnswerChoiceUpdateView(PermissionRequiredMixin, UpdateView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_form.html'
    fields = ['question', 'text', 'is_correct']
    permission_required = 'tests.change_answerchoice'
    success_url = reverse_lazy('test-list')

class AnswerChoiceDeleteView(PermissionRequiredMixin, DeleteView):
    model = AnswerChoice
    template_name = 'admin/answerchoice_confirm_delete.html'
    permission_required = 'tests.delete_answerchoice'
    success_url = reverse_lazy('test-list')