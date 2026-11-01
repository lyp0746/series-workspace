# -*- coding: utf-8 -*-
"""重排 emergence-critical 的附录：按 spec v2 的 A–F 语义重组。
A 形式化与证明 / B 数据与复算 / C 协议与稳健性 / D 登记簿 / E 工具 / F 索引与缺口
参考文献独立成件。只做一次性结构整理，不写新内容。
"""
import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                   "emergence-critical", "source", "appendix_a.html")
OUT = os.path.dirname(SRC)
L = open(SRC, encoding="utf-8").read().splitlines(keepends=True)


def blk(a, b):
    """1-indexed inclusive"""
    return "".join(L[a - 1:b])


def retitle(s, new_head):
    """去掉块首的旧标题行，换成 new_head。"""
    return re.sub(r"^\s*<h[234][^>]*>.*?</h[234]>\s*\n", "", s, count=1) if \
        re.match(r"\s*<h[234]", s) else s


# ---------- 参考文献（原 49–59）
refs = blk(49, 59)
refs = retitle(refs, "")
open(os.path.join(OUT, "back_references.html"), "w", encoding="utf-8").write(
    '<h2 class="chapter">参考文献</h2>\n' + refs.strip() + "\n")

# ---------- A 形式化与证明：X.1–X.5（391–636）
xA = blk(391, 636)
blocks = re.split(r'(?=<h3 id="secx-\d">)', xA)
blocks = [b for b in blocks if b.strip()]
cn = ["一", "二", "三", "四", "五"]
newA = ['<h2 class="chapter" id="apxA">附录 A　形式化：推导与解析</h2>',
        '<p>这一组是本册最"硬"的部分：五段推导，从朗道自由能到有限尺度标度，再到边界条件与约束优化。它们不构成新的理论主张，只把正文里用到的结论一步一步写出来，便于复算与挑错。读法：每段开头一句"这一段要得到什么"，段末一句"它对本书意味着什么"；中间的代数可以跳，结论不能跳。</p>']
for i, b in enumerate(blocks, 1):
    b = re.sub(r'<h3 id="secx-\d">\s*X\.\d+\s*第[一二三四五六七八九十百]+章\s*', 
               f'<h3 id="secA-{i}">A.{i}　', b, count=1)
    # 内部 NN.k → A.i.k（h3 → h4）
    old_prefix = re.findall(r'<h3 id="sec(\d+)-(\d+)">\s*(\d+)\.(\d+)', b)
    nn = old_prefix[0][0] if old_prefix else None

    def rep(m):
        return f'<h4 id="secA-{i}-{m.group(2)}">A.{i}.{m.group(2)}　'
    b = re.sub(r'<h3 id="sec\d+-(\d+)">\s*\d+\.(\d+)　', lambda m: rep(m), b)
    newA.append(b.strip())
open(os.path.join(OUT, "appendix_a.html"), "w", encoding="utf-8").write("\n".join(newA) + "\n")

# ---------- B 数据、实验与复算
B = ['<h2 class="chapter" id="apxB">附录 B　数据、实验与复算</h2>',
     '<p>这一组回答一个问题：书里的每个数从哪来、怎么复算、失败的那几次长什么样。表多、字少，是刻意如此——附录的任务是可核对，不是可读。</p>',
     '<h3 id="secB-1">B.1　数值实验：参数、结果与失败记录</h3>']
B.append(retitle(blk(127, 163), "").strip())
B.append('<h3 id="secB-2">B.2　全部模拟原始数据</h3>')
B.append(retitle(blk(183, 285), "").strip())
B.append('<h3 id="secB-3">B.3　预警指标与渗流原始数据</h3>')
B.append(retitle(blk(286, 390), "").strip())
B.append('<h3 id="secB-4">B.4　十个短案例</h3>')
B.append(retitle(blk(100, 103), "").strip())
open(os.path.join(OUT, "appendix_b.html"), "w", encoding="utf-8").write("\n".join(B) + "\n")

# ---------- C 协议与稳健性
C = ['<h2 class="chapter" id="apxC">附录 C　协议与稳健性</h2>',
     '<p>这一组是"怎么用"的部分：一份十步诊断协议、五个看起来像却不是的失败案例，以及每章两道的思考题。它们的作用是防止把框架用在它不适用对象上。</p>',
     '<h3 id="secC-1">C.1　五个"看起来像，其实不是"</h3>']
