# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import json
import logging
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Manager, freeze_support
import threading
import os
import sys
import time
try:
    from http.client import RemoteDisconnected
except ImportError:
    from httplib import BadStatusLine as RemoteDisconnected

def is_tool(name):
    """
    Check whether `name` is on PATH and marked as executable.
    from: https://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script/34177358#34177358
    """

    # from whichcraft import which
    from shutil import which

    return which(name) is not None

def win_runas_admin(func):
    '''
    from: https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script/41930586#41930586
    '''
    import ctypes

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if is_admin():
        # Code of your program here
        func()
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )

def pip_exists():
    '''
    check if pip is existed
    '''
    import pkgutil
    return bool(pkgutil.find_loader("pip"))

def reload_module(module_obj):
    '''
    reload module
    '''
    sub_modules = [key for key in sys.modules if key.startswith('prompt_toolkit.')]
    for key in sub_modules:
        sys.modules.pop(key, None)
    #########################################################################
    # ##### import notes #####
    # reload() only reload the module specified, without sub modules
    # module name to reload() must in sys.modules, so it should not be popped
    # sys.modules.pop(module_obj.__name__, None)
    ########################################################################
    try:
        # Python 3.4+
        import importlib
        if hasattr(importlib, 'reload'):
            importlib.reload(module_obj)
        else:
            # Python 3.0~3.3
            import imp
            imp.reload(module_obj)
    except ImportError:
        # Python 2
        reload(module_obj)

is_win = sys.platform == 'win32' or os.name == 'nt'

try:
    import prompt_toolkit
    pt_version = getattr(prompt_toolkit, '__version__', '')
    if not bool(pt_version):
        sys.modules.pop('prompt_toolkit', None)
        raise ImportError('module prompt_toolkit damaged')
    if pt_version.startswith('1'):
        if os.system(sys.executable + ' -m pip install prompt-toolkit --upgrade') != 0:
            if is_tool('conda'):
                if is_win:
                    def conda_upgrade():
                        os.system('conda upgrade prompt_toolkit')
                    win_runas_admin(conda_upgrade)
                else:
                    os.system('sudo ' + sys.executable + ' -m pip install prompt-toolkit')
            else:
                print('plase upgrade [prompt-toolkit] with administrator permission')
        ###########################################################################
        # ##### import notes #####
        # Prompt_toolkit 2.0 is not compatible with 1.0
        # reload() prompt_toolkit will not reload sub modules
        # in file prompt_toolkit.__init__.py:
        #     it self will import some objects from sub modules,
        #     this will lead to ImportError because of compatible problem
        ##########################################################################
        reload_module(prompt_toolkit)
except ImportError:
    if not is_win:
        # only consider APT package system
        pip_package = 'python3-pip' if sys.version_info.major == 3 else 'python-pip'
        if not pip_exists():
            os.system('sudo apt-get install ' + pip_package)
    else:
        os.system(sys.executable + ' -m pip install prompt-toolkit')
    import prompt_toolkit
try:
    import requests
except ImportError:
    os.system(sys.executable + ' -m pip install requests')

from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit import print_formatted_text
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt


from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.keys import Keys
# from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.formatted_text import HTML

class NewRadioList(object):
    """
    List of radio buttons. Only one can be checked at the same time.
    :param values: List of (value, label) tuples.

    modified from: https://github.com/jonathanslenders/python-prompt-toolkit/blob/master/prompt_toolkit/widgets/base.py
    """
    def __init__(self, values):
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(i, tuple) and len(i) == 2
                   for i in values)

        self.values = values
        self.current_value = values[0][0]
        self._selected_index = 0

        # Key bindings.
        kb = KeyBindings()

        @kb.add('up')
        def _(event):
            self._selected_index = max(0, self._selected_index - 1)
            self.current_value = self.values[self._selected_index][0]

        @kb.add('down')
        def _(event):
            self._selected_index = min(
                len(self.values) - 1,
                self._selected_index + 1
            )
            self.current_value = self.values[self._selected_index][0]

        @kb.add(Keys.Any)
        def _(event):
            # We first check values after the selected value, then all values.
            for value in self.values[self._selected_index + 1:] + self.values:
                if value[0].startswith(event.data):
                    self._selected_index = self.values.index(value)
                    return

        # Control and window.
        self.control = FormattedTextControl(
            self._get_text_fragments,
            key_bindings=kb,
            focusable=True)

        self.window = Window(
            content=self.control,
            style='class:radio-list',
            right_margins=[
                ScrollbarMargin(display_arrows=True),
            ],
            dont_extend_height=True)

    def _get_text_fragments(self):
        result = []
        for i, value in enumerate(self.values):
            checked = (value[0] == self.current_value)
            selected = (i == self._selected_index)
            style = ''
            if checked:
                style += ' class:radio-checked'
            if selected:
                style += ' class:radio-selected'

            result.append((style, ''))

            if selected:
                result.append(('[SetCursorPosition]', ''))

            display = value[1]
            if checked:
                result.append((style, '->'))
                display = HTML('<style bg="#999" fg="red">{0}</style>'.format(display))
            else:
                result.append((style, '  '))

            result.append((style, ''))
            result.append(('class:radio', ' '))
            result.extend(to_formatted_text(display, style='class:radio'))
            result.append(('', '\n'))

        result.pop()  # Remove last newline.
        return result

    def __pt_container__(self):
        return self.window


