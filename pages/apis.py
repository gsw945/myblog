from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from ipware import get_client_ip
from ratelimit.decorators import ratelimit

from .models import ArticleAnalysis, Article


def ratelimit_key(group, request):
    client_ip, is_routable = get_client_ip(request)
    req_article = getattr(request, request.method.upper(), request.POST).get('article', None)
    if not (bool(req_article) and req_article.isdigit()):
        req_article = None
    setattr(request, 'req_article', req_article)
    setattr(request, 'client_ip', client_ip)
    setattr(request, 'is_routable', is_routable)
    return '{0}-{1}-{2}'.format(client_ip, group, req_article)

@ratelimit(key=ratelimit_key, rate='1/10s', method=ratelimit.ALL, block=False)
def api_article_analysis(request):
    is_limited = getattr(request, 'limited', False)
    if is_limited:
        ret = {
            'error': 3,
            'desc': '访问过于频繁，请稍后再试'
        }
    else:
        req_article = getattr(request, 'req_article', None)
        if bool(req_article):
            article_id = int(req_article)
            article = Article.objects.filter(pk=article_id).first()
            if isinstance(article, Article):
                client_ip = getattr(request, 'client_ip', None)
                is_routable = getattr(request, 'is_routable', None)
                obj = ArticleAnalysis(article=article, client_ip=client_ip, is_routable=is_routable)
                obj.save()
                ret = {
                    'error': 0,
                    'desc': 'ok',
                    'debug': obj.id
                }
            else:
                ret = {
                    'error': 1,
                    'desc': '参数[article]不存在'
                }
        else:
            ret = {
                'error': 2,
                'desc': '参数[article]错误'
            }
    return JsonResponse(ret)
