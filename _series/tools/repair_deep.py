# -*- coding: utf-8 -*-
"""深度修复：① 把混进章节的附录小节搬回附录 ② 章标题统一 ③ 小节号重排 ④ 附录字母校正"""
import io, re, os, glob, json

BOOKS=["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
       "impossibility-triangle","interpretation-tradeoff","emergence-critical","hotspot-bills","mind-forks"]

# ---------- ① 搬回附录 ----------
NEWAPX={"entropy-spiral":("appendix_f.html","补编：数据、案例与登记"),
        "distinction-evolution":("appendix_f.html","补编：提案、警告与登记接口")}
for b,(fname,title) in NEWAPX.items():
    src=f"{b}/source"; collected=[]
    for f in sorted(glob.glob(src+"/ch*.html")):
        t=io.open(f,encoding='utf-8').read()
        blocks=re.split(r"(?m)(?=<h3)",t)
        keep=[blocks[0]]; moved=[]
        for blk in blocks[1:]:
            m=re.match(r"<h3[^>]*>([^<]*)</h3>",blk)
            head=re.sub(r"<[^>]+>","",m.group(1)).strip() if m else ""
            if re.match(r"^[A-Z]\.\d", head) or head in ("参考文献","附录 数据与案例"):
                moved.append(blk)
            else:
                keep.append(blk)
        if moved:
            io.open(f,'w',encoding='utf-8').write("".join(keep))
            collected += moved
    if collected:
        body="\n\n".join(x.strip() for x in collected)
        io.open(os.path.join(src,fname),"w",encoding='utf-8').write(
            f'<h2 class="chapter">附录 F　{title}</h2>\n<div class="box"><p>本附录收存由正文迁出的数据索引、案例与登记接口；它们是证据与工具，不是论述。</p></div>\n\n'+body)
        bp=f"{b}/build_book.py"; t=io.open(bp,encoding='utf-8').read()
        if fname not in t:
            t=t.replace("BACK = [\n", f'BACK = [\n        ("附录 F　{title}", "{fname}", "apxF"),\n',1)
        io.open(bp,'w',encoding='utf-8').write(t)
        print(f"{b}: 搬回 {len(collected)} 节 → {fname}")

# ---------- ② 章标题统一「第N章」 ----------
CN={c:i+1 for i,c in enumerate("一二三四五六七八九")}
def cn2int(s):
    if s.isdigit(): return int(s)
    if "十" in s:
        a,_,b2=s.partition("十"); return (CN.get(a,1) if a else 1)*10+(CN.get(b2,0) if b2 else 0)
    return CN.get(s,0)
for b in BOOKS:
    for f in glob.glob(f"{b}/source/ch*.html"):
        t=io.open(f,encoding='utf-8').read()
        n=int(re.search(r"ch(\d+)",os.path.basename(f)).group(1))
        t2=re.sub(r'<h2 class="chapter">第\s*[0-9一二三四五六七八九十]+\s*章\s*[　 ]*',
                  lambda m: f'<h2 class="chapter">第{n}章　', t, count=1)
        if t2!=t: io.open(f,'w',encoding='utf-8').write(t2)

# ---------- ③ 小节号重排（含正文引用改写） ----------
for b in BOOKS:
    src=f"{b}/source"
    for f in sorted(glob.glob(src+"/ch*.html")):
        n=int(re.search(r"ch(\d+)",os.path.basename(f)).group(1))
        t=io.open(f,encoding='utf-8').read()
        heads=list(re.finditer(r'<h3([^>]*)>([^<]*)</h3>', t))
        cnt=0; smap={}
        for m in heads:
            txt=re.sub(r"<[^>]+>","",m.group(2)).strip()
            om=re.match(rf"^{n}\.(\d+)", txt)
            if not om: continue
            cnt+=1
            if int(om.group(1))!=cnt: smap[om.group(1)]=str(cnt)
            new=re.sub(rf"^{n}\.\d+\s*[　 ]*", f"{n}.{cnt}　", txt)
            attrs=re.sub(r'id="[^"]*"', f'id="sec{n}-{cnt}"', m.group(1))
            t=t.replace(m.group(0), f"<h3{attrs}>{new}</h3>",1)
        for old,new in smap.items():
            t=re.sub(rf"(?<![\d.]){n}\.{old}(?=\s*[节表图])", f"{n}.{new}", t)
        io.open(f,'w',encoding='utf-8').write(t)

# ---------- ④ 附录字母 / 标题校正 ----------
for b in BOOKS:
    src=f"{b}/source"
    files=sorted(f for f in os.listdir(src) if re.fullmatch(r"appendix_[a-z]\.html",f))
    for i,f in enumerate(files):
        p=os.path.join(src,f); t=io.open(p,encoding='utf-8').read()
        m=re.search(r'<h2 class="chapter">([^<]*)</h2>',t)
        if not m: continue
        title=re.sub(r"^附\s*录\s*[A-F]\s*[　 ]*","",m.group(1))
        want=f"附录 {chr(65+i)}　{title}"
        if m.group(1)!=want:
            t=t[:m.start()]+f'<h2 class="chapter">{want}</h2>'+t[m.end():]
            io.open(p,'w',encoding='utf-8').write(t)
print("deep repair done")
