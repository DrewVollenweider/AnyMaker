# 全游戏研究入口 / Whole-game research

2026-10-18（America/New_York）。这是持续研究系统的首个全游戏基线检查点，不是“已理解整个游戏”的声明。先看 [覆盖矩阵](COVERAGE.md)、[版本记录](VERSIONS.md) 和 [交接](HANDOFF.md)，再按 [系统索引](versions/build-25904830/system-map.json) 检索。原有 [当前工程结论](../CURRENT-FACTS.md) 和验收记录继续有效，但必须保留各自版本和证据边界。

本轮完成全安装双遍 SHA-256 清单、隔离快照、现有研究复核、定义索引、GCL 函数记录/引用索引、历史地址迁移检查，以及 Opening/Hatch 密封链的首次深入静态研究。没有启动、附加或操纵游戏，也没有修改安装目录或活动存档。运行实验尚未执行。

## 如何回答问题

1. 确认 Steam build、输入 SHA-256 和分析工具 SHA-256，禁止混用旧地址。
2. 在定义数据库查询原始字段；省略字段保留为省略，不擅自填默认值。
3. 在 GCL 数据库按完整签名查函数，沿符号引用查调用方，再检查原始代码和反汇编。符号引用不是已经执行的调用。
4. 检查代表性原生文件，区分加载状态、静态连接和历史运行验收。
5. 用 [证据分类](#证据分类) 写出已知内容和边界；运行时歧义转入 [实验协议](EXPERIMENTS.md)。
6. 添加可复现命令、输入哈希、结果、反例和下一步。完整反编译、二进制、ROM、个人存档只留本地。

## 检索与工具

Python 3.12+，索引和基本解析只使用标准库。命令从仓库根运行；`$r` 指向仓库外独立研究目录。输出目录必须是新目录，已有输出不会被覆盖。

```powershell
python scripts/research/gcl_index.py build "$r/snapshot/bin/game.gcl" "$r/gcl"
python scripts/research/catalog.py build "$r/snapshot" "$r/catalog"
python scripts/research/gcl_index.py query "$r/gcl/index.sqlite" hatch_manager
python scripts/research/gcl_index.py query "$r/gcl/index.sqlite" hatch_manager.tick --callers
python scripts/research/catalog.py query "$r/catalog/definitions.sqlite" 'microcontroller OR battery'
python scripts/research/system_map.py "$r/gcl/index.sqlite" "$r/catalog/definitions.sqlite" "$r/system-map.json"
python -m unittest discover -s scripts/research -p test_research.py -v
```

`gcl/index.sqlite` 保存完整本地签名、代码范围/哈希、重定位操作数、全局/源文件表和引用解析状态。`catalog/definitions.sqlite` 保存定义 JSON、JSON Pointer、来源/规范化定义哈希和全文搜索。可按 `functions.record` 和 `definitions.json` 取原始记录；原始定义不在轻量组件索引中重复发布。

[工具与维护](TOOLS.md) 给出基线、Ghidra、历史证据检查和升级比较命令。当前机器的精确本地路径在工作区 `RESEARCH-HANDOFF.md`，不写入公共仓库。

## 证据分类

| 类别 | 含义 |
| --- | --- |
| `shipped` | 发布的文档/定义明确写出的内容，尚不等于运行实现 |
| `static` | 按匹配版本检查实现、调用关系或原始字节得到的结论 |
| `runtime` | 实际游戏观察；注明操作者、初始状态、控制变量和观测范围 |
| `inference` | 有支持的推论，写明推理桥梁及可能反例 |
| `hypothesis` | 待检验解释，不能写作结果 |
| `unknown` | 尚无足够证据，记录下一步 |

置信程度与证据类别分开记录。函数数量、关键词命中、成功反编译、静态审核通过都不计作系统运行验收。

本轮新增实质结论见 [Opening/Hatch](SEALING.md)。目前没有全系统的单位表、完整类型恢复、完整 GCL 容器语法、通用运行时遥测或万能反编译器。
