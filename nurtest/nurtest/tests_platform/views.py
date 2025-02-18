from django.shortcuts import render, get_object_or_404
from .models import Test, TestResult, AnswerChoice, UserAnswer
from django.contrib.auth.decorators import login_required
import random
from .models import Question

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Test, Category
from django import template
# Отображение списка доступных тестов
def test_list(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'test/tests.html', {'tests': tests})

@login_required
def process_answers(request, questions, test_result):
    score = 0
    total_points = 0
    user_answers_dict = {}  # Словарь для хранения ответов

    for question in questions:
        selected_answer = request.POST.get(str(question.id))
        if selected_answer:
            user_answers_dict[question.id] = selected_answer  # Сохраняем ответ в словарь

            # Для одиночного ответа (radio)
            if question.question_type == 'single':
                try:
                    answer_choice = AnswerChoice.objects.get(id=selected_answer)
                    if answer_choice.is_correct:
                        score += question.points
                    total_points += question.points
                    UserAnswer.objects.create(
                        question=question,
                        selected_answer=answer_choice,
                        test_result=test_result
                    )
                except AnswerChoice.DoesNotExist:
                    continue

            # Для множественного ответа (checkbox)
            elif question.question_type == 'multiple':
                selected_answers = request.POST.getlist(str(question.id))
                correct_answers = question.answerchoice_set.filter(is_correct=True)
                correct_count = correct_answers.count()
                selected_correct_count = 0
                for answer_id in selected_answers:
                    try:
                        answer_choice = AnswerChoice.objects.get(id=answer_id)
                        if answer_choice.is_correct:
                            selected_correct_count += 1
                        UserAnswer.objects.create(
                            question=question,
                            selected_answer=answer_choice,
                            test_result=test_result
                        )
                    except AnswerChoice.DoesNotExist:
                        continue

                if selected_correct_count == correct_count:
                    score += question.points
                else:
                    score += question.points * (selected_correct_count / correct_count)

                total_points += question.points

            elif question.question_type == 'text':
                text_answer = selected_answer.strip()
                UserAnswer.objects.create(
                    question=question,
                    text_answer=text_answer,
                    test_result=test_result
                )
                total_points += question.points

        else:
            total_points += question.points  # Если ответа нет, баллы за вопрос все равно начисляются

    # Сохраняем ответы в сессию
    request.session['user_answers'] = user_answers_dict

    return score, total_points

from django.core.paginator import Paginator

@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.question_set.all()

    # Добавляем пагинацию (по 5 вопросов на страницу)
    paginator = Paginator(questions, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        test_result = TestResult.objects.create(user=request.user, test=test, score=0)
        score, total_points = process_answers(request, questions, test_result)
        test_result.score = score
        test_result.save()

        percentage = (score / total_points) * 100 if total_points > 0 else 0

        return render(request, 'test/test_result.html', {
            'test': test,
            'score': score,
            'percentage': percentage,
            'result': test_result
        })

    return render(request, 'test/test_detail.html', {
        'test': test,
        'page_obj': page_obj,  # Передаем объект страницы
    })


@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.question_set.all()

    # Пагинация (по 5 вопросов на страницу)
    paginator = Paginator(questions, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Извлекаем сохраненные ответы из сессии
    saved_answers = request.session.get('user_answers', {})

    if request.method == 'POST':
        # Сохраняем ответы в сессии
        user_answers = {}
        for question in test.question_set.all():
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                user_answers[question.id] = selected_answer_id

        # Сохраняем в сессии
        request.session['user_answers'] = user_answers

        # Сохраняем результат теста
        test_result = TestResult.objects.create(user=request.user, test=test, score=0)
        score, total_points = process_answers(request, questions, test_result)
        test_result.score = score
        test_result.save()

        percentage = (score / total_points) * 100 if total_points > 0 else 0

        # Очистить сохраненные ответы после завершения теста
        request.session.pop('user_answers', None)

        return render(request, 'test/test_result.html', {
            'test': test,
            'score': score,
            'percentage': percentage,
            'result': test_result
        })

    return render(request, 'test/test_detail.html', {
        'test': test,
        'page_obj': page_obj,
        'saved_answers': saved_answers,  # Передаем сохраненные ответы
    })
# Детализация ответов пользователя на тест
@login_required
def test_result_detail(request, result_id):
    result = get_object_or_404(TestResult, id=result_id)
    user_answers = UserAnswer.objects.filter(test_result=result)

    # Собираем ответы для всех вопросов
    question_answers = {}
    for answer in user_answers:
        question_answers[answer.question.id] = answer.selected_answer.id

    return render(request, 'test/test_result_detail.html', {
        'result': result,
        'user_answers': user_answers,
        'question_answers': question_answers  # Передаем все ответы по вопросам
    })


def random_test(request):
    test = random.choice(Test.objects.all())
    questions = test.question_set.all()

    if request.method == 'POST':
        correct_answers = 0
        total_questions = questions.count()
        
        for question in questions:
            user_answer = request.POST.getlist(str(question.id))
            correct_choices = question.answerchoice_set.filter(is_correct=True).values_list('id', flat=True)
            correct_choices = set(map(str, correct_choices))

            if set(user_answer) == correct_choices:
                correct_answers += 1

        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        result = TestResult.objects.create(user=request.user, test=test, score=correct_answers)
        return render(request, 'test/test_result.html', {
    'score': correct_answers,
    'percentage': round(percentage, 2),
    'test': test,
    'result': result  # <-- Добавляем в контекст
})

    return render(request, 'test/random_test.html', {'questions': questions, 'test': test})

def test_list(request):
    query = request.GET.get('q', '')  # Получаем строку поиска
    tests = Test.objects.filter(title__icontains=query) if query else Test.objects.all()

    paginator = Paginator(tests, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tests': tests,
        'page_obj': page_obj,
        'query': query,  # Передаем введенный запрос обратно в шаблон
    }
    return render(request, 'test/tests.html', context)



register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)