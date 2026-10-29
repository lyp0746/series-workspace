# -*- coding: utf-8 -*-
"""把《中道周行集》转成合集用的卷首 HTML：保留【】、内联封面图、诗行居中、散文两端对齐。"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(r"C:\Users\16103\Downloads\李毅芃的书籍及论文\李毅芃文集\中道周行集.md")
IMG = ROOT / "_assets" / "cover.jpg"

CSS = """<style>
.verse { text-align: center; text-indent: 0; margin: 0 0 .35em 0; letter-spacing: 1px; }
.verse-gap { height: 3mm; }
.prose { text-align: justify; text-indent: 2em; }
table.nat td, table.nat th { word-break: break-word; white-space: normal; }
.byline { text-align: center; text-indent: 0; font-size: 9pt; color: #666; margin: 2mm 0 6mm 0; }
.ti { text-align: center; text-indent: 0; font-size: 9pt; color: #777; margin: 0 0 2mm 0; }
</style>"""

JIE = """<h2 class="front">题解　它为什么放在全书之前</h2>
<p>这一篇不是学术文本：它以诗、词、散、骈、赋、铭六体写同一件事，没有数据、没有分级、也不进入任何引用计数。放在卷首，只有一个理由——<b>它把本合集的方法说成了另一种语言，而两种语言对得上。</b></p>
<table class="nat" style="width:100%;font-size:9pt;table-layout:fixed"><colgroup><col style="width:22%"><col style="width:44%"><col style="width:34%"></colgroup><thead><tr><th>篇中语</th><th>合集里对应的做法</th><th>在哪一件里被做深</th></tr></thead><tbody>
<tr><td class="s">读观行验，日新周复始</td><td>观察 → 抽象 → 建模 → 应用 → 反馈 → 更新（开放、贝叶斯、可证伪）</td><td>全系列；第九篇的对账是它的账本形态</td></tr>
<tr><td class="s">执两用中，不偏不倚</td><td>完备／可组合／可传递至多取二——「中道」不是折中，是在两端之间选一个可执行的组合</td><td>《选择的代价》；论文十四把三角读成价目表</td></tr>
<tr><td class="s">真善为极，万世不移</td><td>锚点：A/B/C 分级与「结论强度 ≤ 证据强度」</td><td>《诠释的权衡》；论文十二「只认锚点」</td></tr>
<tr><td class="s">慎终如始，持满若虚</td><td>不作宿命判断：把每条结论写成可被推翻的样子，把失败写进正文</td><td>论文九（110 条里 16 条被自己打掉）；论文十四（T8 自证否证）</td></tr>
<tr><td class="s">日中则昃，月满则亏</td><td>「临界」：量变到质变的那道门槛，以及「越成功越脆」</td><td>《涌现的临界》；论文十四的「旗舰层越不可替代，价越高」</td></tr>
<tr><td class="s">龙蛇屈伸，木雁之间</td><td>权变：同一机制在不同尺度上换形态（不是同构，是同约束）</td><td>《遗忘的边界》；论文十一把「像」分成四档</td></tr>
</tbody></table>
<p>一句提醒：<b>对得上，不等于同一件事。</b>这篇的价值在于它给了一个精神上的坐标，不在于它能当论证用。若把「中道」读成「一定行、一定有解」，那正与本合集最硬的那几条结论相反——三角之所以是价目表而不是宿命，正是因为它拒绝告诉你「一定行」。</p>
<p style="text-align:right;color:#666;font-size:9pt">编者　2026 年 10 月</p>
"""

# 六体的行态：诗/词/赋/铭 记作 verse（居中），散/骈 记作 prose（两端对齐）
VERSE_BODIES = ("诗", "词", "赋", "铭")


def main():
    md = SRC.read_text(encoding="utf-8")
    md = re.sub(r"^\s*<div[^>]*>\s*", "", md.strip())
    md = re.sub(r"</div>\s*$", "", md.strip())
    md = re.sub(r"<img[^>]*>", "", md)
    img64 = base64.b64encode(IMG.read_bytes()).decode("ascii")

    head, rest = [], []
    state = "prose"       # 当前行态
    started = False       # 是否已过题名页
    in_body = False       # 是否已进入【总论】/【分述】正文
    for raw in md.split("\n"):
        s = raw.strip()
        if not s or s == "---":
            continue
        if s.startswith("# 《中道周行集》"):
            head.append('<h2 class="front">卷首　中道周行集</h2>')
            head.append('<p style="text-align:center;font-size:10.5pt;letter-spacing:3px;color:#8a6d2f">中道周行 · 持满若虚卷</p>')
            head.append('<p style="text-align:center;margin:8mm 0 2mm 0"><img src="data:image/jpeg;base64,%s" '
                        'style="width:42%%;max-width:78mm;height:auto;border:.4pt solid #d8d2c4"/></p>' % img64)
            head.append('<p style="text-align:center;text-indent:0;font-size:8.5pt;color:#777;margin:0 0 6mm 0">'
                        '《中道周行·持满若虚卷》手卷全图（作者手书版）</p>')
            started = True
            continue
        m = re.match(r"^\*\*作者：(.+?)\*\*$", s)
        if m:
            if not in_body:         # 卷首题名页上的作者行
                head.append('<p style="text-align:center;letter-spacing:5px;font-size:12pt">%s</p>' % m.group(1))
            else:                    # 每一体之后的署名
                rest.append('<p class="byline">%s</p>' % m.group(1))
            continue
        if s.startswith("**中道周行·持满若虚卷**"):
            continue
        m = re.match(r"^## 【(.+?)】(.*)$", s)
        if m:
            in_body = True
            state = "prose"
            rest.append('<h2 class="front">【%s】%s</h2>' % (m.group(1), m.group(2)))
            continue
        m = re.match(r"^### (.+)$", s)
        if m:
            in_body = True
            title = m.group(1)
            state = "verse" if any(b in title[:6] for b in VERSE_BODIES) else "prose"
            rest.append('<h2 class="front" style="font-size:17pt;letter-spacing:2px">%s</h2>' % title)
            continue
        m = re.match(r"^\*（(.*?)）\*$", s)
        if m:
            rest.append('<p class="ti">（%s）</p>' % m.group(1))
            continue
        m = re.match(r"^\*\*(李毅芃书于.*?)\*\*$", s)
        if m:
            rest.append('<p style="text-align:right;color:#666;margin-top:6mm">%s</p>' % m.group(1))
            continue
        cls = "verse" if state == "verse" else "prose"
        rest.append('<p class="%s">%s</p>' % (cls, s))

    html = CSS + "\n" + "\n".join(head) + "\n" + JIE + "\n" + "\n".join(rest)
    (ROOT / "_front_daozhou.html").write_text(html, encoding="utf-8")
    print("wrote _front_daozhou.html |", len(html), "chars | img", len(img64) // 1024, "KB | verse",
          html.count('class="verse"'), "| prose", html.count('class="prose"'))


if __name__ == "__main__":
    main()
