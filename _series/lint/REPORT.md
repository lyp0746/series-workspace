# 校阅账（lint v2）

规则：`_series/spec/skeleton.md` v2　｜　对象：23 件（9 书 / 14 篇）
**error 0　warn 4**

| 件 | 等级 | 字数(正文/附录) | 附录 | 主要问题 |
|---|---|---:|---:|---|
| knowledge-tradeoffs | ok | 43,877 / 2,914 | 6 |  |
| distinction-evolution | ok | 66,676 / 2,094 | 4 |  |
| capacity-cascade | ok | 75,578 / 11,549 | 5 |  |
| entropy-spiral | ok | 138,663 / 22,193 | 6 |  |
| impossibility-triangle | ok | 75,864 / 36,197 | 5 |  |
| interpretation-tradeoff | ok | 77,374 / 18,757 | 5 |  |
| emergence-critical | ok / warn 2 | 87,001 / 8,840 | 23 | 附录字母不连续：A B C D E F H I J K L M N O P Q ; 附录 23 节 > 6 |
| mind-forks | ok | 136,086 / 9,823 | 4 |  |
| hotspot-bills | ok / warn 2 | 46,288 / 1,766 | 10 | 附录字母不连续：A B C D F G H I J K; 附录 10 节 > 6 |
| ComputingDemystified | ok | 24,800 / 1,593 | 6 |  |
| WorldPeriodization | ok | 15,428 / 3,080 | 3 |  |
| SleepingResidue | ok | 23,604 / 2,865 | 4 |  |
| HunanRelaySystem | ok | 26,889 / 2,913 | 5 |  |
| BureauRotationCession | ok | 37,847 / 4,773 | 6 |  |
| HarnessEcology | ok | 19,287 / 2,331 | 6 |  |
| OptimizationBoundary | ok | 16,813 / 2,125 | 5 |  |
| CapacityProxies | ok | 17,043 / 446 | 3 |  |
| DomainCrossSection | ok | 22,930 / 2,990 | 3 |  |
| IsomorphismStrength | ok | 21,260 / 2,632 | 3 |  |
| MemoryAnchor | ok | 19,922 / 3,333 | 3 |  |
| MemoryStressTest | ok | 16,980 / 2,936 | 6 |  |
| LedgerReconciliation | ok | 23,919 / 2,440 | 4 |  |
| MonarchCompetition | ok | 23,163 / 2,743 | 3 |  |

## emergence-critical
- `02` w 附录字母不连续：A B C D E F H I J K L M N O P Q R S T U V W B（期望 A B C D E F G H I J K L M N O P Q R S T U V W）
- `04` w 附录 23 节 > 6（同文件分节；skeleton §4 要求 ≤6 件，建议合并）

## hotspot-bills
- `02` w 附录字母不连续：A B C D F G H I J K（期望 A B C D E F G H I J）
- `04` w 附录 10 节 > 6（同文件分节；skeleton §4 要求 ≤6 件，建议合并）
