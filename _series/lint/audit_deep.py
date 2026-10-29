# -*- coding: utf-8 -*-
"""深度校对：lint 之外的结构检查（只读）。"""
import io, re, os, json, glob
BOOKS=["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
       "impossibility-triangle","interpretation-tradeoff","emergence-critical","hotspot-bills","mind-forks"]
issues=[]
for b in BOOKS:
    src=f"{b}/source"
    parts=json.load(io.open(f"{src}/parts.json",encoding="utf-8"))
    listed=[c for p in parts for c in p["chapters"]]
    files=sorted(os.path.basename(f) for f in glob.glob(src+"/ch*.html"))
    # 1 章号/文件名/标题一致性
    for i,c in enumerate(listed,1):
        t=io.open(os.path.join(src,c["file"]),encoding="utf-8").read()
        h=re.search(r'<h2 class="chapter">([^<]*)</h2>',t)
        title=h.group(1) if h else ""
        if not re.match(rf"^第{c['no']}章　", title):
            issues.append(f"{b} {c['file']}: 标题「{title[:20]}」与章号 {c['no']} 不符")
        if c["file"]!=f"ch{int(c['no']):02d}.html":
            issues.append(f"{b}: 章号 {c['no']} 与文件 {c['file']} 不符")
        if int(c["no"])!=i:
            issues.append(f"{b}: 章号不连续（第{i}个是 {c['no']}）")
    # 2 文件是否都在 parts 里
    if set(files)!=set(c["file"] for c in listed):
        issues.append(f"{b}: 磁盘与 parts 不一致 {set(files)^set(c['file'] for c in listed)}")
    # 3 小节编号
    for c in listed:
        t=io.open(os.path.join(src,c["file"]),encoding="utf-8").read()
        nums=[]
        for m in re.finditer(r'<h3([^>]*)>([^<]*)</h3>', t):
            txt=re.sub(r"<[^>]+>","",m.group(2)).strip()
            mm=re.match(rf"^({c['no']})\.(\d+)", txt)
            if mm: nums.append(int(mm.group(2)))
            elif txt not in ("本章小结","本章参考文献"):
                issues.append(f"{b} {c['file']}: 未编号小节「{txt[:16]}」")
            sid=re.search(r'id="sec(\d+)-(\d+)"', m.group(1) or "")
            if sid and sid.group(1)!=c["no"]:
                issues.append(f"{b} {c['file']}: id {sid.group(0)} 与章号不符")
        if nums and nums!=list(range(1,len(nums)+1)):
            issues.append(f"{b} {c['file']}: 小节号不连续 {nums}")
    # 4 附录
    apx=sorted(f for f in os.listdir(src) if re.fullmatch(r"appendix_[a-z]\.html",f))
    bp=io.open(f"{b}/build_book.py",encoding="utf-8").read()
    back=set(re.findall(r'"(appendix_[a-z]\.html)"',bp))
    if set(apx)!=back:
        issues.append(f"{b}: 附录文件与 BACK 不一致 磁盘-{set(apx)-back} BACK-{back-set(apx)}")
    letters=[]
    for i,f in enumerate(apx):
        t=io.open(os.path.join(src,f),encoding="utf-8").read()
        h=re.search(r'<h2 class="chapter">([^<]*)</h2>',t)
        title=h.group(1) if h else ""
        letters.append(title[:4])
        if not re.match(rf"^附录 {chr(65+i)}　", title):
            issues.append(f"{b} {f}: 附录标题「{title[:16]}」字母不符（应为 {chr(65+i)}）")
    # 5 图片引用
    for f in glob.glob(src+"/*.html"):
        t=io.open(f,encoding="utf-8").read()
        for m in re.finditer(r'<img[^>]*src="([^"]+)"', t):
            s=m.group(1)
            if s.startswith("data:"): continue
            if not os.path.exists(os.path.join(b,s)) and not os.path.exists(os.path.join(src,s)):
                issues.append(f"{b} {os.path.basename(f)}: 图片缺失 {s}")
    # 6 章引用有效性
    n=len(listed)
    for f in glob.glob(src+"/*.html"):
        t=io.open(f,encoding="utf-8").read()
        for m in re.finditer(r"第\s*(\d+)\s*章", t):
            k=int(m.group(1))
            if k<1 or k>n:
                issues.append(f"{b} {os.path.basename(f)}: 引用第{k}章（共{n}章）")
print(f"共 {len(issues)} 项")
for x in issues[:60]: print(" -", x)
