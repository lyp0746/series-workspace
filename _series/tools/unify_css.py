# -*- coding: utf-8 -*-
"""统一九本书的版式（对标 Nature/Science 的 V1–V12）。

幂等：以 MARK 标记是否已改过。
- 正文 12 pt / 1.62；节 12.8；小节 = 正文（不再倒挂）；章 17；部分 21
- 目录行 flex + 页码列
- 装饰预算：蓝（概念）+ 琥珀（警示）+ 灰（中性），去掉绿色与米色底
- 去掉章标题左侧色条，改成细上规则线
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade",
         "entropy-spiral", "impossibility-triangle", "interpretation-tradeoff",
         "emergence-critical", "mind-forks", "hotspot-bills"]
MARK = "/* v4: nature-benchmark */"


def patch_paper(path):
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        return False
    # 正文
    s = re.sub(r"font-size: 13pt;\n  line-height: 1\.5;",
               "font-size: 12pt;\n  line-height: 1.62;", s)
    s = re.sub(r"font-size: 11\.2pt;\n  line-height: 1\.82;",
               "font-size: 11.6pt;\n  line-height: 1.78;", s)
    s = re.sub(r"p \{ margin: 0 0 9\.5px; \}\s+/\* 9\.5pt 节奏：科普专著略宽 \*/",
               "p { margin: 0 0 8.5px; }", s)
    s = re.sub(r"p \{ margin: 0 0 8px; \}\s+/\* 8pt 节奏 \*/",
               "p { margin: 0 0 8.5px; }", s)
    # 标题层级
    s = s.replace("h2 {\n  font-size: 14pt; font-weight: 700;\n  margin: 30px 0 12px; padding: 0 0 5px 0;\n  border-bottom: 1.4px solid #222;\n}",
                  "h2 {\n  font-size: 14.5pt; font-weight: 700;\n  margin: 30px 0 12px; padding: 0 0 5px 0;\n  border-bottom: 0.9px solid #333;\n}")
    s = s.replace("h3 { font-size: 13pt; font-weight: 700; margin: 20px 0 8px; color: #222; }",
                  "h3 { font-size: 12.8pt; font-weight: 700; margin: 21px 0 8px; color: #1f1f1f; }")
    s = s.replace("h4 { font-size: 11pt; font-weight: 700; margin: 14px 0 6px; color: #333; }",
                  "h4 { font-size: 1em; font-weight: 700; margin: 16px 0 6px; color: #262626; }")
    s = s.replace("h4.arg { font-size: 13pt; font-weight: 700; color: #444; margin: 12px 0 4px; }",
                  "h4.arg { font-size: 1em; font-weight: 700; color: #333; margin: 14px 0 5px; }")
    s = s.replace("h5 { font-size: 13pt; font-weight: 600; margin: 10px 0 4px; color: #333; }",
                  "h5 { font-size: 1em; font-weight: 600; margin: 10px 0 4px; color: #333; }")
    # 装饰预算
    s = s.replace(".scenario { background: #f3f9f5; border-left: 3.5px solid #009E73; }",
                  ".scenario { background: #f7fafc; border-left: 3px solid #7aa8c4; }")
    s = s.replace(".warning { background: #fff6ee; border-left: 3.5px solid #D55E00; }",
                  ".warning { background: #fbf7ef; border-left: 3px solid #B26B00; }")
    s = s.replace(".case { background: #fbfbf9; border: 1px solid #ddd; border-top: 3px solid #333; }",
                  ".case { background: #fbfbfb; border: 1px solid #e2e2e2; border-top: 1.5px solid #6b6b6b; }")
    s = s.replace(".define { background: #f4f8fb; border-left: 3.5px solid #2E86AB; }",
                  ".define { background: #f4f8fb; border-left: 3px solid #2E86AB; }")
    s = s.replace(".note { background: #fafafa; border-left: 3px solid #999; }",
                  ".note { background: #f7f7f7; border-left: 3px solid #b5b5b5; }")
    s = s.replace(".box { background: #faf9f5; border: 1px solid #ddd; }",
                  ".box { background: #fafafa; border: 1px solid #e4e4e4; }")
    s = s.replace(".part-summary {\n  max-width: 132mm; margin: 8mm auto 2mm; padding: 4.5mm 6mm;\n  border-top: 1px solid #d8cbb0; border-bottom: 1px solid #d8cbb0;\n  background: #fbf9f4; font-size: 10pt; line-height: 1.8;\n}",
                  ".part-summary {\n  max-width: 132mm; margin: 9mm auto 2mm; padding: 4mm 0 0;\n  border-top: 0.8px solid #9a9a9a; font-size: 9.6pt; line-height: 1.9;\n}")
    s = s.replace("  margin-bottom: .35em; color: #8a6d2f;", "  margin-bottom: .35em; color: #4a4a4a;")
    # 目录：flex + 页码列（V6）
    s = s.replace("/* ------------------------------ 其他 ------------------------------ */",
                  """/* ---- 目录：右侧页码列 ---- */
.toc .l1, .toc .l2, .toc .l3, .toc .l4 {
  display: flex; align-items: baseline;
}
.toc .l1 > a, .toc .l2 > a, .toc .l3 > a, .toc .l4 > a { flex: 0 1 auto; min-width: 0; }
.toc .folio {
  margin-left: auto; padding-left: 10px; flex: 0 0 auto;
  color: #555; font-size: .9em; font-variant-numeric: tabular-nums;
}

/* ------------------------------ 其他 ------------------------------ */""")
    # 注释里的字号说明同步（避免文档与实现不一致）
    s = s.replace("10.5pt、1.5 倍行距", "12pt、1.62 倍行距")
    s = s.replace("页面：A4 单栏、30/35/32/35mm 边距、10.5pt、1.5 倍行距。",
                  "页面：A4 单栏、26/30/28/30mm 边距、12pt、1.62 倍行距。")
    s = s.replace("font-size: 13pt;\n  line-height: 1.5;", "font-size: 12pt;\n  line-height: 1.62;")
    s = s.rstrip() + "\n\n" + MARK + "\n"
    open(path, "w", encoding="utf-8").write(s)
    return True


def patch_book(path):
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        return False
    # 章标题：去左侧色条，改为上规则线
    s = s.replace("""h2.chapter {
  font-size: 18pt; font-weight: 700; border: 0;
  border-left: 6px solid #222; padding: 0 0 0 12px;
  margin: 0 0 14px; break-before: page;
}""",
                  """h2.chapter {
  font-size: 17pt; font-weight: 700; border: 0;
  border-top: 1.2px solid #222; padding: 8px 0 0;
  margin: 0 0 16px; break-before: page;
}""")
    # 部分扉页：字号与系列统一
    s = s.replace('font-size: 22pt; font-weight: 600; letter-spacing: 2.5px;',
                  'font-size: 21pt; font-weight: 600; letter-spacing: 1.6px;')
    s = s.rstrip() + "\n\n" + MARK + "\n"
    open(path, "w", encoding="utf-8").write(s)
    return True


if __name__ == "__main__":
    for b in BOOKS:
        p1 = os.path.join(ROOT, b, "assets", "css", "paper.css")
        p2 = os.path.join(ROOT, b, "assets", "css", "book.css")
        a = patch_paper(p1)
        c = patch_book(p2)
        print(b, "paper:", a, "book:", c)
