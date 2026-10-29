import io, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "entropy-spiral", "source")
new = io.open(os.path.join(ROOT, "_series", "content", "entropy-ch20.html"), encoding="utf-8").read()
MAP = {20: 21, 21: 22, 22: 23, 23: 24, 24: 25}
# 1) 旧 20–24 重编号（先写临时）
tmp = {}
for old, nw in MAP.items():
    p = os.path.join(SRC, f"ch{old:02d}.html")
    t = io.open(p, encoding="utf-8", newline="").read()
    t = t.replace(f'<h2 class="chapter">第{old}章', f'<h2 class="chapter">第{nw}章', 1)
    t = re.sub(rf'id="sec{old}-(\d+)"', rf'id="sec{nw}-\1"', t)
    t = re.sub(rf"(<h3[^>]*>){old}\.(\d+)", rf"\g<1>{nw}.\2", t)
    t = re.sub(rf"(?<![\d.]){old}\.(\d+)(\s*[节表图])", rf"{nw}.\1\2", t)
    t = re.sub(rf"第\s*{old}\s*章", f"第{nw}章", t)
    tmp[nw] = t
for old in MAP:
    os.remove(os.path.join(SRC, f"ch{old:02d}.html"))
for n, t in tmp.items():
    io.open(os.path.join(SRC, f"ch{n:02d}.html"), "w", encoding="utf-8", newline="").write(t)
io.open(os.path.join(SRC, "ch20.html"), "w", encoding="utf-8").write(new)
# 2) parts.json：第五部分 16–20，第六部分 21–25
parts = json.load(io.open(os.path.join(SRC, "parts.json"), encoding="utf-8"))
idx = {}
for p in parts:
    for c in p["chapters"]:
        idx[int(c["no"])] = c
for old, nw in MAP.items():
    c = idx[old]; c["no"] = str(nw); c["file"] = f"ch{nw:02d}.html"
    c["sections"] = [re.sub(rf"^{old}\.", f"{nw}.", s) for s in c.get("sections", [])]
    idx[nw] = c
def secs(f):
    h = io.open(os.path.join(SRC, f), encoding="utf-8").read()
    return [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<h3[^>]*>([^<]*)</h3>", h)]
idx[20] = {"no": "20", "title": "把 τ 押上去：三次事前登记，与它们目前的沉默",
           "file": "ch20.html", "written": True, "sections": secs("ch20.html")}
parts[4]["chapters"] = [idx[n] for n in [16, 17, 18, 19, 20]]
parts[5]["chapters"] = [idx[n] for n in [21, 22, 23, 24, 25]]
json.dump(parts, io.open(os.path.join(SRC, "parts.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("parts:", [len(p["chapters"]) for p in parts], "总章", sum(len(p["chapters"]) for p in parts))