C.append(retitle(blk(105, 107), "").strip())
C.append('<h3 id="secC-2">C.2　一次完整诊断的十步协议</h3>')
C.append(retitle(blk(108, 112), "").strip())
C.append('<h3 id="secC-3">C.3　思考题（每章两题）</h3>')
C.append(retitle(blk(116, 117), "").strip())
open(os.path.join(OUT, "appendix_c.html"), "w", encoding="utf-8").write("\n".join(C) + "\n")

# ---------- D 可证伪登记簿（原 A 组）
Dold = blk(2, 45)
Dold = re.sub(r'<h3>\s*附录 可证伪登记簿　术语表（查询式）</h3>',
              '<h3 id="secD-1">D.1　术语表（查询式）</h3>', Dold)
Dold = Dold.replace('<h4>附录 B　可证伪登记（append-only）</h4>',
                    '<h3 id="secD-2">D.2　可证伪登记（append-only）</h3>')
Dold = Dold.replace('<h4>附录 C　证据等级与概念等级</h4>',
                    '<h3 id="secD-3">D.3　证据等级与概念等级</h3>')
Dold = Dold.replace('<h4>附录 D　此前几本与本书的关系（含证据链）</h4>',
                    '<h3 id="secD-4">D.4　此前几本与本书的关系（含证据链）</h3>')
Dold = Dold.replace('<h4>附录 E　本系列</h4>', '<h3 id="secD-5">D.5　本系列</h3>')
D = ['<h2 class="chapter" id="apxD">附录 D　可证伪登记簿</h2>', Dold.strip()]
open(os.path.join(OUT, "appendix_d.html"), "w", encoding="utf-8").write("\n".join(D) + "\n")

# ---------- E 工具与清单
E = ['<h2 class="chapter" id="apxE">附录 E　工具与清单</h2>',
     '<p>这一组是"拿下来就能用"的：一页纸速查、人物小传、给不同读者的读法、一张可打印的诊断表。它们不增加论证，只降低使用门槛。</p>']
E.append(retitle(blk(119, 126), "").strip())     # O/P/Q
E.append('<h3 id="secE-16">E.5　一页纸诊断表（可打印）</h3>')
E.append(retitle(blk(165, 182), "").strip())     # S
open(os.path.join(OUT, "appendix_e.html"), "w", encoding="utf-8").write("\n".join(E) + "\n")

# ---------- F 索引、符号与缺口
F = ['<h2 class="chapter" id="apxF">附录 F　索引、符号与缺口</h2>',
     '<p>最后这一组不是附录的附录，而是书的"背面"：核心概念索引、符号表、相变概念小史、延伸阅读，以及三处至今没有数据的缺口。</p>',
     '<h3 id="secF-1">F.1　核心概念索引</h3>']
F.append(retitle(blk(60, 86), "").strip())
F.append('<h3 id="secF-2">F.2　符号表</h3>')
F.append(retitle(blk(87, 99), "").strip())
F.append('<h3 id="secF-3">F.3　相变概念小史</h3>')
F.append(retitle(blk(113, 115), "").strip())
F.append('<h3 id="secF-4">F.4　延伸阅读</h3>')
F.append(retitle(blk(47, 48), "").strip())
F.append('''<h3 id="secF-5">F.5　三处数据缺口</h3>
<table class="nat">
<caption class="cap"><b>表 F.3　三处至今没有数据的缺口</b></caption>
<thead><tr><th class="l">缺口</th><th class="l">为什么现在没有</th><th class="l">怎样才算补上</th></tr></thead>
<tbody>
<tr><td class="l">跨系统的普适类归属</td><td class="l">需要同一套标度分析跑在至少五个不同系统上</td><td class="l">同一脚本、同一窗口选择规则，给出五个系统的 α 与置信区间</td></tr>
<tr><td class="l">"回不去"的操作化</td><td class="l">对称破缺可观测，但"不可逆"需要长时间跟踪</td><td class="l">同一系统跨越临界点前后各 3 年以上的追踪</td></tr>
<tr><td class="l">诊断效力与复杂度的反比</td><td class="l">目前只有经验观察，没有控制的复杂度梯度</td><td class="l">构造 C 从 3 到 30 的一组系统，同一诊断者盲评</td></tr>
</tbody></table>
<div class="box"><p><b>一句总账：</b>这本书能证明的是"哪些变化可以被认成相变"，不能证明的是"社会系统的相变何时发生"。前者是形式化的成果，后者是数据的缺口——两者不能互相冒充。</p></div>''')
open(os.path.join(OUT, "appendix_f.html"), "w", encoding="utf-8").write("\n".join(F) + "\n")

print("done: appendix_a..f + back_references")
