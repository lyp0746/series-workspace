# 数据源（文本）

> 状态：**已编码**（2026-10-23）。60 部来源（核心 46、扩展 14）、252 条边界；编码手册见 `docs/codebook.md`，
> 数据见 `data/schemes.py` 与 `data/schemes.csv`，统计量见 `data/stats.json`。
> 只记录年份与时期名，不复制原文。

## 三组传统与来源

| 组 | 例 | 数量目标 |
|---|---|---|
| 欧洲中心 | Western civilization 教材（Spielvogel、McKay）、Britannica 世界史条目、剑桥世界史卷目 | 10—15 |
| 全球史 | Bentley & Ziegler《Traditions & Encounters》、McNeill《A World History》、Stavrianos、AP World History 时期表 | 10—15 |
| 中国教材 | 吴于廑/齐世荣《世界史》、中学历史教材、世界近代史/现代史教材 | 10—15 |
| 补充 | 维基 "Periodization" / "List of time periods" | 3—5（仅补充） |

## 编码字段

```
source, year_published, tradition, scope, boundary_year, period_name, region, note, coder
```

- `tradition`：european / global / china / other
- `scope`：world / region / nation
- `boundary_year`：该来源**明确写出**的年份；没有就 NA，不推断
- `period_name`：该边界开启的时期名（如"近代早期"）
- `region`：欧洲 / 亚洲 / 非洲 / 全球 / 未注明

## 五条编码规则（先定，后编码）

1. 边界年 = 明确写出的年份；没有就 NA。
2. 多边界（"1453/1492"）分别记录，不取平均。
3. "近代早期"这类区间，记起止两个边界年。
4. 来源版本以实际使用的版次为准，记 `year_published`。
5. 维基只作补充；去掉维基后结论须不变。

## 坑

1. 教材目录常只给章名不给年 → 记 NA，不补。
2. "中世纪"起点在不同传统里是 395/476/500 → 分别记，不统一。
3. 中国教材的"近代"起点是 1640，与欧洲中心的 1500 不同 → 必须按来源记。
4. 同一来源的不同卷可能给不同边界 → 记 `note`。
5. "全球史"来源未必没有欧洲中心 → 按实际边界编码，不按书名归类。

## 版权

教材与工具书受版权保护：**只编码年份与时期名，不复制段落**；引用不超过必要长度。
