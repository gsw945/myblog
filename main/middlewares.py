import uuid
from datetime import datetime, timedelta

from django.utils.deprecation import MiddlewareMixin
from django.apps import apps


class AnalysisMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        analysis_uid = request.COOKIES.get('analysis_uid')
        # 是否是回头客
        regular = True
        if not analysis_uid:
            regular = False
            analysis_uid = uuid.uuid5(uuid.NAMESPACE_DNS, '').hex
            cookie_kwargs = {
                'expires': datetime.now() + timedelta(days=365),
                'httponly': True
            }
            response.set_cookie('analysis_uid', analysis_uid, **cookie_kwargs)
            
        referer = request.META.get('HTTP_REFERER', None)
        remote_addr = request.META.get('REMOTE_ADDR', None)
        x_real_ip = request.META.get('HTTP_X_REAL_IP', None)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', None)
        host = request.META.get('HTTP_HOST', None)
        remote_host = request.META.get('REMOTE_HOST', None)
        remote_user = request.META.get('REMOTE_USER', None)
        user_agent = request.META.get('HTTP_USER_AGENT', None)
        x_requested_with = request.META.get('HTTP_X_REQUESTED_WITH', None)
        full_url = request.build_absolute_uri()
        dt_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        info = {
            'regular': regular,
            'uid': analysis_uid,
            'method': request.method,
            'url': full_url,
            'referer': referer,
            'remote_addr': remote_addr,
            'x_real_ip': x_real_ip,
            'x_forwarded_for': x_forwarded_for,
            'accept_language': accept_language,
            'host': host,
            'remote_host': remote_host,
            'remote_user': remote_user,
            'user_agent': user_agent,
            'x_requested_with': x_requested_with,
            'dt_str': dt_str
        }
        # print(info)
        AccessAnalysis = apps.get_model('pages', 'AccessAnalysis')
        obj = AccessAnalysis(**info)
        obj.save()

        return response