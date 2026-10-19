# Opening / Hatch：从几何到浮力密封

证据：`static`；置信程度高的是下列具体代码条件，运行表现仍未验证。仅适用于 build 25904830、GCL `626a994b…`。见 [函数记录](versions/build-25904830/sealing-records.json)、[常量字节](versions/build-25904830/sealing-constants.json) 和 [逐指令核对](versions/build-25904830/export-check.json)。完整伪代码/反汇编只留本地，按签名和哈希可重新生成。

## 已建立的路径

建造工具返回的 plate 枚举中 Opening=2，Hatch=3。`server_scene.vehicle._rebuild_buoyancy` 在重建浮力后调用 hatch manager 重建登记。`rebuild_vehicle_hatches` 按 plate type 分别登记两类对象；两类记录包含 vehicle、plate ID、面积、法向、简化后的顶点及已配对对象。

`_get_plate_node_positions_simplified` 使用面板节点、面支撑偏移和原生节点位置；同方向连续边不会全部作为独立转角保存。因此不能只比较原始 `plates[].nodes` 的数组长度，也不能只比较两个组件/载具原点。

`_check_hatch_opening_match` 的核心条件为：

1. 两边简化节点列表均非空，数量相同。
2. 面积差的绝对值 **≤0.001**（原生面积返回量；本轮不擅自换算成 m²）。
3. 法向经各自 vehicle 的世界旋转后，点积 **≤−0.99**，即要求接近相反朝向。
4. 用各自完整世界变换比较节点。先找满足距离测试的最近首节点，再检查正向和反向两种循环对应；任一整圈通过即可。
5. `_test_node_match` 要求距离平方 **严格小于** `g_node_match_threshold_sq`。初始化值为 **0.02**，平方在独立 ctor 中计算；恰好在阈值处不通过。0.02 是该路径的原生世界坐标量，未用修改后的几何做实验。

该函数读取面积、法向、顶点和 vehicle 变换，没有在此谓词中查询 latch 是否 engagement。由此可以说“密封匹配谓词中未发现直接锁紧条件”；不能扩展成“所有门的锁都没有影响”，因为锁可能通过保持物理姿态间接影响匹配。

manager `tick` 将尚未配对的 hatch 与尚未配对的 opening 比较。匹配后双方互指，并调用 `vehicle_buoyancy.set_is_plate_opening_sealed(..., true)`；已配对对象不再满足匹配条件时设置 false 并清理关系。这支持一对一配对与随姿态变化解除密封的解释。匹配对象选择依赖遍历顺序；重叠的多个候选和精确 tick 调度尚未做运行验证。

`set_is_plate_opening_sealed` 按 plate ID 写入浮力 plate 的 **+0xc2** 字节。`vehicle_buoyancy._calculate_forces` 的开口流动分支读取同一字节，并要求其为 **0**；随后水量变化用覆盖面积/水位、`g_opening_flow_rate` 和 `g_server_delta_time` 计算并限幅。这把匹配结果连到了实际水流路径，而非只找到含有 “seal” 的名称。

## 可回答与不可回答

`static`：Hatch 的形状、对应节点、面积、方向和世界位置确实进入密封判定。几何失配会使现有配对解除并清除 seal 标志。配对谓词不是一个单纯的 latch 状态判断。

`inference`：代码路径支持“Opening 是可被匹配 Hatch 密封的浮力开口”，不支持“Opening 无条件阻水”的泛化。完整初始状态/异常几何仍须继续追踪 `vehicle_buoyancy.create` 和 plate 默认构造，不能把本轮部分路径写成全状态形式证明。

`unknown`：玩家是否可穿过每种 Opening 几何、边框碰撞、Hatch 的实体碰撞，以及打开后实际进水速度/可见水位。`vehicle_plate_util.add_static_geometry` 已确认按 type 分派 opening/window/hatch/solid 内部几何，再生成外边；这尚未证明具体碰撞构建和玩家胶囊的路径，不能将渲染空洞当成穿行验收。

`unknown`：锁紧对持续密封的间接影响、运动抖动、服务器/客户端表现、存读后的密封恢复、复杂非凸/简化边界和多个候选。没有执行游戏实验。

## 关键地址（仅此输入哈希）

| 函数 | code offset / bytes | 已核对用途 |
| --- | --- | --- |
| `_check_hatch_opening_match` | 53415309 / 3744 | 几何判定及循环匹配 |
| `_test_node_match` | 53425275 / 96 | 距离平方严格比较，RIP 槽 96/104 |
| `g_node_match_threshold.$ctor` | 53434854 / 32 | 0.02 初始化 |
| `g_node_match_threshold_sq.$ctor` | 53435590 / 40 | 阈值自乘 |
| `hatch_manager.tick` | 53440764 / 992 | 配对、true/false 调用 |
| `set_is_plate_opening_sealed` | 62326512 / 256 | 按 plate ID 写 +0xc2 |
| `_calculate_forces` | 62056483 / 20736 | 同字段控制 opening flow 分支 |

导出的 18 个函数并非 18 个完整理解的函数。例如完整 `_calculate_forces`、浮力表面重建和物理创建只检查了相关路径；其余分支继续标为未解释。完整 Ghidra 调用约定/结构类型仍未恢复。
