# -*- coding: utf-8 -*-
"""html2mathml.py —— 把书稿里手写的公式 HTML 转成 MathML（Chrome 原生渲染）。

用法：
    from html2mathml import convert
    convert('<i>X</i> → <i>Z</i>　⟹　<i>I</i>(<i>X</i>;<i>Y</i>)')   # -> '<math ...>…</math>'

设计：宽容优先。认不出的结构一律退成 <mtext>（正体），行为与原来的 HTML 文本一致，
不会比现状更差；认得出的结构（变量斜体、下标、分数、求和、运算符间距）按 ISO 80000-2
的排版惯例交给 MathML 处理——这正是 Axler 那本书的写法。

只处理“一个公式”的片段，不含 <p>/<div>。
"""
import html
import re

# 这些多字母串按“函数名/算子”排成正体（Axler：span、dim、min、max 都是正体）
FUNCS = {"min", "max", "arg", "argmax", "argmin", "span", "log", "ln", "exp",
         "Var", "Cov", "Err", "det", "dim", "rank", "KL", "cos", "sin", "tan",
         "supp", "inf", "sup", "lim", "Pr", "E", "median", "Risk", "Hazard",
         "Exposure", "AdaptiveCapacity", "ReLU", "softmax", "top", "k"}

# 二元/关系运算符：交给 <mo>，由 MathML 负责两侧的空隙
BIG = set("∑Σ∏Π∐∫∮⋃⋂⋁⋀")
BIN = set("=+−-*/<>≤≥≠≈∼~≡∝→←↔⇒⇔⟹⟸∈∉⊂⊆⊇⊃∪∩±∓×·⋅∗÷⊕⊗⊖∧∨∇∂≪≫")
FENCE = set("()[]{}")
PUNCT = set(",;:")
OPS = BIG | BIN | FENCE | PUNCT | set("∞∥|!?/")

CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]+")
WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")
NUM = re.compile(r"\d+(?:\.\d+)?")

TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)([^>]*)>")


def _esc(s):
    return html.escape(s, quote=False)


class Tok:
    """一个已归类的片段。kind: mi mn mo mtext frac sub sup"""
    __slots__ = ("kind", "text", "inner")

    def __init__(self, kind, text="", inner=None):
        self.kind, self.text, self.inner = kind, text, inner

    def emit(self):
        if self.kind == "frac":
            return "<mfrac><mrow>%s</mrow><mrow>%s</mrow></mfrac>" % (
                tokens_to_mathml(self.inner[0]), tokens_to_mathml(self.inner[1]))
        if self.kind == "msub":
            return "<msub>%s%s</msub>" % (self.text, tokens_to_mathml(self.inner))
        if self.kind == "msup":
            return "<msup>%s%s</msup>" % (self.text, tokens_to_mathml(self.inner))
        if self.kind == "munder":
            return "<munder>%s%s</munder>" % (self.text, tokens_to_mathml(self.inner))
        if self.kind == "mi":
            if CJK.match(self.text or ""):
                return "<mtext>%s</mtext>" % _esc(self.text)
            # 单字母＝变量（斜体）；多字母标识符与函数名一律正体
            normal = self.text in FUNCS or len(self.text) > 1
            attrs = ' mathvariant="normal"' if normal else ""
            return "<mi%s>%s</mi>" % (attrs, _esc(self.text))
        if self.kind == "mbold":
            return '<mi mathvariant="bold">%s</mi>' % _esc(self.text)
        if self.kind == "mn":
            return "<mn>%s</mn>" % _esc(self.text)
        if self.kind == "mo":
            return "<mo>%s</mo>" % _esc(self.text)
        return "<mtext>%s</mtext>" % _esc(self.text)


def _classify(text):
    """把一段纯文本切成 mi/mn/mo/mtext 序列；处理 a_b 形式的隐含下标。"""
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "_^":                      # 隐含上下标：κ_info、a_0
            m = WORD.match(text, i + 1) or NUM.match(text, i + 1)
            if m and out:
                inner = [Tok("mn" if m.group(0)[0].isdigit() else "mi", m.group(0))]
                prev = out.pop()
                out.append(Tok("msub" if ch == "_" else "msup", prev.emit(), inner))
                i = m.end(); continue
            i += 1; continue
        m = CJK.match(text, i)
        if m:
            out.append(Tok("mtext", m.group(0))); i = m.end(); continue
        m = NUM.match(text, i)
        if m:
            out.append(Tok("mn", m.group(0))); i = m.end(); continue
        m = WORD.match(text, i)
        if m:
            out.append(Tok("mi", m.group(0))); i = m.end(); continue
        if ch in BIG:
            out.append(Tok("mo", ch)); i += 1; continue
        if ch in OPS:
            out.append(Tok("mo", ch)); i += 1; continue
        # 其余（希腊字母、带附标的字母等）按变量（斜体）处理
        out.append(Tok("mi", ch)); i += 1
    return out


