#!/usr/bin/env python3
# sort sites from redditdl

import sys
from urllib.parse import urlparse

# sites which don't seem to work properly anymore
broken_sites = [
    'reddituploads.com'
]

# sites which can be downloaded with gallery-dl
gdl_sites = [
    'imgur.com',
    'redgifs.com',
    'pixiv.net',
    'reddit.com',
    'imgflip.com',
    'giphy.com',
    'eroshare.com',
    'erome.com'
]

# hosted sites that can be downloaded with youtube-dl
ytdl_sites = [
    'gfycat.com',
    'pornhub.com',
    'youtube.com',
    'youtu.be',
    'v.redd.it',
    'vidble.com',
    'vimeo.com',
    'xvideos.com',
    'youporn.com',
    'xhamster.com',
    'vid.me',
    'twitter.com',
    't.co',
    'streamable.com'
]

# sites which can be downloaded normally
download_sites = [
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
]

spam_embeds = [
    'discord.gg',
    'discord.com',
    'discordapp.com'
]

def which(url):
    o = urlparse(url.lower())
    hn = o.hostname
    if hn is None:
        return 'broken'
    if any(hn.endswith(site) for site in broken_sites):
        return 'broken'
    if any(hn.endswith(site) for site in download_sites):
        return 'dl'
    if any(hn.endswith(spam) for spam in spam_embeds):
        return 'spam'
    if any(hn.endswith(site) for site in ytdl_sites):
        return 'ytdl'
    if any(hn.endswith(site) for site in gdl_sites):
        return 'gdl'
    if hn.count('.') < 1:
        # http://Hello
        return 'broken'
    if (hn.count('.') == 1) and any(hn.endswith(x) for x in ['gif', 'gifv', 'mov', 'jpg', 'jpeg', 'png', 'mp4', 'mkv', 'heic']):
        # http://IMB_s167Aj.gif
        return 'broken'
    if any(x in hn for x in '[]()+~|*&^%$#@!'):
        # http://[Imgur](http://i.imgur.com/p55trtfuytytfe.jpg)
        return 'broken'
    return 'unknown'

if __name__ == '__main__':
    s = sorted(list(set(x for x in str(sys.stdin.read()).split('\n') if all(ord(c) < 128 for c in x))))
    d = {k: open(k + '.txt', 'w+') for k in ['spam', 'dl', 'ytdl', 'gdl', 'unknown', 'broken']}
    for item in s:
        d[which(item)].write(item + '\n')
    for f in d.values():
        f.close()