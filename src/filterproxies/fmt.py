with open('proxies.txt', 'a') as f:
    with open('socks5_proxies.txt', 'r') as tmp:
        for line in tmp.readlines():
            if line and not line.isspace():
                f.write('socks5://' + line)
    with open('http_proxies.txt', 'r') as tmp:
        for line in tmp.readlines():
            if line and not line.isspace():
                f.write('http://' + line)