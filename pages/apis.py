from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from ipware import get_client_ip
from ratelimit.decorators import ratelimit
from easy_thumbnails.files import get_thumbnailer

from .models import ArticleAnalysis, Article, Message, ToolCategory
from .captcha import  web_captcha


def is_email(email_str):
    try:
        validate_email(email_str)
        valid_email = True
    except validate_email.ValidationError:
        valid_email = False
    return valid_email

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

@ratelimit(key=ratelimit_key, rate='250/d', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='60/h', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='1/25s', method=ratelimit.ALL, block=False)
def api_article_analysis(request):
    '''
    250/d: 每天250次限制
    60/h: 每小时60次限制
    1/25s: 每25秒一次限制
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
                    'desc': '统计成功',
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

@ratelimit(key=ratelimit_key, rate='300/d', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='60/h', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='1/3s', method=ratelimit.ALL, block=False)
def api_generate_captcha(request):
    '''
    300/d: 每天300次限制
    60/h: 每小时60次限制
    1/2s: 每2秒一次限制
    '''
    # 是否被限制
    is_limited = getattr(request, 'limited', False)
    if is_limited:
        ret = {
            'error': 1,
            'desc': '访问过于频繁，请稍后再试'
        }
    else:
        img_str, secret = web_captcha()
        request.session['captcha_secret'] = secret
        request.session.modified = True
        ret = {
            'error': 0,
            'desc': '获取验证码成功',
            'data': img_str
        }
    return JsonResponse(ret)

@ratelimit(key=ratelimit_key, rate='60/d', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='12/h', method=ratelimit.ALL, block=False)
@ratelimit(key=ratelimit_key, rate='1/12s', method=ratelimit.ALL, block=False)
def api_leave_message(request):
    '''
    60/d: 每天60次限制
    12/h: 每小时12次限制
    1/12s: 每12秒一次限制
    '''
    # 是否被限制
    is_limited = getattr(request, 'limited', False)
    if is_limited:
        ret = {
            'error': 1,
            'desc': '访问过于频繁，请稍后再试'
        }
    else:
        req_data = getattr(request, request.method.upper(), request.POST)
        email = req_data.get('email', None)
        content = req_data.get('content', None)
        reply = req_data.get('reply', 'false')
        captcha = req_data.get('captcha', None)
        if all([email, content, captcha]):
            if is_email(email):
                secret = request.session.get('captcha_secret', None)
                if bool(secret):
                    try:
                        del request.session['captcha_secret']
                        request.session.modified = True
                    except KeyError:
                        pass
                    if secret.lower() == captcha.lower():
                        reply = reply.lower() in ('1', 'true')
                        obj = Message(email=email, content=content, reply=reply)
                        obj.save()
                        ret = {
                            'error': 0,
                            'desc': '留言成功'
                        }
                    else:
                        ret = {
                            'error': 4,
                            'desc': '验证码错误'
                        }
                else:
                    ret = {
                        'error': 3,
                        'desc': '验证码已过期'
                    }
            else:
                ret = {
                    'error': 2,
                    'desc': '邮箱格式有误'
                }
        else:
            error_msg = '参数错误, 请填写[{}]'
            if not bool(email):
                error_msg = error_msg.format('邮箱')
            if not bool(content):
                error_msg = error_msg.format('留言内容')
            if not bool(captcha):
                error_msg = error_msg.format('验证码')
            ret = {
                'error': 1,
                'desc': error_msg
            }
    return JsonResponse(ret)

def api_category_tools(request):
    req_params = getattr(request, request.method.upper(), request.POST)
    req_category = req_params.get('category', None)
    ret = {}
    if bool(req_category):
        if req_category.isdigit():
            category_id = int(req_category)
            obj = ToolCategory.objects.filter(pk=category_id).first()
            if isinstance(obj, ToolCategory):
                tools = obj.tool_set.filter(display=True).order_by('index').all()
                rows = []
                # refer: https://easy-thumbnails.readthedocs.io/en/stable/usage/#python
                thumbnail_options = {
                    'quality': 100,
                    'subsampling': 2,
                    'autocrop': False,
                    'bw': False,
                    'replace_alpha': '#fff',
                    'detail': False,
                    'sharpen': False,
                    'crop': 'scale',
                    'upscale': True
                }
                thumbnail_options.update({'size': (58, 58)})
                for tool in tools:
                    thumbnailer = get_thumbnailer(tool.cover)
                    thumb = thumbnailer.get_thumbnail(thumbnail_options)
                    tool_json = {
                        'detail': tool.detail,
                        'name': tool.name,
                        'cover': {
                            'url': thumb.url,
                            'width': thumb.width,
                            'height': thumb.height
                        },
                        'name': tool.name,
                        'intro': tool.intro
                    }
                    rows.append(tool_json)
                ret = {
                    'error': 0,
                    'desc': None,
                    'rows': rows
                }
            else:
                ret = {
                    'error': 3,
                    'desc': '请求的[category]不存在'
                }
        else:
            ret = {
                'error': 2,
                'desc': '参数[category]错误'
            }
    else:
        ret = {
            'error': 1,
            'desc': '参数[category]缺失'
        }
    return JsonResponse(ret)
