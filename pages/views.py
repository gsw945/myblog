from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Article, Tag


def view_index(request):
    context = {}
    return render(request, 'page-index.html', context)

def view_list(request):
    articles = Article.objects.all()
    tags = Tag.objects.all()
    context = {
        'article_list': articles,
        'tag_list': tags
    }
    return render(request, 'article/list.html', context)

def view_detail(request, article_id):
    context = {}
    return render(request, 'article/detail.html', context)

def view_search(request):
    context = {}
    return render(request, 'article/search.html', context)

def view_copyright(request):
    context = {}
    return render(request, 'me/copyright.html', context)

def view_about(request):
    context = {}
    return render(request, 'me/about.html', context)

def view_message(request):
    context = {}
    return render(request, 'me/message.html', context)
