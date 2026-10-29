# -*- coding: utf-8 -*-
"""抓取公开页面并保存原文到 raw/（带 UA、超时、编码修正）。"""
import sys, pathlib, urllib.request, gzip, io, re, time
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def get(url, name, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en,zh;q=0.8",
                                               "Accept-Encoding": "gzip"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        txt = data.decode("utf-8", "replace")
    except Exception as e:
        print("FAIL", name, url, e); return None
    html = pathlib.Path("raw") / (name + ".html")
    html.write_text(txt, encoding="utf-8")
    # 去标签的纯文本，便于 grep
    t = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", txt)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = re.sub(r"&nbsp;?", " ", t); t = re.sub(r"&amp;", "&", t)
    t = re.sub(r"&lt;", "<", t); t = re.sub(r"&gt;", ">", t); t = re.sub(r"&quot;", '"', t)
    t = re.sub(r"[ \t\xa0]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
    (pathlib.Path("raw") / (name + ".txt")).write_text(t, encoding="utf-8")
    print("OK  ", name, len(txt), "bytes ->", len(t), "chars")
    return t
if __name__ == "__main__":
    for spec in sys.argv[1:]:
        name, url = spec.split("=", 1)
        get(url, name)
