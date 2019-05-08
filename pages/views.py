from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from .models import Article, Tag


def view_index(request):
    context = {}
    return render(request, 'page-index.html', context)

def view_list(request):
    article_list = Article.objects.order_by('-upate_time').all()
    paginator = Paginator(article_list, 15) # 每页显示15条
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    tags = Tag.objects.all()
    context = {
        'article_list': articles,
        'tag_list': tags
    }
    return render(request, 'article/list.html', context)

def view_detail(request, article_id):
    article_set = Article.objects.filter(id=article_id)
    if article_set.count() > 0:
        article = article_set.first()
        context = {
            'article': article
        }
        return render(request, 'article/detail.html', context)
    raise Http404('博文不存在')

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
