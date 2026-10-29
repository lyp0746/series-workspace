#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""通俗本补「一句话带走」（spec v2 §2b 第④段）。"""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = {
 "knowledge-tradeoffs": {
  9: "六个路口各有各的价目表，但用的都是同一把尺子：你可以要两个，不能要三个。",
  11: "十三个误解大多源于同一件事：把“约束”读成了“宿命”。",
  12: "本书不指望说服所有人，只希望反对它的人能说清反对的是哪一句。",
  13: "二十五个真实的人，没有一个是“案例”；他们都是在具体处境里做取舍的人。",
  14: "能背下来的用法一定不够用，够用的用法一定背不下来。",
  15: "练习题的答案不止一个；取舍题如果只有一个答案，它就不是取舍题。",
  16: "三个人的谈话里最有用的一句，往往不是结论，而是“你刚才那句话，代价是谁付”。",
  17: "给老师、家长和孩子的一页：不要用这套东西给孩子打分。",
  18: "这本书的边界，比它的结论更值得记住。",
  19: "一年之后回看，最该保留的不是结论，而是“当时的判断依据”。",
 },
 "hotspot-bills": {
  4: "注意力不是被夺走的，是被交换掉的——你付出的那部分，账单在后面几章。",
  5: "制度之所以慢，不是因为它笨，而是因为它必须同时照顾那些不在场的人。",
  8: "十个反例说明：这张卡最该用的时候，是它可能错的时候。",
  13: "身体、城市与代际：三个尺子量出来的，往往是同一笔延迟支付的账。",
  14: "五张长卡的正确读法不是看结论，而是看每一步“我可能在哪里错”。",
  15: "二十个追问里最要紧的一个是：这张卡凭什么比我的直觉更可靠。",
  16: "十二句话把一年收成账：每一句都该能对上一条可核的事实。",
  18: "三十条一句话诊断不是答案库，是一份“先问哪一句”的索引。",
 },
}
BOX = '<div class="box box-takeaway"><p><b>一句话带走：</b>{}</p></div>\n'
for book, table in T.items():
    src = os.path.join(ROOT, book, "source"); hit = 0
    for no, line in table.items():
        p = os.path.join(src, f"ch{no:02d}.html")
        t = io.open(p, encoding="utf-8").read()
        if "一句话带走" in t:
            continue
        m = re.search(r"<h3[^>]*>\s*本章参考文献", t)
        if m:
            t = t[:m.start()] + BOX.format(line) + "\n" + t[m.start():]
        else:
            t = t.rstrip() + "\n" + BOX.format(line)
        io.open(p, "w", encoding="utf-8").write(t); hit += 1
    print(book, hit)
