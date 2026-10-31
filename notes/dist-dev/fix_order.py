import io, re
ROOT = r"D:\0_Article\distinction-evolution\source"
JOBS = [("ch13.html", "sec13-7"), ("ch15.html", "sec15-6"), ("ch19.html", "sec19-7"), ("ch24.html", "sec24-7")]
for f, marker in JOBS:
    p = ROOT + "\\" + f
    s = io.open(p, encoding="utf-8").read()
    i = s.find('<h3 id="%s"' % marker)
    k = s.find('　本章参考文献</h3>')
    if i < 0 or k < 0:
        print("skip", f, i, k); continue
    k = s.rfind('<h3', i, k)
    block = s[i:k]
    rest = s[:i] + s[k:]
    m = re.search(r'<h3[^>]*>[^<]*本章小结</h3>', rest)
    if not m:
        print("no summary", f); continue
    out = rest[:m.start()] + block + "\n" + rest[m.start():]
    io.open(p, "w", encoding="utf-8").write(out)
    print("reordered", f, len(block))
