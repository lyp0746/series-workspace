import io,re,glob,collections
# 1) 反向力量句：改成含“成为可能”的写法
NEW={
 'entropy-spiral':'这条限制也使一件事成为可能：读者不必相信作者，就能自己判断该在哪里接手。',
 'hotspot-bills':'把「你在为哪一格付钱」摆上桌面，使一次争论转向可核对的事实成为可能。',
 'BureauRotationCession':'把让渡写成可核对的账，使后来者不必从零开始成为可能。',
 'HarnessEcology':'负面结果并不削弱判据，它使「什么时候该停」被事先写下来成为可能。',
 'OptimizationBoundary':'说清边界，使优化被负责任地使用成为可能。',
 'IsomorphismStrength':'断裂探针使类比在被使用之前先知道自己能承载多少成为可能。',
 'MemoryAnchor':'把「不知道该信哪一条」写成可裁决的流程，使不确定性被分配成为可能。',
 'MemoryStressTest':'0.57 只是一个参数点，但它使「低于它就别用」成为一句话成为可能。',
 'LedgerReconciliation':'对账不产生新证据，却使每条旧结论看清自己位置成为可能。',
}
OLD={'entropy-spiral':'这条限制也划出了本书真正的位置','hotspot-bills':'这张卡不替你做判断',
     'BureauRotationCession':'把让渡写成可核对的账，使后来者不必从零开始','HarnessEcology':'负面结果并不削弱这套判据',
     'OptimizationBoundary':'边界的存在使优化重新变成','IsomorphismStrength':'断裂探针的作用不是否定类比',
     'MemoryAnchor':'把「不知道该信哪一条」写成可裁决的流程，使系统','MemoryStressTest':'0.57 只是一个参数点，但它使「低于它就别用」成为一句',
     'LedgerReconciliation':'对账不产生新证据，却使每一条旧结论'}
for b,sent in NEW.items():
    chs=sorted(glob.glob(f"{b}/source/ch*.html"))
    targets=[chs[-1]] if chs else ([f"{b}/source/paper.md"] if __import__("os").path.exists(f"{b}/source/paper.md") else [])
    if not chs and not __import__("os").path.exists(f"{b}/source/paper.md"):
        import glob as _g; targets=_g.glob(f"{b}/*.md")
    for f in targets:
        if not f.endswith((".html",".md")): continue
        t=io.open(f,encoding='utf-8').read()
        if OLD[b] in t:
            t=re.sub(r"<p>"+re.escape(OLD[b])+r".*?</p>\n\n","",t,flags=re.S)
            t=t.replace(OLD[b],"")
        if sent not in t:
            m=re.search(r'<div class="box box-takeaway">|<h3[^>]*>\s*本章参考文献',t)
            para=f"<p>{sent}</p>\n\n"
            t=(t[:m.start()]+para+t[m.start():]) if m else t.rstrip()+"\n"+para
        io.open(f,'w',encoding='utf-8').write(t)
# 2) 重名小节（带 id 的 h3）
REN={"interpretation-tradeoff":("争论的全景",["ch09.html","ch10.html","ch11.html","ch12.html","ch13.html"]),
     "emergence-critical":("你可能想到的问题",["ch08.html","ch10.html","ch11.html","ch01.html"])}
for b,(name,files) in REN.items():
    for f in files:
        p=f"{b}/source/{f}"
        t=io.open(p,encoding='utf-8').read()
        n=int(re.search(r"ch(\d+)",f).group(1))
        t2=re.sub(rf"<h3([^>]*)>{name}</h3>", rf"<h3\1>{name}（第{n}章）</h3>", t)
        if t2!=t: io.open(p,'w',encoding='utf-8').write(t2)
print("done")
