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
    for question in questions:
        selected_answer = request.POST.get(str(question.id))
        if selected_answer:
            # Для одиночного ответа (radio)
            if question.question_type == 'single':
                answer_choice = AnswerChoice.objects.get(id=selected_answer)
                if answer_choice.is_correct:
                    score += question.points
                UserAnswer.objects.create(question=question, selected_answer=answer_choice, test_result=test_result)

            # Для множественного ответа (checkbox)
            elif question.question_type == 'multiple':
                selected_answers = request.POST.getlist(str(question.id))
                for answer_id in selected_answers:
                    answer_choice = AnswerChoice.objects.get(id=answer_id)
                    if answer_choice.is_correct:
                        score += question.points
                    UserAnswer.objects.create(question=question, selected_answer=answer_choice, test_result=test_result)

            # Обработка текстового ответа
            elif question.question_type == 'text':
                try:
                    answer_choice = AnswerChoice.objects.get(text=selected_answer)
                    if answer_choice.is_correct:
                        score += question.points
                    UserAnswer.objects.create(question=question, selected_answer=answer_choice, test_result=test_result)
                except AnswerChoice.DoesNotExist:
                    pass
                # text_answer = request.POST.get(str(question.id))
                # if answer_choice is not None:
                #     UserAnswer.objects.create(question=question, selected_answer=answer_choice, test_result=test_result)
                #     # You can alternatively score text answers based on length, keyword presence, or manual review
                #     score += question.points
    return score

# Страница прохождения теста
@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.question_set.all()

    if request.method == 'POST':
        test_result = TestResult.objects.create(user=request.user, test=test, score=0)
        score = process_answers(request, questions, test_result)
        test_result.score = score
        test_result.save()
        return render(request, 'test/test_result.html', {'test': test, 'score': score, 'result': test_result})

    return render(request, 'test/test_detail.html', {'test': test, 'questions': questions})

# Просмотр результатов теста


@login_required
def test_result_detail(request, result_id):
    result = get_object_or_404(TestResult, id=result_id)
    print('wwwww', result, result_id)
    user_answers = UserAnswer.objects.filter(test_result=result)
    print('user_answers', user_answers)
    return render(request, 'test/test_result_detail.html', {'result': result, 'user_answers': user_answers})


@login_required
def test_result(request, result_id):
    result = TestResult.objects.get(id=result_id)
    test = result.test
    score = result.score
    total_questions = test.question_set.count()

    print('result', result)
    print('test', test)
    print('score', score)
    print('total_questions', total_questions)
    # Вычисляем процент
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    return render(request, 'test/test_result.html', {
        'test': test,
        'score': score,
        'percentage': percentage,  # Добавляем процент
        'result': result,
    })