def _parse(fragment):
    """把 HTML 片段解析成嵌套列表：('t', text) 或 ('tag', name, attrs, children)。"""
    root = []
    stack = [root]
    pos = 0
    for m in TAG.finditer(fragment):
        if m.start() > pos:
            stack[-1].append(("t", html.unescape(fragment[pos:m.start()])))
        closing, name, attrs = m.group(1) == "/", m.group(2).lower(), m.group(3)
        if not closing:
            node = ("tag", name, attrs, [])
            stack[-1].append(node)
            if name not in ("br", "img", "hr"):
                stack.append(node[3])
        else:
            if len(stack) > 1:
                stack.pop()
        pos = m.end()
    if pos < len(fragment):
        stack[-1].append(("t", html.unescape(fragment[pos:])))
    return root


def _flatten(nodes):
    """展平成 (kind, payload) 流：text / i / b / sub / sup / other。"""
    out = []
    for nd in nodes:
        if nd[0] == "t":
            out.append(("text", nd[1]))
        else:
            _, name, attrs, kids = nd
            if name in ("sub", "sup"):
                out.append((name, _flatten(kids)))
            elif name in ("i", "em"):
                out.append(("i", _flatten(kids)))
            elif name in ("b", "strong"):
                out.append(("b", _flatten(kids)))
            elif name == "span":
                out.append(("other", _flatten(kids)))
            else:
                out.append(("other", _flatten(kids)))
    return out


def _emit(nodes):
    """把展平流变成 Tok 列表，并把 sub/sup 粘到前一个元素上。"""
    toks = []
    for kind, payload in nodes:
        if kind == "text":
            toks.extend(_classify(payload))
        elif kind == "i" or kind == "b":
            inner = _emit(payload)
            txt = "".join(t.text for t in inner)
            if kind == "b":
                toks.append(Tok("mbold", txt))          # 粗体向量
            else:
                toks.append(Tok("mi", txt or " "))
        elif kind in ("sub", "sup"):
            inner = _emit(payload)
            prev = toks.pop() if toks else Tok("mi", "")
            base = prev.emit()
            if prev.kind == "mo" and prev.text in ("∑", "∏", "⋃", "⋂", "∫", "⊕", "⊗"):
                toks.append(Tok("munder" if kind == "sub" else "msup", base, inner))
            else:
                toks.append(Tok("msub" if kind == "sub" else "msup", base, inner))
        else:
            toks.extend(_emit(payload))
    return toks


def tokens_to_mathml(toks):
    return "".join(t.emit() for t in toks)


FRAC = re.compile(r"\(([^()<>\s]{1,24})/([^()<>\s]{1,24})\)")


def convert(fragment, display=False):
    """返回 <math> 片段。display=True 为独立公式。"""
    pending = []

    def grab(m):
        pending.append((m.group(1), m.group(2)))
        return chr(0xE000 + len(pending) - 1)      # 单个私用字符占位，不会被切碎

    frag = FRAC.sub(grab, fragment)
    toks = _emit(_flatten(_parse(frag)))

    def emit_frac(num, den):
        return "<mfrac><mrow>%s</mrow><mrow>%s</mrow></mfrac>" % (
            tokens_to_mathml(_emit(_flatten(_parse(num)))),
            tokens_to_mathml(_emit(_flatten(_parse(den)))))

    out = []
    for tk in toks:
        s = tk.emit()
        if tk.kind == "mi" and len(tk.text) == 1 and 0xE000 <= ord(tk.text) <= 0xF8FF:
            num, den = pending[ord(tk.text) - 0xE000]
            s = emit_frac(num, den)
        out.append(s)
    body = "".join(out)
    tag = '<math display="block">' if display else "<math>"
    return tag + body + "</math>"


if __name__ == "__main__":
    tests = [
        "<i>X</i> → <i>Z</i>　⟹　<i>I</i>(<i>X</i>;<i>Y</i>) ≤ <i>I</i>(<i>X</i>;<i>Z</i>)",
        "<i>L</i><sub>IB</sub> = <i>I</i>(<i>X</i>;<i>Z</i>) + <i>β</i> · <i>I</i>(<i>Z</i>;<i>Y</i>)",
        "Σ<sub>i</sub> Ṡ<sub>i</sub> + Σ<sub>i&lt;j</sub> Ξ<sub>ij</sub>",
        "κ_info(G) = (1/2) Var(λ)",
        "Θ<sub>debt</sub> ≈ w<sub>h</sub>·(家庭债务/GDP) + w<sub>f</sub>·(企业债务/GDP)·π<sub>fin</sub>",
        "λ<sub>2</sub>=2−2cos(π/n)",
    ]
    for t in tests:
        print("IN ", t)
        print("OUT", convert(t, display=True))
        print()
