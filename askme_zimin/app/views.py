import copy
import random
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

number_answers = 50

QUESTIONS = [
    {
        'title': f'Title {i+1}',
        'id': i,
        'like': random.randint(0, 30),
        'dislike': random.randint(0, 30),
        'text': f'This is text for question = {i+1}',
        'number_answers': number_answers
    } for i in range(30)
]

ANSWERS = [
    {
        'text': f'This is answer number = {i+1}',
        'like': random.randint(0, 30),
        'dislike': random.randint(0, 30),
        'id': i
    } for i in range(number_answers)
] 

def paginate(objects_list, request, per_page=10):
    try:
        page_num = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page_num = 1
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        if page_num < 0:
            page = paginator.page(1)
        else:
            page = paginator.page(paginator.num_pages)
    return page



    return page

def index(request):
    page = paginate(QUESTIONS, request, 5)
    return render(request, template_name='index.html', context={'questions': page.object_list, 'page_obj': page})

def hot(request):
    q = QUESTIONS[::-1]
    page = paginate(q, request, 5)
    return render(request, template_name='hot.html', context={'questions': page.object_list, 'page_obj': page})

def question(request, question_id):
    page = paginate(ANSWERS, request, 3)
    return render(request, template_name='single_question.html', context={'question': QUESTIONS[question_id], 'answers': page.object_list, 'page_obj': page})

def ask(request):
    return render(request, template_name='ask.html')

def profile(request):
    return render(request, template_name='profile.html')

def login(request):
    return render(request, template_name='login.html')

def signup(request):
    return render(request, template_name='registration.html')

def pages_by_tag(request, tag):
    page = paginate(QUESTIONS, request, 5)
    return render(request, template_name='questions_by_tag.html', context={'questions': page.object_list, 'tag': tag, 'page_obj': page})

