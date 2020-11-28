#!/usr/bin/python3
from multiprocessing import Pool
from threading import Lock
import requests
import sys
import time
import random

proxies = {}

def test(proxy, url):
    try:
        r = requests.get(
            url,
            proxies={
                'http': proxy,
                'https': proxy
            },
            timeout=7
        )
        return r.status_code
    except Exception:
        pass
    return 0

def callback(proxy):
    def f(result):
        for code in result:
            print('error code:', code)
        return
        proxies[proxy] = sum(result)
        if proxies[proxy] > 0:
            print('found a legitimate result!')
    return f

if __name__ == '__main__':
    urls = []

    with open(sys.argv[1], 'r') as f_urls:
        for line in f_urls.readlines():
            if line and not line.isspace():
                urls.append(line.strip())

    with open(sys.argv[2], 'r') as f_proxies:
        for line in f_proxies.readlines():
            if line and not line.isspace():
                proxies[line.strip()] = 0

    with Pool(min(50, len(urls) * 3)) as p:
        for idx, proxy in enumerate(proxies.keys()):
            p.starmap_async(test, ((proxy, url) for url in urls), callback=callback(proxy))
            print(idx)
            time.sleep(0.75 + 0.75 * random.random())
        p.close()
        p.join()

    with open(sys.argv[3], 'a') as f:
        for proxy, score in proxies.items():
            f.write('{} {}\n'.format(score, proxy))