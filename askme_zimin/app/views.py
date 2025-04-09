from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from app.models import Question, Answer, Tag
from django.db.models import Count, Q, Subquery, OuterRef, IntegerField

popular_tags = Tag.objects.annotate(
    question_count=Count('question')
).order_by('-question_count')[:8]

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
        raise Http404("Страница не найдена")
    
    return page

def index(request):
    
    questions = Question.objects.new()
    page = paginate(questions, request, 5)
    
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page,
        'popular_tags': popular_tags,
    })

def hot(request):
    questions = Question.objects.best() #самые залайканые вопросы
    page = paginate(questions, request, 5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page,
        'popular_tags': popular_tags,
    })

def question(request, question_id):
    try:
        question, answers = Question.objects.get_question_with_answers(question_id)  
        page = paginate(answers, request, 3)
        return render(request, 'single_question.html', {
            'question': question,
            'answers': page.object_list,
            'page_obj': page,
            'popular_tags': popular_tags,
        })
    except Question.DoesNotExist:
        raise Http404("Вопрос не найден")

def ask(request):
    return render(request, 'ask.html', {'popular_tags': popular_tags,})

def profile(request):
    return render(request, 'profile.html', {'popular_tags': popular_tags,})

def login(request):
    return render(request, 'login.html', {'popular_tags': popular_tags,})

def signup(request):
    return render(request, 'registration.html', {'popular_tags': popular_tags,})

def pages_by_tag(request, tag):
    questions = Question.objects.by_tag(tag).order_by('-created_at')
    page = paginate(questions, request, 5)

    if not questions.exists():
        raise Http404("Нет вопросов с этим тегом")
    return render(request, 'questions_by_tag.html', {
        'popular_tags': popular_tags,
        'questions': page.object_list,
        'tag': tag,
        'page_obj': page
    })