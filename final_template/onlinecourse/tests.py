from django.test import TestCase

# Create your tests here.

from models import Course, Enrollment, Question, Choice, Submission

questions = Question.objects.all()
submission = Submission.objects.first()
choices = submission.choices.all().values_list('pk', flat=True)
print(choices)

print

for question in questions:
    print(question.question)
    choices = Choice.objects.filter(question_id=question.id)
    for choice in choices:
        if choice.is_correct:
            print("green " + choice.choice)
        print(choice.choice)
