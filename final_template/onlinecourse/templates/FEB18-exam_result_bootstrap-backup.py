<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    {% load static %}
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>

 <nav class="navbar navbar-light bg-light">
    <div class="container-fluid">
        <div class="navbar-header">
              <a class="navbar-brand" href="{% url 'onlinecourse:index' %}">Home</a>
        </div>
        <ul class="nav navbar-nav navbar-right">
            {% if user.is_authenticated %}
            <li>
                <a class="btn btn-link" href="#">{{ user.first_name }}({{ user.username }})</a>
                <a class="btn btn-link" href="{% url 'onlinecourse:logout' %}">Logout</a>
            </li>
            {% else %}
            <li>
                <form class="form-inline" action="{% url 'onlinecourse:login' %}" method="post">
                    {% csrf_token %}
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="Username" name="username" >
                        <input type="password" class="form-control" placeholder="Username" name="psw" >
                        <button class="btn btn-primary" type="submit">Login</button>
                        <a class="btn btn-link" href="{% url 'onlinecourse:registration' %}">Sign Up</a>
                    </div>
                </form>
            </li>
            {% endif %}
        </ul>
    </div>
</nav>

<div class="container-fluid">
    {% if grade > 80 %}
    <div class="alert alert-success">
       <!--HINT Display passed info -->
       <strong> Congradulations, {{ user }}!</strong> You have passed the exam and completed the course with score
       {{ grade }} / 100
    </div>
        {% else %}
        <div class="alert alert-danger">
            <!--HINT Display failed info -->
            <strong>Failed</strong> Sorry, {{ user }}! You have failed exam with score {{ grade }} / 100
        </div>
        <a class="btn btn-link text-danger" href="{% url 'onlinecourse:course_details' course.id %}">Re-test</a>
        {% endif %}
        <div class="card-columns-vertical mt-1">
        <h5 class="">Exam results</h5>
            <!--HINT Display exam results-->
            {{choices}}
        </div>
    </div>
</body>
</html>


from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import context
# <HINT> Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id

    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result', args=(course_id, submission_id,)))

# <HINT> A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(Choice.objects.get(id=choice_id))
    return submitted_answers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()

    exam_score = 0
    for choice in choices:
        if choice.is_correct:
            exam_score += int(choice.question.grade)
    context['course'] = course
    context['grade'] = exam_score
    context['choices'] = choices

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
    

def get_grades(course_id):
    course = Course.objects.get(pk=course_id)
    questions = course.question_set.all()
    total_grades = 0
    for question in questions:
        total_grades += question.grade
    
    return total_grades
