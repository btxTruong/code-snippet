import os
import random
import shutil
from contextlib import contextmanager
from datetime import datetime
from urllib.parse import unquote, urlparse

import requests


@contextmanager
def time_running():
    started = datetime.now()
    try:
        yield
    finally:
        print('Download finished in {}'.format(datetime.now() - started))


def join(fromdir, tofile, readsize=1024):
    parts = os.listdir(fromdir)
    parts.sort()

    file = os.path.join(fromdir, tofile)
    with open(file, 'wb') as fw:
        for tempfile in parts:
            filepath = os.path.join(fromdir, tempfile)
            with open(filepath, 'rb') as fr:
                while True:
                    data = fr.read(readsize)
                    if not data:
                        break
                    fw.write(data)
            os.remove(filepath)


def clear(fromdir):
    shutil.rmtree(fromdir)


def random_useragent():
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) "
        "Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) "
        "Gecko/20100101 Firefox/65.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) "
        "Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) "
        "Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) "
        "Gecko/20100101 Firefox/65.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
    )
    return random.choice(user_agents)


def get_content_size(url):
    r = requests.get(url)
    return int(r.headers.get('Content-Length', 0))


def get_range_byte(totalsize, num_part):
    """  byte-range in headers"""
    chuck = round(totalsize / num_part)

    range_size = []
    byte_start = 0
    for i in range(num_part):
        byte_end = byte_start + chuck
        if byte_end > totalsize:
            byte_end = totalsize
        range_size.append((byte_start, byte_end))
        byte_start += chuck + 1
    return range_size


def get_filename_from_url(url):
    """name of file download"""
    return os.path.basename(unquote(urlparse(url).path))


def fmt_bytes(size):
    """convert bytes to other unit"""
    if size < 0:
        raise ValueError('Size not negative')
    units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB']
    for u in units:
        if size < 1024:
            return '{:.2f} {}'.format(size, u)
        size /= 1024
    return '{:.2f} YB'.format(size)


def progress_bar(current_size, total_size, scale=0.3):
    _, cols = get_terminal_size()
    width = int(cols * scale)
    filled = round(width * current_size / total_size)
    bar = '#' * filled + '-' * (width - filled)
    percent = round(100 * current_size / total_size, 1)
    suffix = ' '  # remove overlap if current line shorter previous line
    out = '  {}/{} [{}] {}%{}'.format(fmt_bytes(current_size),
                                      fmt_bytes(total_size),
                                      bar,
                                      percent,
                                      suffix * 5)
    print(out, end='\r')


def get_terminal_size():
    row, columns = os.popen('stty size').read().split()
    return int(row), int(columns)
