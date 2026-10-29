#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按 [NN]/Q/S/T/C 数据文件，为每章补主提问框、本章小结、一句话带走、反例。"""
import io, re, sys, os
ROOT='.'
book=sys.argv[1]; data=sys.argv[2]
t=io.open(data,encoding='utf-8').read()
blocks=re.split(r"(?m)^\[(\d+)\]$", t)[1:]
recs={}
for i in range(0,len(blocks),2):
    no=blocks[i]; body=blocks[i+1]
    rec={}
    for line in body.strip().split("\n"):
        m=re.match(r"^([QSTC]):\s*(.*)$", line)
        if m: rec[m.group(1)]=m.group(2).strip()
    recs[int(no)]=rec
n=0
for no,rec in recs.items():
    p=os.path.join(ROOT,book,'source',f'ch{no:02d}.html')
    if not os.path.exists(p): print('缺', p); continue
    x=io.open(p,encoding='utf-8').read(); o=x
    # 主提问框
    if rec.get('Q') and 'box-takeaway' not in x.split('</h2>')[1][:400]:
        x=re.sub(r'(</h2>\s*\n)', r'\1<div class="box box-takeaway"><p><b>本章主提问：</b>'+rec['Q']+r'</p></div>\n\n', x, count=1)
    # 反例
    if rec.get('C') and rec['C'][:20] not in x:
        m=re.search(r'<div class="box box-summary">|<div class="box box-takeaway">', x)
        x=(x[:m.start()]+rec['C']+"\n\n"+x[m.start():]) if m else x.rstrip()+"\n"+rec['C']+"\n"
    # 小结
    if rec.get('S') and 'box-summary' not in x:
        li="".join(f"<li>{s.strip()}</li>" for s in rec['S'].split('|'))
        box=f'<div class="box box-summary"><span class="bt">本章小结</span>\n<ul>{li}</ul></div>\n\n'
        m=re.search(r'<div class="box box-takeaway">|<h3[^>]*>\s*本章参考文献', x)
        x=(x[:m.start()]+box+x[m.start():]) if m else x.rstrip()+"\n"+box
    # 带走
    if rec.get('T') and '一句话带走' not in x:
        box=f'<div class="box box-takeaway"><p><b>一句话带走：</b>{rec["T"]}</p></div>\n\n'
        m=re.search(r'<h3[^>]*>\s*本章参考文献', x)
        x=(x[:m.start()]+box+x[m.start():]) if m else x.rstrip()+"\n"+box
    if x!=o:
        io.open(p,'w',encoding='utf-8').write(x); n+=1
print(book,"改",n,"章")
