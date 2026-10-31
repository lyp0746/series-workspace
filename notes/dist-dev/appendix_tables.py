# -*- coding: utf-8 -*-
"""追加附录 B 的数据表（由实算生成，不手写数字）。"""
import io
import os
import numpy as np

ROOT = r"D:\0_Article\distinction-evolution\source"
P = os.path.join(ROOT, "appendix_b.html")


def lap(n, E):
    A = np.zeros((n, n))
    for u, v in E:
        A[u, v] = A[v, u] = 1
    return np.diag(A.sum(1)) - A


def spec(L):
    return np.sort(np.linalg.eigvalsh(L))


def R_of(e):
    nz = e[np.abs(e) > 1e-9]
    return e[-1] / nz[0] if len(nz) > 1 else float("nan")


def kn(n): return [(i, j) for i in range(n) for j in range(i + 1, n)]
def kpy(n): return [(i, (i + 1) % n) for i in range(n)]
def pth(n): return [(i, i + 1) for i in range(n - 1)]
def star(n): return [(0, i) for i in range(1, n)]
def kmn(m, n): return [(i, m + j) for i in range(m) for j in range(n)]
def hyper(d): return [(i, i ^ (1 << b)) for i in range(1 << d) for b in range(d) if i < (i ^ (1 << b))]
def petersen():
    return ([(i, (i + 1) % 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
            + [(i, 5 + i) for i in range(5)])


def grid(n):
    idx = lambda i, j: i * n + j
    E = [(idx(i, j), idx(i + 1, j)) for i in range(n - 1) for j in range(n)]
    E += [(idx(i, j), idx(i, j + 1)) for i in range(n) for j in range(n - 1)]
    return n * n, E


def torus(n):
    idx = lambda i, j: (i % n) * n + (j % n)
    E = [(idx(i, j), idx(i + 1, j)) for i in range(n) for j in range(n)]
    E += [(idx(i, j), idx(i, j + 1)) for i in range(n) for j in range(n)]
    return n * n, E


rows = []
fams = [("完全图 K_5", 5, kn(5)), ("完全图 K_8", 8, kn(8)),
        ("完全二部 K_2,3", 5, kmn(2, 3)), ("完全二部 K_3,7", 10, kmn(3, 7)),
        ("星 K_1,6", 7, star(7)), ("星 K_1,9", 10, star(10)),
        ("环 C_6", 6, kpy(6)), ("环 C_10", 10, kpy(10)), ("环 C_20", 20, kpy(20)),
        ("路 P_6", 6, pth(6)), ("路 P_10", 10, pth(10)), ("路 P_20", 20, pth(20)),
        ("超立方 Q_3", 8, hyper(3)), ("超立方 Q_4", 16, hyper(4)),
        ("Petersen", 10, petersen()),
        ("网格 5×5", 25, grid(5)[1]), ("网格 8×8", 64, grid(8)[1]),
        ("环面 4×4", 16, torus(4)[1]), ("环面 6×6", 36, torus(6)[1])]
for name, n, E in fams:
    e = spec(lap(n, E))
    rows.append((name, n, e[1], e[-1], R_of(e), len({round(x, 6) for x in e})))

tbl = ['<h3 id="secb6">B.6　十九个图的谱与 R（实算）</h3>',
       '<p>下表全部由 <code>analysis/figures_rewrite.py</code> 的同一段代码算出，未手抄。'
       '最后一列是谱的不同取值个数，用来判断谱的“离散程度”：完全图只有一个非零值，'
       '网格与环面的取值个数随规模增长。</p>',
       '<table class="nat">',
       '<tr><th class="l">图</th><th class="l">n</th><th class="l">λ₂</th><th class="l">λₙ</th><th class="l">R</th><th class="l">谱不同值数</th></tr>']
for name, n, l2, ln, R, k in rows:
    tbl.append('<tr><td class="l">%s</td><td class="l">%d</td><td class="l">%.4f</td><td class="l">%.4f</td><td class="l">%.3f</td><td class="l">%d</td></tr>'
               % (name, n, l2, ln, R, k))
tbl.append('</table>')

# κ 表
tbl += ['<h3 id="secb7">B.7　谱方差量 κ 的实测</h3>',
        '<p>κ=½Var(λ)。注意它与 R 的行为相反：<b>κ 有统一上界（因为 0≤λ≤2Δ），而 R 无界。</b>'
        '这条对照是附录 D 中 R4 的数值依据。</p>',
        '<table class="nat"><tr><th class="l">图</th><th class="l">Var(λ)</th><th class="l">κ=½Var</th><th class="l">R</th></tr>']
for name, n, E in [("K_8", 8, kn(8)), ("C_10", 10, kpy(10)), ("P_10", 10, pth(10)),
                   ("Petersen", 10, petersen()), ("网格 8×8", 64, grid(8)[1]),
                   ("网格 12×12", 144, grid(12)[1]), ("环面 6×6", 36, torus(6)[1])]:
    e = spec(lap(n, E))
    tbl.append('<tr><td class="l">%s</td><td class="l">%.4f</td><td class="l">%.4f</td><td class="l">%.3f</td></tr>'
               % (name, float(np.var(e)), float(np.var(e)) / 2, R_of(e)))
tbl.append('</table>')

# Lyapunov 表
tbl += ['<h3 id="secb8">B.8　Lyapunov 谱随耦合的符号变化</h3>',
        '<p>取 Petersen 图（λₙ=5、λ₂=2），α=1。表中每格是 μ_k=βλ_k−α 的符号（+/−），'
        '可以看到 <b>β 跨过 0.2 时最高频先变正，跨过 0.5 时最低非平凡才变正</b>——'
        '这就是定理 17.1 的表格版。</p>',
        '<table class="nat"><tr><th class="l">β</th><th class="l">λₙ=5</th><th class="l">λ=3</th><th class="l">λ₂=2</th><th class="l">已解锁</th></tr>']
for beta in (0.10, 0.19, 0.21, 0.35, 0.49, 0.51, 0.80):
    sig = [("+" if beta * l > 1 else "−") for l in (5, 3, 2)]
    tbl.append('<tr><td class="l">%.2f</td><td class="l">%s</td><td class="l">%s</td><td class="l">%s</td><td class="l">%d</td></tr>'
               % (beta, sig[0], sig[1], sig[2], sum(1 for s in sig if s == "+")))
tbl.append('</table>')

# 网格收敛表
tbl += ['<h3 id="secb9">B.9　网格与环面的收敛（扩展表）</h3>',
        '<table class="nat"><tr><th class="l">n</th><th class="l">网格 R</th><th class="l">(8/π²)n²</th><th class="l">环面 R</th><th class="l">(2/π²)n²</th><th class="l">λ₂(网格)/h²</th></tr>']
for n in (6, 8, 10, 16, 20, 32, 40, 64, 80):
    g2 = 2 - 2 * np.cos(np.pi / n); gn = 2 * (2 - 2 * np.cos(np.pi * (n - 1) / n))
    t2 = 2 - 2 * np.cos(2 * np.pi / n)
    tbl.append('<tr><td class="l">%d</td><td class="l">%.1f</td><td class="l">%.1f</td><td class="l">%.2f</td><td class="l">%.1f</td><td class="l">%.4f</td></tr>'
               % (n, gn / g2, 8 / np.pi ** 2 * n * n, 8 / t2, 2 / np.pi ** 2 * n * n, g2 * n * n))
tbl.append('</table>')
tbl.append('<p>最后一列单调上升趋近 π²=9.8696；两族 R 的比值稳定在 4 附近（第 19.3b 节解释了这个 4 的来源）。</p>')

s = io.open(P, encoding="utf-8").read()
s = s.rstrip() + "\n\n" + "\n".join(tbl) + "\n"
io.open(P, "w", encoding="utf-8").write(s)
print("附录 B 追加四张表，行数：", len(rows))
