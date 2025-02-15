from django.db import models
from accounts.models import CustomUser

# Категория теста
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Тест
class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)  # Поле для популярности
    rating = models.FloatField(default=0.0)  # Поле для рейтинга

    def __str__(self):
        return self.title

# Вопрос
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[
        ('single', 'Один ответ'),
        ('multiple', 'Несколько ответов'),
        ('text', 'Текстовый ответ')
    ])
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.text

# Варианты ответа
class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

# Результаты тестов
class TestResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.user.username} in {self.test.title}"

# Ответ пользователя
class UserAnswer(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Answer for {self.question.text} by {self.test_result.user.username}"