# -*- coding: utf-8 -*-
"""docx → md（一次性转换，此后 md 是唯一源）。

用法：python convert_sanwen.py
产出：得鹿梦鱼.md
标记：`## 标题` / `P 正文段` / `Q 引语段` / `FIG 文件名 | 图注`
"""
import io
import re
from docx import Document

SRC = "得鹿梦鱼：五公里的单向时间、粗码与电子幽灵.docx"
DST = "得鹿梦鱼.md"
BOOK, SUB, BY, SEAL = "得鹿梦鱼", "五公里的单向时间、粗码与电子幽灵", "李毅芃", "得鹿梦鱼"
HEAD_RE = re.compile(r"^(序章|尾声|后记|楔子|第[一二三四五六七八九十百零〇两\d]+[卷章篇部])[：:]\s*(.*)$")

PHOTOS = [
    ("刺出一道孤冷的剑芒", "图1_村道直出.jpg", "村口的路。手机直出，未开夜景模式。"),
    ("惨白的光打在粗糙的柏油路面上", "图2_村道夜景模式.jpg", "同一条路，开了夜景模式。"),
    ("像极了大海深处的一座孤岛灯塔", "图3_满月与窗.jpg", "满月，与那扇亮着的窗。"),
    ("投下一滩银白色的光斑", "图4_树影隧道.jpg", "树影隧道，与尽头的白光。"),
    ("与先前的满月遥相呼应", "图5_围挡与灯火.jpg", "黄铜色围挡、工棚，与围挡背后的万家灯火。"),
]


# 一次性校订：错字（繁简混入、同音误字、数字体例）＋感叹号收敛
FIXES = [
    ("緩緩", "缓缓"), ("沒有", "没有"),
    ("我不仅哑然失笑", "我不禁哑然失笑"),
    ("我用我23岁真实的血肉", "我用我二十三岁真实的血肉"),
    ("虚荣心的23岁青年", "虚荣心的二十三岁青年"),
    ("这具23岁的疲惫肉身", "这具二十三岁的疲惫肉身"),
]
EXCLAIM_KEEP = "给我抓虫"


def normalise(t):
    for a, b in FIXES:
        t = t.replace(a, b)
    if EXCLAIM_KEEP not in t:
        t = t.replace("？！", "？").replace("！", "。")
    return t


def clean(t):
    t = t.replace("\u3000", " ")
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    return re.sub(r"[ \t]+", " ", t).strip()


def split_head(t):
    m = HEAD_RE.match(t)
    if m:
        return f"{m.group(1)}：{m.group(2).strip()}"
    if t.strip() in {"序章", "尾声", "后记"}:
        return t.strip()
    return None


doc = Document(SRC)
paras = []
for p in doc.paragraphs:
    t = clean(p.text)
    if not t:
        continue
    if t.strip("《》 ").startswith("得鹿梦鱼") and ("五公里" in t or "单向时间" in t):
        continue
    if re.sub(r"\s+", "", t) in {BY, BY + "著", "作者：" + BY}:
        continue
    paras.append(normalise(t))

# 卷末与尾声重复的那两句，去掉卷末那份
if any(split_head(p) == "尾声：赐名、成书与十二万亿年的庞加莱回归" for p in paras):
    kept, seen = [], False
    for p in paras:
        h = split_head(p)
        if h and h.startswith("尾声"):
            seen = True
        if not seen and (p.startswith("长夜已尽。在这单向流动的时间里") or p == "我们，晚安。"):
            continue
        kept.append(p)
    paras = kept

out = [f"# {BOOK}", f"SUB {SUB}", f"BY {BY}", f"SEAL {SEAL}", ""]
in_quote = False
for t in paras:
    h = split_head(t)
    if h:
        out.append(f"## {h}")
        in_quote = False
        continue
    starts, ends = t.startswith("“"), t.endswith("”")
    if starts:
        in_quote = True
    out.append(("Q " if in_quote else "P ") + t)
    if ends:
        in_quote = False
    for anchor, f, cap in PHOTOS:
        if anchor in t:
            out.append(f"FIG {f} | {cap}")

io.open(DST, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("wrote", DST, len(out), "行")
