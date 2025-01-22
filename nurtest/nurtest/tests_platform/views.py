from django.shortcuts import render, get_object_or_404
from .models import Test, TestResult, AnswerChoice, UserAnswer
from django.contrib.auth.decorators import login_required

# Отображение списка доступных тестов
@login_required
def test_list(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'test/tests.html', {'tests': tests})

# Страница прохождения теста
@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.question_set.all()
    if request.method == 'POST':
        # Обработка ответа на вопросы
        score = 0
        for question in questions:
            selected_answer = request.POST.get(str(question.id))
            if selected_answer:
                answer_choice = AnswerChoice.objects.get(id=selected_answer)
                if answer_choice.is_correct:
                    score += question.points

        # Сохранение результата теста
        result = TestResult.objects.create(
            user=request.user,
            test=test,
            score=score
        )
        return render(request, 'test/test_result.html', {'test': test, 'score': score, 'result': result})

    return render(request, 'test/test_detail.html', {'test': test, 'questions': questions})

# Просмотр результатов теста
@login_required
def test_result(request, result_id):
    result = get_object_or_404(TestResult, id=result_id)
    user_answers = UserAnswer.objects.filter(test_result=result)
    return render(request, 'test/test_result_detail.html', {'result': result, 'user_answers': user_answers})
