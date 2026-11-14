# -*- coding: utf-8 -*-
"""《明清湘中驿道体系》图件统一入口（fig01—fig09）。

三张脚本各管一段，风格统一由 `_series/tools/figstyle.py` 提供（Okabe–Ito 配色、
300 dpi、constrained_layout、图内不写标题）：

  make_figures_gepf.py → fig01—fig07（GEPF 三层、驿铺配置、商品流、密度、成本、地名、三百年）
  analysis/gis_pilot.py → fig08（28 节点经纬投影）
  analysis/robustness.py → fig09（jackknife 与蒙特卡洛）

用两个解释器路径都行：

    python analysis/make_figures.py

单跑某一段时直接调用对应脚本即可。
"""
import pathlib
import runpy

BASE = pathlib.Path(__file__).resolve().parent.parent
for script in ("make_figures_gepf.py", "analysis/gis_pilot.py", "analysis/robustness.py"):
    print("==", script)
    runpy.run_path(str(BASE / script), run_name="__main__")
