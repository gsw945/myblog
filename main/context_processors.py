def request_urls(request):
    urls = {
        'FULL_URL_WITH_QUERY_STRING': request.build_absolute_uri(),
        'FULL_URL': request.build_absolute_uri('?'),
        'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip("/"),
        'ABSOLUTE_ROOT_URL': request.build_absolute_uri('/').strip("/"),
    }
    return urls