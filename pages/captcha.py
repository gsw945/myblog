import os
import base64
from io import BytesIO
import string
import random
import pickle

from matplotlib.font_manager import fontManager
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageColor, ImageFilter, ImageFont
from django.conf import settings


def char_in_font(unicode_char, ttf_font):
    '''
    from: https://stackoverflow.com/questions/43834362/python-unicode-rendering-how-to-know-if-a-unicode-character-is-missing-from-the/43857892#43857892
    '''
    if isinstance(ttf_font, str):
        font = TTFont(
            file=ttf_font,
            allowVID=True,
            ignoreDecompileErrors=True,
            fontNumber=1
        )
    else:
        font = ttf_font
    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            if ord(unicode_char) in cmap.cmap:
                return True
    return False

def supported_fonts(char):
    '''
    from: https://stackoverflow.com/questions/18821795/how-can-i-get-list-of-font-familyor-name-of-font-in-matplotlib/18821968#18821968
    '''
    return [
        font.fname for font in fontManager.ttflist
        if os.path.exists(font.fname) and char_in_font(char, font.fname)
    ]

def random_hexdigits(len=1):
    '''
    生成随机生成数字或字母
    '''
    return random.sample(string.hexdigits, len)

def punctuation(len=1):
    '''
    生成干扰字符
    '''
    return tuple(random.sample(string.punctuation, len))

def random_color(min=64, max=255):
    '''
    定义干扰字符颜色
    '''
    return tuple((random.randint(min, max) for i in range(3)))

def fill_color(draw, image, interval):
    '''
    填充颜色
    '''
    for i in range(0, image.width, interval):
        for j in range(0, image.height, interval):
            draw.point((i, j), fill=random_color())

def fill_dischar(draw, image, interval):
    '''
    生成干扰字符
    '''
    for i in range(0, image.width, interval):
        dis = punctuation()
        j = random.randrange(3, image.height // 2 - 3)
        font = ImageFont.truetype(get_rangom_font(), 10)
        draw.text((i, j), dis[0], fill=random_color(64, 255), font=font)

def fill_char(draw, image, num, interval):
    '''
    生成验证码
    '''
    secret = ''
    for i in range(num):
        cha = random_hexdigits()
        secret += str(cha[0])
        j_max = image.height // 4 - 1
        if j_max < 1:
            j_max = 1
        j = random.randrange(0, j_max)
        positon = (image.width * (i / num) + interval, j - 2)
        # print(positon)
        # print(image.size)
        font = ImageFont.truetype(get_rangom_font(), 22)
        draw.text(positon, cha[0], fill=random_color(32, 127), font=font)
    return secret

def generate_image(width=90, height=26, color=(192, 192, 192)):
    '''
    生成验证码图片
    '''
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    fill_color(draw, image, 5)
    fill_dischar(draw, image, 10)
    secret = fill_char(draw, image, 4, 5)
    return image, secret

def image2base64(image):
    buffered = BytesIO()
    image.save(buffered, format='JPEG')
    img_str = 'data:image/jpeg;base64,{0}'.format(
        base64.b64encode(buffered.getvalue()).decode('ascii')
    )
    buffered.close()
    return img_str

def get_rangom_font():
    cache_folder = os.path.join(settings.BASE_DIR, 'cache')
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    font_list_cache = os.path.join(cache_folder, 'font-list.cache')
    font_list = [None]
    if os.path.exists(font_list_cache):
        with open(font_list_cache, 'rb') as fb:
            font_list = pickle.load(fb)
    else:
        font_list = supported_fonts('垚')
        with open(font_list_cache, 'wb') as fb:
            pickle.dump(font_list, fb, pickle.HIGHEST_PROTOCOL)
    return random.choice(font_list)

def web_captcha():
    image, secret = generate_image()
    img_str = image2base64(image)
    image.close()
    return img_str, secret


if __name__ == '__main__':
    from datetime import datetime
    from pprint import pprint
    dt_begin = datetime.now()
    pprint(supported_fonts('垚'))
    dt_end = datetime.now()
    dt_diff = dt_end - dt_begin
    print('begin:', dt_begin.strftime('%Y-%m-%d %H:%M:%S.%f'))
    print('  end:', dt_end.strftime('%Y-%m-%d %H:%M:%S.%f'))
    print('datetime used: {0}.{1} seconds'.format(dt_diff.seconds, dt_diff.microseconds))
    '''
    https://stackoverflow.com/questions/48229318/how-to-convert-image-pil-into-base64-without-saving?rq=1
    https://stackoverflow.com/questions/31826335/how-to-convert-pil-image-image-object-to-base64-string
    '''