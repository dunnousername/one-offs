#!/usr/bin/env python3
# get the average size of a file in a list
# requires requests and tqdm

import argparse
import random
import time

import requests
from tqdm import tqdm

parser = argparse.ArgumentParser(description='get the average size of a file in a list using HTTP HEAD requests')
parser.add_argument('list', help='path to list file')
parser.add_argument('--samples', help='sample size', default=5000, type=int)
parser.add_argument('--sleep', help='sleep interval', default=1.0, type=float)
args = parser.parse_args()

def get_length(url):
    try:
        resp = requests.head(url, allow_redirects=True)
        length = int(resp.headers['content-length'])
        if length == 0:
            print('warning: content-length is zero and status code is {}'.format(resp.status_code))
        return length
    except Exception as e:
        print('warning: received {} error while trying to download {}. Results may be inaccurate.'.format(e, url))
        return 0

if __name__ == "__main__":
    with open(args.list, 'r') as f:
        lines = [line for line in f.readlines() if not line.isspace()]
    random.shuffle(lines)
    lines = lines[:args.samples]
    print(lines[:100])
    total = 0
    total_samples = 0
    for url in tqdm(lines):
        length = get_length(url)
        if length:
            total += length
            total_samples += 1
        time.sleep(args.sleep)
    print('Average file size is {:.2f}B. {}/{} of files worked ({:.3f}%).'.format(total / total_samples, total_samples, len(lines), total_samples / len(lines) * 100.0))