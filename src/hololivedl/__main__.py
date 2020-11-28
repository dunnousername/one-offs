import re
import requests
import time
import threading
import youtube_dl
import random

waifus = set([])
online = set([])

class TrashCan(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

def check_online(waifu):
    regex = r'https://(?:www\.)?youtube\.com/embed/live_stream\?channel=(?:[a-zA-Z0-9\-_]+)'
    if re.match(regex, waifu) is not None:
        try:
            r = requests.get(waifu)
            regex2 = r'<link rel="canonical" href="(?P<href>[^"]+)">'
            tmp = re.search(regex2, r.text)
            if tmp is not None:
                return tmp['href']
        except Exception:
            pass
        return None

def download(waifu, url):
    ytdl = youtube_dl.YoutubeDL({
        'nopart': True,
        'quiet': True
    })
    ytdl.download([url])
    online.remove(waifu)

yt_regex = r'https://(?:www\.)?youtube\.com/channel/(?:[a-zA-Z0-9\-_]+)'

with open('waifus.txt', 'r') as f:
    for raw_line in f:
        line = raw_line.strip()
        if not line or line.startswith('#') or line.isspace():
            continue
        match = re.match(yt_regex, line)
        if match is not None:
            r = requests.get(line)
            if r.ok:
                regex = r'<link rel="canonical" href="https://(?:www\.)?youtube.com/channel/(?P<id>[^"]+)">'
                g = re.search(regex, r.text)
                url = 'https://www.youtube.com/embed/live_stream?channel={}'.format(g['id'])
                waifus.add(url)
                print('added', line)
                #time.sleep(0.5)
                continue
        raise ValueError('invalid url')

print('done initializing')

main_ytdl = youtube_dl.YoutubeDL({
    'quiet': True,
    'no_warnings': True,
    'logger': TrashCan()
})

while True:
    for waifu in waifus:
        if waifu not in online:
            tmp = check_online(waifu)
            if tmp is not None:
                try:
                    main_ytdl.extract_info(tmp, download=False)
                    print('A waifu is online! {}'.format(waifu))
                    online.add(waifu)
                    threading.Thread(target=download, args=[waifu, tmp]).start()
                except youtube_dl.utils.ExtractorError:
                    pass
                except youtube_dl.utils.DownloadError:
                    pass
                finally:
                    time.sleep(2.0 + 1.5 * random.random())