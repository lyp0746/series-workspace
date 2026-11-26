# -*- coding: utf-8 -*-
"""在 Zenodo 本地描述里**只增不改**一句「可视化阅读台」。幂等。给出前/后字数。"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
Z = os.path.join(ROOT, "_zenodo")
MARK = "可视化阅读台"

HTML_ADD = ('<p><b>可视化阅读台。</b>本件另附两个离线单文件页面（仓库 <code>assets/</code> 下）：'
            '阅读页 <code>{slug}-reader.html</code>——三档（骨架／阅读／全展）＋ 章末审问卡，卡内四行'
            '（带走／打脸条件／证据封顶／动手）全部原文摘录；结构地图 <code>{slug}-explorer.html</code>——'
            '章际引用 3D 螺旋、部×部矩阵与附录原表台账。不联网、无外部依赖、双击即开。</p>'
            '<p><b>Reading console.</b>Two offline single-file pages ship alongside this item: a reading console '
            'with three density levels and per-chapter audit cards quoting the text verbatim, and a structure map '
            'with a chapter-citation spiral, a part-by-part matrix and the appendix ledgers. No network, no dependencies.</p>')
TXT_ADD = ('可视化阅读台。本件另附两个离线单文件页面（仓库 assets/ 下）：阅读页 {slug}-reader.html'
           '（三档＋章末审问卡，四行原文摘录）与结构地图 {slug}-explorer.html（3D 章际螺旋、部×部矩阵、附录台账）。'
           '不联网、无外部依赖、双击即开。\n'
           'Reading console. Two offline single-file pages: a reading console with three density levels and '
           'per-chapter audit cards, and a structure map with a chapter-citation spiral and the appendix ledgers.\n')


def do(path, slug, is_html):
    t = io.open(path, encoding="utf-8").read()
    if MARK in t:
        return None, len(t), len(t)
    add = (HTML_ADD if is_html else TXT_ADD).format(slug=slug)
    m = re.search(r"(<p><b>(版本信息|Edition)</b>|<p><b>Version)", t)
    if m:
        t2 = t[:m.start()] + add + t[m.start():]
    else:
        t2 = t.rstrip() + "\n" + add
    io.open(path, "w", encoding="utf-8", newline="\n").write(t2)
    return True, len(t), len(t2)


def main():
    tot0 = tot1 = 0
    rows = []
    for fn in sorted(os.listdir(os.path.join(Z, "desc"))):
        if not fn.endswith(".html"):
            continue
        slug = fn[:-5]
        ok, a, b = do(os.path.join(Z, "desc", fn), slug, True)
        tot0 += a; tot1 += b
        rows.append((fn, ok, a, b))
        p2 = os.path.join(Z, "desc_plain", slug + ".txt")
        if os.path.exists(p2):
            ok2, a2, b2 = do(p2, slug, False)
            tot0 += a2; tot1 += b2
            rows.append((slug + ".txt", ok2, a2, b2))
    for n, ok, a, b in rows:
        print(f"  {n:34} {'+' if ok else '='}  {a:6d} → {b:6d}  ({b - a:+d})")
    print(f"合计 {tot0} → {tot1}（{tot1 - tot0:+d} 字符）")


if __name__ == "__main__":
    main()
