import io, re
ROOT = r"D:\0_Article\distinction-evolution\source"
JOBS = [("ch13.html", "第四套工具"), ("ch15.html", "类型论里的相等层级"),
        ("ch19.html", "1/3 缺口"), ("ch24.html", "三层可信度")]
for f, title in JOBS:
    p = ROOT + "\\" + f
    s = io.open(p, encoding="utf-8").read()
    # 找到新块的起止（到“本章参考文献”前）
    m = re.search(r'<h3[^>]*>[^<]*%s[^<]*</h3>' % re.escape(title), s)
    if not m:
        print("no block", f); continue
    i = m.start()
    k = s.find('　本章参考文献</h3>')
    k = s.rfind('<h3', i, k)
    block = s[i:k]
    rest = s[:i] + s[k:]
    # 小结块
    ms = re.search(r'(<h3[^>]*>)(\d+)\.(\d+)([^<]*本章小结[^<]*)(</h3>)', rest)
    if not ms:
        print("no summary", f); continue
    ch, n = int(ms.group(2)), int(ms.group(3))
    newnum = "%d.%d" % (ch, n)          # 新节占用小结的号
    ms_newnum = "%d.%d" % (ch, n + 1)   # 小结顺延
    block = re.sub(r'(<h3[^>]*>)\d+\.\d+', r'\g<1>' + newnum, block, count=1)
    rest = rest[:ms.start()] + ms.group(1) + ms_newnum + ms.group(4) + ms.group(5) + rest[ms.end():]
    out = rest[:ms.start()] + block + "\n" + rest[ms.start():]
    io.open(p, "w", encoding="utf-8").write(out)
    print("fixed", f, newnum, "->", ms_newnum)
