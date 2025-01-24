from django.shortcuts import render, get_object_or_404
from .models import Test, TestResult, AnswerChoice, UserAnswer
from django.contrib.auth.decorators import login_required

# Отображение списка доступных тестов
@login_required
def test_list(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'test/tests.html', {'tests': tests})

# Обработка ответов на вопросы
def process_answers(request, questions, test_result):
    score = 0
    total_points = 0  # Считаем общий балл за все вопросы
    for question in questions:
        selected_answer = request.POST.getlist(str(question.id))  # Получаем все выбранные ответы
        total_points += question.points  # Добавляем баллы для каждого вопроса
        if selected_answer:
            # Для одиночного ответа (radio)
            if question.question_type == 'single':
                try:
                    answer_choice = AnswerChoice.objects.get(id=selected_answer[0])
                    if answer_choice.is_correct:
                        score += question.points
                    UserAnswer.objects.create(
                        question=question,
                        selected_answer=answer_choice,
                        test_result=test_result
                    )
                except AnswerChoice.DoesNotExist:
                    continue

            # Для множественного ответа (checkbox)
            elif question.question_type == 'multiple':
                for answer_id in selected_answer:
                    try:
                        answer_choice = AnswerChoice.objects.get(id=answer_id)
                        if answer_choice.is_correct:
                            score += question.points
                        UserAnswer.objects.create(
                            question=question,
                            selected_answer=answer_choice,
                            test_result=test_result
                        )
                    except AnswerChoice.DoesNotExist:
                        continue

            # Обработка текстового ответа
            elif question.question_type == 'text':
                text_answer = selected_answer[0].strip()
                UserAnswer.objects.create(
                    question=question,
                    text_answer=text_answer,
                    test_result=test_result
                )
    return score, total_points


# Страница прохождения теста
@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.question_set.all()

    if request.method == 'POST':
        test_result = TestResult.objects.create(user=request.user, test=test, score=0)
        score, total_points = process_answers(request, questions, test_result)
        test_result.score = score
        test_result.save()

        # Вычисление процента правильных ответов
        percentage = (score / total_points) * 100 if total_points > 0 else 0

        return render(request, 'test/test_result.html', {
            'test': test,
            'score': score,
            'percentage': percentage,  # Процент правильных ответов
            'result': test_result
        })

    return render(request, 'test/test_detail.html', {'test': test, 'questions': questions})

# Просмотр результатов теста
@login_required
def test_result(request, result_id):
    result = get_object_or_404(TestResult, id=result_id)
    test = result.test
    score = result.score

    # Получаем общее количество баллов за все вопросы
    total_points = test.question_set.aggregate(total_points=models.Sum('points'))['total_points'] or 0

    # Вычисляем процент правильных ответов
    percentage = (score / total_points) * 100 if total_points > 0 else 0

    return render(request, 'test/test_result.html', {
        'test': test,
        'score': score,
        'percentage': percentage,  # Процент правильных ответов
        'result': result,
    })

# Детализация ответов пользователя на тест
@login_required
def test_result_detail(request, result_id):
    result = get_object_or_404(TestResult, id=result_id)
    user_answers = UserAnswer.objects.filter(test_result=result)
    return render(request, 'test/test_result_detail.html', {
        'result': result,
        'user_answers': user_answers
    })
