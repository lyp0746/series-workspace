# -*- coding: utf-8 -*-
"""DuckDuckGo HTML 结果抽取（标题+链接+摘要），用于定位一手来源，不直接引用。"""
import sys, urllib.request, urllib.parse, re, html
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
def search(q, n=10):
    u='https://html.duckduckgo.com/html/?q='+urllib.parse.quote(q)
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA,'Accept-Language':'en'}),timeout=25)
    chunks=[]
    while True:
        try:
            c=r.read(4096)
        except Exception:
            break
        if not c: break
        chunks.append(c)
    d=b''.join(chunks).decode('utf-8','replace')
    out=[]
    for m in re.finditer(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</a>', d, re.S):
        link=html.unescape(m.group(1)); t=re.sub(r'<[^>]+>','',m.group(2)); s=re.sub(r'<[^>]+>','',m.group(3))
        link=urllib.parse.unquote(re.sub(r'^//duckduckgo.com/l/\?uddg=','',link).split('&rut=')[0])
        out.append((html.unescape(t).strip(), link, html.unescape(s).strip()))
    return out[:n]
if __name__=='__main__':
    for t,l,s in search(' '.join(sys.argv[1:])):
        print('*',t,'\n ',l,'\n ',s[:200],'\n')
