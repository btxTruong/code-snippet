import getpass
import os
import threading
import time
import requests
import ultils  

CHUCK_SIZE = 1024 * 1024 * 2  # 2MB
DEFAULT_CACHE_DIR = '/home/{}/speedup_download/'.format(getpass.getuser())
CURRENT_SIZE = 0


def now():
    return str(int(time.time()))


def create_template_dir():
    if not os.path.exists(DEFAULT_CACHE_DIR):
        os.mkdir(DEFAULT_CACHE_DIR)

    path = os.path.join(DEFAULT_CACHE_DIR, now())
    os.mkdir(path)

    return path


def on_progress(filesize):
    while True:
        ultils.progress_bar(CURRENT_SIZE, filesize)
        if CURRENT_SIZE == filesize:
            break


def download(url, num_part=5):
    template_path_download = create_template_dir()

    filesize = ultils.get_content_size(url)
    filename = ultils.get_filename_from_url(url)
    range_byte = ultils.get_range_byte(filesize, num_part)  # range header

    monitor_thread = threading.Thread(target=on_progress, args=(filesize,))
    monitor_thread.start()

    part = 1
    threads = []
    for byte_start, byte_end in range_byte:
        filepath = os.path.join(template_path_download,
                                '{}.{:02d}'.format(filename, part))
        part += 1
        thread = threading.Thread(target=download_each_part,
                                  args=(url, byte_start, byte_end, filepath))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print('\n    Download complete')
    ultils.join(template_path_download, filename)


def download_each_part(url, byte_start, byte_end, filepath):
    global CURRENT_SIZE

    headers = {
        'User-Agent': ultils.random_useragent(),
        'Range': "bytes={}-{}".format(byte_start, byte_end)
    }

    with requests.get(url, allow_redirects=True, headers=headers, stream=True) as resp:
        with open(filepath, 'wb') as f:
            for chuck in resp.iter_content(chunk_size=1024 * 1024):
                CURRENT_SIZE += len(chuck)
                f.write(chuck)


if __name__ == '__main__':
    url = 'http://do1.dr-chuck.com/pythonlearn/EN_us/pythonlearn.pdf'

    download(url)
