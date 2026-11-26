# 可视化阅读台：工程经验（2026-11-26）

> 一次性项目（26 件 × 两页）做完后归并的可复用经验。按"下次会再犯"排序，不按时间。

## 一、改生成器的纪律

1. **超 600 行、或同类补丁超 5 次 → 重写，不续补。** 这轮把 1,700 行的 `make_reader.py` 打了 20 次字符串补丁，
   第 20 次吞掉 `PAPERS = {`，整个文件编译不过。重写成 763 行后一次通过。
2. **改之前先存基线。** `for f in */interactive/*-reader.html; do wc -c "$f"; done > _baseline.txt`，
   重写后逐项比对体积／卡片数——这一步抓出两处回归（卷一沙盘丢失、《区分的语言》23/24）。
3. **补丁只做"定位-替换"，不做"插入一大段"。** 多行插入用 `write` 整段替换，不用 `replace` 拼字符串。
4. **每个断言都写进脚本，不靠肉眼。** 页面级四条：`</html>` 后无残留、末卡在附录之前、
   `375px == 375`、卡片数 == 章数。这四条抓到的 bug 比读代码多。

## 二、路径与环境

5. **Windows 的 Python 只认 `C:\`。** `/mnt/c/...` 会被解释成 `D:\mnt\c\...`；而写入方与读取方会**一致地错**，
   两边都不报错，最难查。规则：Windows 侧一律 `r"C:\..."`，WSL 侧才用 `/mnt/c`。
6. **`cmd.exe /c` 传中文 commit message 必碎**（括号、空格、全角逗号都会切词）。一律 `-F 文件`，
   且文件要放在 Windows 能读的路径（`D:\0_Article\msg.txt`），不能放 `/tmp`。
7. **临时信使文件要用完即删，且别进 `git add -A`。** 这轮把 `msg1.txt`/`msg2.txt` 提进了提交，事后 `--amend` 才清掉。

## 三、DOM 与内容抽取

8. **书与论文的表注方向相反。** 书在 `<caption>` 里；Markdown 转出的论文在 `</table>` **下方的一个 `<p>`**。
   方向反了，就会把上一张表的表名戴到下一张头上（张冠李戴，且看源码才看得见）。
9. **章末边界要取"最早的那个边"**：下一章 opener／`<h2 class="chapter">`／`<h1 class="part-title">`／
   `附录|结语|后记|参考文献|术语表|通俗导读`／`#rfoot`／`</body>`。少一个，末章的卡就掉到 `</html>` 外面。
   还要排除"第39章 结语…"这类**章题自带截断词**的情况。
10. **`本章小结` 有四种写法**：`<ol>`、`box-summary` 里的 `<ul>`、单段 `<p>`、`box` 包一层。
    再加一条兜底（章内最长的 `<p>`），才能保证"卡数 == 章数"。
11. **论文的否证条件只有一个权威源**：论文十五的 126 条总账（`LedgerReconciliation/ledger.csv`）。
    去单篇正文里正则猜，只会猜出小节标题。**跨件的元数据，先找有没有现成总账，再谈抽取。**

## 四、资源与发布

12. **SVG 进 `<img>` 走严格 XML 解析**；一个重复属性就整张拒载。内联 `<svg>` 走 HTML 宽松解析，同一文件能显示。
    要单文件自包含就内联（base64），别指望相对路径。
13. **挑"轻量数据台账"要限体积。** 只排除同名文件不够；这轮把 3.5 MB 的 reader 当成 explorer 拷了 14 份，
    造成 reader 里 iframe 套娃。条件要写成：**排除含 reader、且 <400 KB**。
14. **GitHub 同名资产不能覆盖**：先 `DELETE /releases/assets/{id}` 再 `POST`，否则 422。
15. **发版用安全序**：先建新包 → 校验资产数齐 → 才删旧 release/tag。**"删得掉、传不上"的窗口期不许开。**
16. **手工改过 `文集` 里的文件，最后必须重跑 `publish_viz.py`**，否则 `MANIFEST.txt` 与实物对不上（这轮漏过一次）。

## 五、文档

17. **README/About 的"双语"要逐段相邻，不是各写一段。** 中文段后紧跟英文段；否则就会出现"有的有、有的没有"。
18. **数字不要手填**，从 `assets/` 现场读（体积、卡数、章数）。手填的必然漂。
19. **Zenodo 描述只增不改**：插入点选在「版本信息 / Edition」**之前**，DOI／version／日期／关联标识一个字不动；
    插完跑 `description.count("*") == 0` 与 `<b>/<p>` 配平。公式里的 `*` 用 `∗`（U+2217）表示，避免与断言打架。

## 六、这轮清掉的（留痕）

- 54 个暗底金线 `part-*.svg` ＋ 生成器 `make_part_art.py`（早被 `.part-art{display:none}` 与 CSS 扉页替代）
- 6 处死 `<img class="part-art">`
- `resolution-grain/scripts/build_release_v2.py`（被 `build_release.py` 取代）
- `resolution-grain/assets/knowledge-map.html`（旧 3D 引擎，图表引本地 PNG 会缺图；已被 `resolution-grain-explorer.html` 取代）
- 15 篇论文 `interactive/` 里重复的 reader/explorer（归位到 `assets/` 后不再需要）
- 临时信使文件、`_temp/`、`/mnt/d/mnt`（路径事故产物）、文集里的中文名副本与旧 `*-阅读页.html`
