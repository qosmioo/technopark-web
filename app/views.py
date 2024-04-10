from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404

# Create your views here.
QUESTIONS = [
    {
        "id": i,
        "title": f"Question {i}",
        "text": f"This is question number {i}"
    } for i in range(50)
]


def paginate(request, objects_list, limit=10, pages_count=10):

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404

    paginator = Paginator(objects_list, limit)
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    if not pages_count:
        page_range = paginator.page_range
    else:
        start = page.number - pages_count // 2 - 1
        if start < 0:
            start = 0
        page_range = paginator.page_range[start: page.number + int(pages_count / 2)]
    return page, page_range


def index(request):
    questions = QUESTIONS
    page, page_range = paginate(request, questions, limit=5, pages_count=5)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page': page,
        'page_range': page_range,
        'is_authorized': True
    })


def hot(request):
    questions = QUESTIONS[25:]
    page, page_range = paginate(request, questions, limit=5, pages_count=5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page': page,
        'page_range': page_range,
        'is_authorized': True
    })


def tag(request):
    tag_name = request.GET.get('tag', 1)
    questions = QUESTIONS[25:40]
    page, page_range = paginate(request, questions, limit=5, pages_count=5)
    return render(request, 'hot.html', {
        'tag': tag_name,
        'questions': page.object_list,
        'page': page,
        'page_range': page_range,
        'is_authorized': True
    })


def ask(request):
    return render(request, "ask.html", {'is_authorized': True})


def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, "question.html", {
        'question': item,
        'is_authorized': True
    })


def login(request):
    return render(request, "login.html", {'is_authorized': False})


def signup(request):
    return render(request, "signup.html", {'is_authorized': False})


def settings(request):
    return render(request, "settings.html", {'is_authorized': True})
