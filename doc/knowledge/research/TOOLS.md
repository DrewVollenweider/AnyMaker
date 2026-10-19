# 工具、复现与维护

源在 `scripts/research/`。Python 3.12+ 标准库；Ghidra 导出另用已有隔离 Ghidra/JDK。输出拒绝覆盖，游戏文件始终只读。不要在活动安装内建立输出目录。

| 工具 | 责任与边界 |
| --- | --- |
| `baseline.py` 1.1.0 | 资源余量检查，单 worker/BelowNormal，完整清单、选择性复制、双遍源哈希、实际格式识别；不是原子快照 |
| `gcl_index.py` 1.3.0 | 有界长度前缀、操作数、代码/分配字段与零槽检查；本地 SQLite 函数/引用检索；不是完整 GCL parser |
| `catalog.py` 1.0.0 | 数据目录全部可解析 JSON；定义原文、JSON Pointer、哈希、FTS；不推测默认 |
| `system_map.py` | 15 主题线索与统一问题队列；关键词计数不代表理解 |
| `export_plan.py` | 数据库/输入哈希核对、单一签名、代码哈希核对后生成选定函数计划 |
| `ExportResearch.java` | Ghidra 局部反汇编、指针槽标注和近似伪代码；不修补原文件、不猜结构类型 |
| `run_export.py` | 复用归档 launcher 的参数，明确 runtime/project 路径，2 GiB 堆、一个 worker、BelowNormal、关闭全文件自动分析；校验真实产物 |
| `check_exports.py` | 每条导出指令与原字节及范围核对；不证明伪代码语义 |
| `check_static_evidence.py` | 重新解析 18 个已记录函数并逐项核对 13 个常量的格式/值/原始字节 |
| `check_historical.py` | 旧范围哈希与当前完整签名迁移；哈希变化不是机制变化证明 |
| `compare_builds.py` | 安装清单、定义字段和函数记录哈希比较；区分省略/null/布尔/数值 |
| `test_research.py` | 自有合成 fixture、全部截断点、坏槽/元数据、源变化、真实格式/扩展名冲突、省略/类型差异 |

## 新基线

```powershell
python scripts/research/baseline.py "$env:ANYMAKER_INSTALL" "$r" --steam-manifest "<SteamLibrary>/steamapps/appmanifest_4435340.acf"
python scripts/research/gcl_index.py build "$r/snapshot/bin/game.gcl" "$r/gcl"
python scripts/research/catalog.py build "$r/snapshot" "$r/catalog"
```

首次检查前至少保留快照所需磁盘+20 GiB、4 GiB 可用内存；当前基线采集时约 15–16 GiB 内存可用。大操作只串行。运行 Ghidra 前再次检查余量，必要时暂停分析；不能因用户授权而抢占游玩资源。

## 选定函数导出

`$runtime` 目录应有 `ghidra/ghidra_<version>/` 与 `jdk/<jdk>/bin/java.exe`。复用已验证 runtime，不自动运行下载脚本。`$project` 必须是不存在的普通临时路径，路径元素不得以点开始或含花括号；不要放入 `.codex` 下。`$out` 必须新建。

```powershell
python scripts/research/run_export.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "$out" "$runtime" "$project" 'hatch_manager._test_node_match'
```

runner 按 source SHA 绑定索引；记录 Java 版本、Ghidra properties/脚本哈希与资源。原始槽仍未重定位；可读标签不等于函数指针类型已恢复。GCL code_size 内含常量/填充，不能对每个字节线性反汇编后统计为有效指令。

本轮 18 个函数导出成功并检查 6,599 条指令；新 runner 另对已导出的一个节点匹配函数实际 smoke-test 通过（不增加唯一函数计数）。完整输出及 Ghidra 工程只留本地。

## 更新与历史资料

```powershell
python scripts/research/check_historical.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "<directory-of-selected-evidence-json>" "$r/historical-check.json"
python scripts/research/compare_builds.py "<old>/inventory.json" "<new>/inventory.json" "<new>/diff.json" --old-definitions "<old>/catalog/definitions.sqlite" --new-definitions "<new>/catalog/definitions.sqlite" --old-functions "<old>/gcl/index.sqlite" --new-functions "<new>/gcl/index.sqlite"
```

`check_historical.py` 接受当前六组证据的 `functions[]` camelCase 字段；其他 schema 必须明确适配，不声称所有归档格式自动兼容。定义差异以 source+ID 对齐，嵌套字段差异先报告顶层字段；不是完整字段级迁移引擎。

旧 `anymaker.py`、`structural_mounts.py`、原生生成器、Workshop 索引和 Ghidra 帮助代码继续按 [原工具说明](../TOOLS.md) 复用。本轮未重新生成游戏资产，没有改变浏览器应用或导出行为。

验证：15 项新工具测试通过；归档测试 26 项执行、25 通过、1 可选 corpus 缺失而跳过；没有执行前端 npm/browser 检查或任何新游戏运行实验。
