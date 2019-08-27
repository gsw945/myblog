from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from .models import Article, Tag, ToolCategory


def view_index(request):
    context = {}
    context['category_list'] = ToolCategory.objects.filter(display=True).order_by('index').all()
    context['category_tools'] = []
    if context['category_list'].count() > 0:
        context['category_tools'] = context['category_list'].first().tool_set.filter(display=True).order_by('index').all()
    return render(request, 'page-index.html', context)

def view_list(request):
    # 查询参数
    req_data = getattr(request, request.method.upper(), request.POST)
    req_tag = req_data.get('tag', None)
    req_query = req_data.get('query', None)
    # 查询条件
    query = None
    if bool(req_query):
        query = Q(title__icontains=req_query.strip())
        query.add(Q(content__icontains=req_query.strip()), Q.OR)
    if bool(req_tag) and req_tag.isdigit():
        tag_q = Q(tags__id=int(req_tag))
        if query is not None:
            query.add(tag_q, Q.AND)
        else:
            query = tag_q
    # 构造查询
    article_list = Article.objects
    if query is not None:
        article_list = article_list.filter(query)
    article_list = article_list.order_by('-upate_time').all()
    # 分页参数
    page = 1
    req_page = req_data.get('page', None)
    if bool(req_page) and req_page.isdigit():
        page = int(req_page)
    # 分页
    paginator = Paginator(article_list, 15) # 每页显示15条
    if paginator.num_pages < page:
        page = paginator.num_pages
    articles = paginator.get_page(page)
    tags = Tag.objects.all()
    # 渲染
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
