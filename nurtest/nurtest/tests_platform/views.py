from django.shortcuts import render, get_object_or_404
from .models import Test, TestResult, AnswerChoice, UserAnswer
from django.contrib.auth.decorators import login_required

# Отображение списка доступных тестов
def test_list(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'test/tests.html', {'tests': tests})

# Обработка ответов на вопросы
@login_required
def process_answers(request, questions, test_result):
    score = 0
    total_points = 0  # Считаем общий балл за все вопросы
    for question in questions:
        selected_answer = request.POST.get(str(question.id))
        if selected_answer:
            # Для одиночного ответа (radio)
            if question.question_type == 'single':
                try:
                    answer_choice = AnswerChoice.objects.get(id=selected_answer)
                    if answer_choice.is_correct:
                        score += question.points
                    total_points += question.points  # Максимум баллов за этот вопрос
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

                # Рассчитываем баллы для многократных вопросов
                if selected_correct_count == correct_count:
                    score += question.points  # Все правильные ответы выбраны
                else:
                    # Если выбраны только некоторые правильные ответы, начисляем баллы пропорционально
                    score += question.points * (selected_correct_count / correct_count)

                total_points += question.points  # Максимум баллов за этот вопрос

            # Обработка текстового ответа
            elif question.question_type == 'text':
                text_answer = selected_answer.strip()
                UserAnswer.objects.create(
                    question=question,
                    text_answer=text_answer,
                    test_result=test_result
                )
                total_points += question.points  # Максимум баллов за текстовый вопрос
        else:
            # Если нет ответа, то не начисляется балл
            total_points += question.points  # Максимум баллов за этот вопрос (за невыполненный)
    
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
        total_questions = test.question_set.count()
        # Если у нас есть хотя бы один вопрос, вычисляем процент
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
    total_questions = test.question_set.count()

    # Получаем количество правильных ответов и общий балл для теста
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
