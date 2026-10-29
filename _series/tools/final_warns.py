import io,re,glob,os,collections
def fix_dup(book, min_n=5):
    src=f"{book}/source"
    names=collections.defaultdict(list)
    for f in sorted(glob.glob(src+"/ch*.html")):
        t=io.open(f,encoding='utf-8').read()
        for m in re.finditer(r"<h3([^>]*)>([^<]*)</h3>", t):
            names[re.sub(r"<[^>]+>","",m.group(2)).strip()].append(f)
    for name,files in names.items():
        if len(files)<min_n: continue
        for f in files[1:]:
            n=re.search(r"ch(\d+)",f).group(1)
            t=io.open(f,encoding='utf-8').read()
            t=t.replace(f"<h3>{name}</h3>", f"<h3>{name}（第{int(n)}章）</h3>")
            io.open(f,'w',encoding='utf-8').write(t)
for b in ("interpretation-tradeoff","emergence-critical"): fix_dup(b)

for name in ("build_epub.py","build_markdown.py"):
    files=[f"{b}/{name}" for b in os.listdir('.') if os.path.exists(f"{b}/{name}")]
    if not files: continue
    sig=collections.Counter(open(f,'rb').read() for f in files)
    best=sig.most_common(1)[0][0]
    for f in files:
        if open(f,'rb').read()!=best: open(f,'wb').write(best)
    print(name,"统一，副本",len(files))

S={
 'entropy-spiral':'这条限制也划出了本书真正的位置：它不能替你决定，但能让「你现在该决定什么」变得清楚。',
 'hotspot-bills':'这张卡不替你做判断，它只是把「你在为哪一格付钱」摆到桌面上——而这已经足够改变一次争论的走向。',
 'WorldPeriodization':'口径的限制反而使比较成为可能：正因为把门写死了，不同的分期传统才第一次能放在同一张表上被检查。',
 'BureauRotationCession':'把让渡写成可核对的账，使后来者不必从零开始——这正是制度史能积累的方式。',
 'HarnessEcology':'负面结果并不削弱这套判据，它使「什么时候该停」成为可以事先写下的东西。',
 'OptimizationBoundary':'边界的存在使优化重新变成可以被负责任地使用的工具：它规定了用它的条件。',
 'IsomorphismStrength':'断裂探针的作用不是否定类比，而是让类比在被使用之前先知道自己能承载多少。',
 'MemoryAnchor':'把「不知道该信哪一条」写成可裁决的流程，使系统的不确定性第一次变成了可以分配的责任。',
 'MemoryStressTest':'0.57 只是一个参数点，但它使「低于它就别用」成为一句可执行的话。',
 'LedgerReconciliation':'对账不产生新证据，却使每一条旧结论第一次知道自己站在哪一格上。',
}
for b,sent in S.items():
    chs=sorted(glob.glob(f"{b}/source/ch*.html"))
    if chs:
        f=chs[-1]; t=io.open(f,encoding='utf-8').read()
        if sent in t: continue
        m=re.search(r'<div class="box box-takeaway">|<h3[^>]*>\s*本章参考文献',t)
        para=f"<p>{sent}</p>\n\n"
        t=(t[:m.start()]+para+t[m.start():]) if m else t.rstrip()+"\n"+para
        io.open(f,'w',encoding='utf-8').write(t)
    else:
        p=f"{b}/source/paper.md"
        if not os.path.exists(p): continue
        t=io.open(p,encoding='utf-8').read()
        if sent in t: continue
        m=re.search(r"(?m)^## 参考文献",t)
        t=(t[:m.start()]+sent+"\n\n"+t[m.start():]) if m else t.rstrip()+"\n\n"+sent
        io.open(p,'w',encoding='utf-8').write(t)
print("反向力量句补完")
