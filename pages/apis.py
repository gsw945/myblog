from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from ipware import get_client_ip
from ratelimit.decorators import ratelimit

from .models import ArticleAnalysis, Article


def ratelimit_key(group, request):
    req_article = getattr(request, 'req_article', None)
    if bool(req_article):
        client_ip = getattr(request, 'client_ip', None)
        is_routable = getattr(request, 'is_routable', None)
    else:
        # 获取访客端IP
        client_ip, is_routable = get_client_ip(request)
        # 获取请求参数中的博文ID
        req_article = getattr(request, request.method.upper(), request.POST).get('article', None)
        # 判断博文ID有效性
        if not (bool(req_article) and req_article.isdigit()):
            req_article = None
        # 附加属性到request，让后续的视图函数中可以使用
        setattr(request, 'req_article', req_article)
        setattr(request, 'client_ip', client_ip)
        setattr(request, 'is_routable', is_routable)
    return '{0}-{1}-{2}'.format(client_ip, group, req_article)

@ratelimit(key=ratelimit_key, rate='60/d', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='12/h', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='1/12s', method=ratelimit.ALL, block=False)
def api_article_analysis(request):
    '''
    60/d: 每天60次限制
    12/h: 每小时12次限制
    1/12s: 每12秒一次限制
    '''
    # 是否被限制
    is_limited = getattr(request, 'limited', False)
    if is_limited:
        ret = {
            'error': 3,
            'desc': '访问过于频繁，请稍后再试'
        }
    else:
        # 博文id
        req_article = getattr(request, 'req_article', None)
        if bool(req_article):
            article_id = int(req_article)
            # 根据博文id查询博文对象
            article = Article.objects.filter(pk=article_id).first()
            if isinstance(article, Article):
                client_ip = getattr(request, 'client_ip', None)
                is_routable = getattr(request, 'is_routable', None)
                # 新的博文访问记录
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
