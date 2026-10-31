import subprocess, io, re
G = r"D:\Git\cmd\git.exe"
ROOT = r"D:\0_Article\distinction-evolution"
def old(f, rev="HEAD~2"):
    r = subprocess.run([G, "show", "%s:source/%s" % (rev, f)], capture_output=True, cwd=ROOT)
    return r.stdout.decode("utf-8", "ignore")
def secs(html):
    out = []
    for p in re.split(r"(?=<h3)", html):
        m = re.match(r"<h3[^>]*>(.*?)</h3>", p, re.S)
        if m:
            out.append((re.sub(r"<[^>]+>", "", m.group(1)).strip(), p))
    return out
BAN = ["初稿", "原稿", "归并", "降级", "补编", "待定", "上一稿", "此前"]
def clean(b):
    keep = []
    for p in re.split(r"(?=<p|<ul|<table|<div|<h4)", b):
        if any(w in p for w in BAN):
            continue
        keep.append(p)
    t = "".join(keep)
    return re.sub(r"<h3[^>]*>.*?</h3>", "", t, flags=re.S).strip()
def pick(S, keys):
    return "".join(clean(v) for k, v in S if any(x in k for x in keys))
def renumber(block, oldch, newch, start):
    n = [start - 1]
    def rep(m):
        n[0] += 1
        return "%d.%d" % (newch, n[0])
    block = re.sub(r"\b%d\.(\d+)\b" % oldch, rep, block)
    block = re.sub(r"第\s*%d\s*章" % oldch, "本章", block)
    block = re.sub(r"第\s*\d+\s*[—－-]\s*\d+\s*章", "本书相关章节", block)
    return block

S7, S10, S20, S28 = secs(old("ch07.html")), secs(old("ch10.html")), secs(old("ch20.html")), secs(old("ch28.html"))
JOBS = [
    ("ch13.html", 7, 13, 8, "13.7", "第四套工具：外微分与一个公式统摄四个积分定理", ["冗余层次", "外微分", "斯托克斯", "反例"]),
    ("ch15.html", 10, 15, 6, "15.6", "类型论里的相等层级：另一个四价位", ["子集", "等价", "类型", "相等"]),
    ("ch19.html", 20, 19, 7, "19.7", "1/3 缺口：一个尚未结算的常数", ["1/3", "类型不匹配", "现状"]),
    ("ch24.html", 28, 24, 7, "24.7", "三层可信度：从可复现到可裁决", ["可信度", "可裁决", "杀手"]),
]
for f, oldch, newch, start, secno, title, keys in JOBS:
    S = {7: S7, 10: S10, 20: S20, 28: S28}[oldch]
    body = renumber(pick(S, keys), oldch, newch, start)
    if len(body) < 500:
        print("SKIP", f, len(body)); continue
    head = '<h3 id="sec%d">%s　%s</h3>\n' % (newch, secno, title)
    p = ROOT + "\\source\\" + f
    s = io.open(p, encoding="utf-8").read()
    a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
    s = s[:a.start()] + head + body + "\n\n" + s[a.start():]
    io.open(p, "w", encoding="utf-8").write(s)
    print("restored", f, "+%d chars" % len(body))
