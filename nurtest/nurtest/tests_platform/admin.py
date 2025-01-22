from django.contrib import admin
from .models import Category, Test, Question, AnswerChoice, TestResult, UserAnswer

admin.site.register(Category)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(AnswerChoice)
admin.site.register(TestResult)
admin.site.register(UserAnswer)
