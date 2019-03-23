from matplotlib.font_manager import fontManager
from fontTools.ttLib import TTFont


def char_in_font(unicode_char, ttf_font):
    '''
    from: https://stackoverflow.com/questions/43834362/python-unicode-rendering-how-to-know-if-a-unicode-character-is-missing-from-the/43857892#43857892
    '''
    if isinstance(ttf_font, str):
        font = TTFont(
            file=ttf_font,
            allowVID=True,
            ignoreDecompileErrors=True,
            fontNumber=-1
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
        if char_in_font(char, font.fname)
    ]


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