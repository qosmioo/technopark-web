import re
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from questions.forms import AskForm, LoginForm, SignUpForm, UserSettingsForm
from questions.models import Question, Tag


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
    questions = Question.objects.last_questions()
    page, page_range = paginate(request, questions, limit=5, pages_count=5)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page': page,
        'page_range': page_range,
    })


def hot(request):
    questions = Question.objects.hot_questions()
    page, page_range = paginate(request, questions, limit=5, pages_count=5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page': page,
        'page_range': page_range,
    })


def tag(request, tag_name):
    # tag_name = request.GET.get('tag', 1)
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = tag_obj.question_set.last_questions
    # questions = list(Question.objects.questions_by_tag(tag_obj))
    page, page_range = paginate(request, questions, limit=5, pages_count=5)
    return render(request, 'hot.html', {
        'tag': tag_obj,
        'questions': page.object_list,
        'page': page,
        'page_range': page_range,
    })


# def ask(request):
#     return render(request, "ask.html", {'is_authorized': True})

@login_required(login_url='/login', redirect_field_name='continue')
def ask(request):
    if request.method == "POST":
        form = AskForm(request.user, request.POST)
        if form.is_valid():
            question_item = form.save()
            return HttpResponseRedirect('/question/' + str(question_item.pk))
    else:
        form = AskForm(request.user)
    return render(request, 'ask.html', {
        'form': form,
    })


def question(request, question_id):
    item = get_object_or_404(Question, id=question_id)
    return render(request, "question.html", {
        'question': item,
        'is_authorized': True
    })


def get_continue(request, default='/'):
    url = request.GET.get('continue', default)
    if re.match(r'^/|http://127\.0\.0\.', url):   # Защита от Open Redirect
        return url
    return default


def login(request):
    url = get_continue(request)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.auth())
            return HttpResponseRedirect(url)
    else:
        form = LoginForm()
    return render(request, 'login.html', {
        'form': form,
        'continue_url': url,
    })


def signup(request):
    url = get_continue(request)
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login?continue=' + url)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {
        'form': form,
        'continue_url': url
    })


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(get_continue(request))


@login_required(login_url='/login', redirect_field_name='continue')
def settings(request):
    user = request.user
    if request.method == "POST":
        form = UserSettingsForm(user, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/settings')
    else:
        form = UserSettingsForm(user, initial={'email': user.email,
                                               'nick_name': user.profile.nick_name,
                                               'avatar': user.profile.avatar})
    return render(request, 'settings.html', {
        'form': form,
    })