def search_library():
    '''search library with keyword inputed'''
    kw = input('library keyword: ')
    resp = request_get('https://api.cdnjs.com/libraries?search={0}'.format(kw))
    if resp.ok:
        data = json.loads(resp.text)
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
            results = sorted(list(map(lambda item: item['name'], results)), reverse=False)

            completer = WordCompleter(results, ignore_case=True, match_middle=True)
            selected = prompt('choose library: ', completer=completer, complete_while_typing=True)
            if selected in results:
                print('your choice is:', end=' ')
                print_formatted_text(ANSI('\x1b[91m{0}'.format(selected)))
                return selected
            else:
                print('canceled')

def get_assets_list(library):
    '''get assets list of specified library'''
    resp = request_get('https://api.cdnjs.com/libraries/{0}?fields=assets'.format(library))
    if resp.ok:
        data = json.loads(resp.text)
        if isinstance(data, dict) and 'assets' in data:
            return data['assets']

def choose_version(assets):
    '''choose a version from assets list'''
    versions = list(map(lambda item: item['version'], assets))
    # print(versions)
    values = list(map(lambda item: (item, item), versions))
    rdo = NewRadioList(values)

    def do_exit(event):
        # get_app().exit()
        event.app.exit(result=rdo.current_value)
    def do_up_down(event):
        print(event)
        pass
    bindings = KeyBindings()
    bindings.add('enter')(do_exit)
    app_bindings = merge_key_bindings([
        load_key_bindings(),
        bindings
    ])

    selected = Application(layout=Layout(rdo), key_bindings=app_bindings).run()
    if selected in versions:
        print('your choice is:', end=' ')
        # refer: https://github.com/jonathanslenders/python-prompt-toolkit/blob/master/examples/print-text/ansi.py
        print_formatted_text(ANSI('\x1b[91m{0}'.format(selected)))
        return selected
    else:
        print('canceled')

def filter_version_list(assets, version):
    '''get files list of specified version'''
    selected = list(filter(lambda item: item['version'] == version, assets))
    return selected[0]['files']

def do_download(library, version, version_files, concurrency=3, retries=3):
    '''download files with multiple threads'''
    manager = Manager()
    share = manager.dict()
    lock = threading.Lock()
    tpool = ThreadPool(concurrency)
    data_len = len(version_files)
    data = list(map(lambda item: (library, version, item, share, lock, data_len, retries), version_files))
    tresult_proxy = tpool.map_async(download_item, data)
    tpool.close()
    tpool.join()
    result = tresult_proxy.get()

def download_item(args):
    '''download one item of files'''
    root_folder = os.getcwd()
    (library, version, url, share, lock, data_len, retries) = args
    folder = os.path.join(root_folder, library, version)
    base_url = 'https://cdnjs.cloudflare.com/ajax/libs/{0}/{1}/'.format(library, version)
    item_url = base_url + url
    # from: http://docs.python-requests.org/zh_CN/latest/user/quickstart.html#id4
    req_time = 0
    while retries > req_time:
        req_time += 1
        try:
            resp = request_get(item_url)
        except RemoteDisconnected:
            print('RemoteDisconnected: retry[{0}/{1}]'.format(req_time, retries))
            continue
        else:
            break
    item_status = False
    if resp.ok:
        item_path = url.replace('/', os.sep)
        full_path = os.path.join(folder, item_path)
        file_folder = os.path.dirname(full_path)
        if not os.path.exists(file_folder) or not os.path.isdir(file_folder):
            # from https://stackoverflow.com/questions/20790580/python-specifically-handle-file-exists-exception/20790635#20790635
            try:
                # FileExistsError error may appear because  of multiple threads concurrency
                os.makedirs(file_folder)
            except OSError as err:
                import errno
                if err.errno == errno.EEXIST:
                    pass
        with open(full_path, 'wb') as fw:
            fw.write(resp.content)
        item_status = True
    else:
        print(resp.status_code, end=' -> ')
        print(item_url)
    lock.acquire()
    share[url] = item_status
    share_len = len(share)
    lock.release()
    time.sleep(0.05)
    # print(share)
    print('{0:2}/{1:2}'.format(share_len, data_len), end=' -> ')
    print(url)

def request_get(url):
    '''requests.get() with options'''
    headers = {
        'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    return requests.get(url, headers=headers)

def setup_log():
    '''setup log for requests'''
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def main(debug=False, retries=3):
    '''main call function'''
    if debug:
        setup_log()
    library = search_library()
    if bool(library):
        assets = get_assets_list(library)
        if bool(assets):
            version = choose_version(assets)
            if bool(version):
                version_files = filter_version_list(assets, version)
                if bool(version_files):
                    concurrency = 10 # concurrency count
                    do_download(
                        library, version, version_files,
                        concurrency=concurrency, retries=retries
                    )


if __name__ == '__main__':
    freeze_support()
    main(debug=True) # you can close log here