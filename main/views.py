import os
import json
import uuid
import time

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from martor.utils import LazyEncoder


def image_thumbnail(path, width=128, height=None):
    '''
    创建缩略图
    TOOD: 图片尺寸修改和保存
    '''
    from PIL import Image
    img = Image.open(path[0])
    img = img.resize((width, height), Image.ANTIALIAS)
    import ipdb; ipdb.set_trace()
    pass

@login_required
def markdown_uploader(request):
    """
    Makdown image upload for locale storage
    and represent as json to markdown editor.
    """
    if request.method == 'POST' and request.is_ajax():
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            image_size = getattr(image, 'size', getattr(image, '_size', settings.MAX_IMAGE_UPLOAD_SIZE + 1))
            if image_size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_MB = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size) MB.') % {'size': to_MB}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(
                settings.MARTOR_UPLOAD_PATH,
                time.strftime(settings.MARTOR_FOLDER_FORMAT),
                img_uuid
            )
            save_path = os.path.join(settings.MEDIA_ROOT, tmp_file)
            def_path = default_storage.save(save_path, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, tmp_file).replace('\\', '/')
            img_path = def_path
            # image_thumbnail((image, img_path, img_url), width=128) # debug

            data = json.dumps({
                'status': 200,
                'path': img_path,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))
