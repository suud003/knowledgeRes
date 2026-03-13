# 改写前后对照样板

## 样板 1：Config 配置文件（MonsterConfig.lua）

### 改写前（FolderDoc_01 原文节选）

```
### 4. MonsterConfig.lua（12.16KB，204行）

**职责**：怪物玩法的核心配置，包含错误码枚举、交互参数、蓝图路径、金币配置等。

**主要配置项**：

#### 4.1 错误码枚举

**EErrorCode**（怪物操作错误码，17个）：

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | Success | 成功 |
| 1 | InvalidPlayer | 无效玩家 |
...（完整17行表格）

#### 4.3 蓝图路径配置

- `MonsterActor`、`MonsterBaseActor`、`CoinActor`、`AccessControlDoor`、`MonsterFactory` 的蓝图路径
- 门锁特效路径（Level1/Level2）
- 建筑网格路径（Level1/Level2）
- 怪物等级特效路径（Level 3-6 的粒子特效）

#### 4.4 金币配置

| 参数 | 值 | 说明 |
|------|-----|------|
| MediumThreshold | 1000 | 中等金币堆阈值 |
| HighThreshold | 50000 | 大量金币堆阈值 |
| MeshPath.Low/Medium/High | 3个SM路径 | 不同金币数量对应不同Mesh |
```

### 改写后（WIKI 文档）

```
# 职责

怪物玩法的核心配置，包含错误码枚举、交互参数、蓝图路径、金币配置等。

# 主要配置项

## 错误码枚举

### EErrorCode（怪物操作错误码）

| 值 | 名称 | 说明 |
| - | - | - |
| 0 | Success | 成功 |
| 1 | InvalidPlayer | 无效玩家 |
...（保留完整表格）

## 交互参数配置

| 操作 | 长按时长(秒) | 最大距离(cm) | 超时时间(秒) | 容忍度 |
| - | - | - | - | - |
| Purchase（购买） | 0.3 | 300 | 10 | 0.8/0.95 |
...

## 金币配置

| 参数 | 值 | 说明 |
| - | - | - |
| MediumThreshold | 1000 | 中等金币堆阈值 |
| HighThreshold | 50000 | 大量金币堆阈值 |

## 蓝图路径配置

详情查看lua文件中的Blueprint字段。主要包括：

- MonsterActor、MonsterBaseActor、CoinActor、AccessControlDoor、MonsterFactory 的蓝图路径
- 门锁特效路径（Level1/Level2）
- 建筑网格路径（Level1/Level2）
- 怪物等级特效路径（Level 3-6 的粒子特效）
```

### 改写要点
1. 移除 `### 4.` 编号标题 → 改为 `# 职责` 开头
2. 移除 `（12.16KB，204行）` 文件大小信息
3. 移除 `#### 4.1` 子编号 → 改为 `## 错误码枚举`
4. 保留完整枚举表和配置参数表
5. 蓝图路径段简化为"详情查看lua文件"

---

## 样板 2：协议路由配置文件（PBRouteConfig.lua）

### 改写前（FolderDoc_01 原文节选）

```
### 1. PBRouteConfig.lua（5.98KB，163行）

**职责**：PB（Protobuf）协议路由配置，定义所有 Client↔DS 的网络协议映射。

**自动生成**：此文件由工具自动生成，请勿手动修改。

**结构**：分为 `PBRouteConfig_Client` 和 `PBRouteConfig_DS` 两张表，运行时根据 `Client` 全局变量返回对应端的配置。

**5个协议模块**：

| 模块名 | PB 文件 | Client Handler | DS Handler | 协议数 |
|--------|---------|----------------|------------|--------|
| **PlanBTShop** | `PlanBT/PlanBTShop.pb` | `PlanBT_PlanBTShop_Client_Handler` | `PlanBT_PlanBTShop_DS_Handler` | 13（含7个notify） |
...

**Shop 协议详细列表**（最复杂的模块）：

| 协议名 | 方向 | 说明 |
|--------|------|------|
| `shop_get_info_req/rsp` | C↔DS | 获取商店信息 |
...（10行详细协议表）
```

### 改写后（WIKI 文档）

```
# 职责

Protobuf协议路由配置，定义 Client↔DS 的网络协议映射。

# 结构

分为 PBRouteConfig_Client 和 PBRouteConfig_DS 两张表，运行时根据 Client 全局变量返回对应端的配置。

# 协议模块

| 模块名 | PB 文件 | Client Handler | DS Handler |
| - | - | - | - |
| PlanBTShop | PlanBT/PlanBTShop.pb | PlanBT_PlanBTShop_Client_Handler | PlanBT_PlanBTShop_DS_Handler |
| PlanBTDraw | PlanBT/PlanBTDraw.pb | PlanBT_PlanBTDraw_Client_Handler | PlanBT_PlanBTDraw_DS_Handler |
| PlanBTSignIn | PlanBT/PlanBTSignIn.pb | PlanBT_PlanBTSignIn_Client_Handler | PlanBT_PlanBTSignIn_DS_Handler |
| PlanBTIllustratedGuide | PlanBT/PlanBTIllustratedGuide.pb | PlanBT_PlanBTIllustratedGuide_Client_Handler | PlanBT_PlanBTIllustratedGuide_DS_Handler |
| PlanBTPlayerData | PlanBT/PlanBTPlayerData.pb | PlanBT_PlanBTPlayerData_Client_Handler | PlanBT_PlanBTPlayerData_DS_Handler |

具体handler定义见后续文档（TODO）
```

### 改写要点
1. 移除编号和文件大小信息
2. 移除"自动生成"的警告
3. 协议模块表移除"协议数"列（精简表格）
4. 移除 Shop 协议详细列表（过细，放在 Handler 文档中更合适）
5. 添加"TODO"提示后续补充

---

## 样板 3：表格精简规则对照

| 改写前（FolderDoc） | 改写后（WIKI） | 说明 |
|---------------------|---------------|------|
| `### 4. MonsterConfig.lua（12.16KB，204行）` | `# 职责` | 移除编号、文件大小 |
| `**职责**：怪物玩法核心配置...` | `怪物玩法核心配置...` | 移除加粗和冒号 |
| `#### 4.1 错误码枚举` | `## 错误码枚举` | 降级标题层级 |
| `**EErrorCode**（怪物操作错误码，17个）：` | `### EErrorCode（怪物操作错误码）` | 移除个数统计 |
| `蓝图路径（5个完整路径）` | `详情查看lua文件中的Blueprint字段` | 简化蓝图路径 |
| `**完整代码解读**：...（20行代码+注释）` | （移除） | 移除冗长代码段 |
| `| 协议数 |` 列 | （移除该列） | 精简表格列数 |
