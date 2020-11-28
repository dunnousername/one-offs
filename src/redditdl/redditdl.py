#!/usr/bin/env python3
# a tool to scrape image datasets from reddit using pushshift.io
# gives a file with a list of links to image files downloadable using aria2c, wget or curl, as well as gallery_dl and youtube_dl
# requires requests, gallery_dl and youtube_dl

import argparse
import collections
import re
import sys
import json
import time
from urllib.parse import urlparse

import requests

import youtube_dl
import gallery_dl

_image_re = re.compile(r'^https:\/\/preview.redd.it\/([a-zA-Z0-9]+\.[a-zA-Z0-9]+)')
def url_before(subreddit, before):
    return 'https://api.pushshift.io/reddit/submission/search/?subreddit={}&is_self=false&sort_type=created_utc&sort=desc&before={}'.format(subreddit, before)

def loop_results(subreddit, start, period):
    ts = int(start)
    results = []
    while True:
        url = url_before(subreddit, ts)
        results = requests.get(url).json()['data']
        if not results:
            break
        ts = results[-1]['created_utc']
        yield from results
        time.sleep(period)

def loop_media(subreddit, start, period):
    for result in loop_results(subreddit, start, period):
        try:
            if ('is_video' in result.keys()) and result['is_video']:
                yield (result['full_link'], result['created_utc'])
            else:
                if 'media' in result.keys():
                    if 'oembed' in result['media'].keys():
                        if 'type' in result['media']['oembed'].keys():
                            if result['media']['oembed']['type'] == 'video':
                                yield (result['url'], result['created_utc'])
                                continue
                if not result['url'].startswith('https://www.reddit.com/gallery'):
                    yield (result['url'], result['created_utc'])
                    continue
                for item in result['media_metadata'].values():
                    f = _image_re.match(item['s']['u']).group(1)
                    yield ('https://i.redd.it/' + f, result['created_utc'])
        except Exception as e:
            print(repr(e))

def url_valid(url_):
    url = urlparse(url_)
    if url.hostname is None:
        return False
    if any(x in url.hostname for x in '!@#$%^&*()[]{};'):
        return False
    return True

def is_spam(url):
    return any(url.startswith('https://' + x) or url.startswith('http://' + x) for x in [
        'discord.gg',
        'discord.com/invite',
        'discordapp.com/invite'
    ])

def http_supports(url):
    hostname = urlparse(url).hostname
    if hostname is None:
        return False
    return any(hostname.endswith(x) for x in [
        'i.redd.it',
        'i.imgur.com',
        'media.tumblr.com',
        'i.eroshare.com',
        'media.giphy.com',
        'media0.giphy.com',
        'media1.giphy.com',
        'media2.giphy.com',
        'media3.giphy.com',
        'cdn.discordapp.com',
        'cdn.discord.com',
        'i.redditmedia.com'
    ])

def gallery_supports(url):
    try:
        return gallery_dl.extractor.find(url) is not None
    except Exception as e:
        print(repr(e))
        return False

youtube_valid_extractors = [e for e in youtube_dl.extractor.list_extractors(21) if not any(e.suitable(x) for x in [
    'thisisnotarealurl.com',
    'a.x',
    'https://begr.ugw',
    '192.168.1.1',
    'http://fea.cd'
])]

def youtube_supports(url):
    try:
        return any(e.suitable(url) for e in youtube_valid_extractors)
    except Exception as e:
        print(repr(e))
        return False

def main(subreddit, f_f, g_f, y_f, u_f, start, period, seen):
    last_ts = start
    try:
        for idx, (url, ts) in enumerate(loop_media(subreddit, start, period)):
            if any(ord(c) >= 128 for c in url):
                print('url {} contains non-ASCII characters; skipping'.format(url))
            elif not url_valid(url):
                print('url {} is invalid; skipping'.format(url))
            elif is_spam(url):
                print('url {} is spam; skipping'.format(url))
            elif hash(url.strip()) not in seen:
                seen.add(hash(url.strip()))
                if http_supports(url):
                    print(url)
                    f_f.write(url + '\n')
                elif gallery_supports(url):
                    print(url)
                    g_f.write(url + '\n')
                elif youtube_supports(url):
                    print(url)
                    y_f.write(url + '\n')
                else:
                    print(url)
                    u_f.write(url + '\n')
            else:
                print('url {} already seen; skipping').format(url)
            if not (idx % 100):
                print('flushing...')
                f_f.flush()
                g_f.flush()
                y_f.flush()
                u_f.flush()
            last_ts = ts
    except Exception as e:
        print('failed at timestamp {}'.format(last_ts))
        return (last_ts, e, seen)
    except KeyboardInterrupt as e:
        print('stopping at timestamp {}'.format(last_ts))
        raise e
    else:
        return (0, None, seen)
    finally:
        f_f.close()
        g_f.close()
        y_f.close()
        u_f.close()

test_url = 'https://api.pushshift.io/reddit/submission/search?subreddit=help'

def test_pushshift():
    try:
        assert len(requests.get(test_url).json()['data']) > 0
    except Exception as e:
        print('pushshift isn\'t working...')
        return False
    else:
        return True

parser = argparse.ArgumentParser(description='Download media links from reddit using pushshift.io')
parser.add_argument('subreddit', help='subreddit to download')
parser.add_argument('-f', '--file_output', help='HTTP GET-able output file', default='dl.txt')
parser.add_argument('-g', '--gallery_output', help='gallery-dl output file', default='gallery.txt')
parser.add_argument('-y', '--youtube_output', help='youtube-dl output file', default='youtube.txt')
parser.add_argument('-u', '--unknown_output', help='unknown output file', default='unknown.txt')
parser.add_argument('-s', '--start', help='timestamp to start downloading from', default=-1, type=int)
parser.add_argument('-r', '--retry', help='retry upon JSONDecodeError', action='store_true')
parser.add_argument('-R', '--rate', help='how many requests to make per second (max 1.0, default 0.5)', default=0.5, type=float)
args = parser.parse_args()

if __name__ == '__main__':
    start = time.time()
    if args.start >= 0:
        start = args.start
    retry = args.retry
    if (args.rate > 1.0) or (args.rate <= 0.0):
        print('Error: --rate must be in the range (0.0, 1.0]')
        sys.exit(1)
    period = 1.0 / args.rate
    if not all(x.isalnum() or (x in ['-', '_']) for x in args.subreddit):
        print('Error: subreddit must be in [a-zA-Z0-9_\\-]')
        sys.exit(1)
    subreddit = args.subreddit
    f_fn = args.file_output
    g_fn = args.gallery_output
    y_fn = args.youtube_output
    u_fn = args.unknown_output

    
    seen = set()

    while True:
        for fn in [f_fn, g_fn, y_fn, u_fn]:
            try:
                with open(fn, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.isspace() or line.startswith('#'):
                            continue
                        seen.add(hash(line))
            except FileNotFoundError:
                continue

        o = lambda fn: open(fn, 'a')
        (last_ts, e, seen) = main(subreddit, o(f_fn), o(g_fn), o(y_fn), o(u_fn), start, period, seen)
        if e is None:
            break
        if retry and isinstance(e, json.decoder.JSONDecodeError):
            start = last_ts
            backoff = max(period, 30)
            time.sleep(backoff)
            while not test_pushshift():
                backoff *= 1.5
                time.sleep(backoff)
            print('pushshift is up again; continuing')
        else:
            raise e
