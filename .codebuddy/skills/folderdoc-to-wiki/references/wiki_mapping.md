# WIKI 文档映射配置

## 已有 WIKI 节点（固定 ID）

| 节点名称 | docid | 类型 | 说明 |
|---------|-------|------|------|
| 个人空间 | 4010703137 | spaceid | iWiki 空间 ID |
| 5.1 偷走脑腐 | 4018569240 | 文件夹 | Showcase 根节点 |
| 快速开始 | 4018569234 | 文档 | FolderDoc_00 整合目标 |
| 模块说明 | 4018569751 | 文件夹 | |
| GM面板 | 4018569782 | 文档 | |
| API参考手册 | 4018569206 | 文件夹 | FolderDoc_01~05 整合根节点 |
| ModConfig.lua | 4018569436 | 文档 | FolderDoc_01 已整理 |
| GamePlay/ | 4018569259 | 文件夹 | |
| Config/ | 4018577057 | 文件夹 | FolderDoc_01 已整理（14个子文档） |
| Dev/ | 4018569491 | 文件夹 | |
| Tools/ | 4018575600 | 文件夹 | |

## Config/ 子文档（FolderDoc_01 已整理）

| 文档标题 | docid |
|---------|-------|
| PBRouteConfig.lua | 4018576894 |
| SubsystemConfig.lua | 4018576947 |
| EventDefine.lua | 4018576964 |
| MonsterConfig.lua | 4018577003 |
| ItemConfig.lua | 4018577657 |
| ShopConfig.lua | 4018577820 |
| SkinConfig.lua | 4018578416 |
| ActiveConfig.lua | 4018582092 |
| DrawConfig.lua | 4018583859 |
| RoundFlowTriggersCfg.lua（没看懂） | 4018584035 |
| RebirthUIConfig.lua | 4018584540 |
| OfflineCoinConfig.lua | 4018584797 |
| EnumDefine.lua | 4018584934 |
| CreativeSubModeOverrideConfig.lua | 4018584949 |

## FolderDoc → WIKI 映射关系

### FolderDoc_00 → 快速开始 (4018569234)

更新已有文档，整合游戏总览内容。

### FolderDoc_01 → API参考手册 (4018569206)（已完成）

- ModConfig.lua (4018569436)
- GamePlay/Config/ (4018577057) → 14个子文档
- Dev/ (4018569491)
- Tools/ (4018575600)

### FolderDoc_02 → API参考手册/GamePlay/ (4018569259)（已完成）

- Core/(4018588518) → 6个子文档
- Actor/(4018588519) → 13个子文档
- Feature/(4018588522) → 8个子文档
- SubSystem/(4018588523) → 2个子文档
- Skill/(4018588526) → 7个子文档
- Backpack/(4018588528) → 1个子文档
- Component/(4018588530) → 1个子文档
- Utils/(4018588532) → 3个子文档

### FolderDoc_03a → API参考手册/Client/ (4018588867)（已完成）

- ClientLogicEntry.lua(4018588885)
- Config/(4018588868) → 4个子文档
- Handler/(4018588870) → 5个子文档
- SubSystem/(4018588872) → 1个子文档
- Shop/(4018588873)、Draw/(4018588874)、SignIn/(4018588875)、IllustratedGuide/(4018588876)、Result/(4018588877) → 各1个子文档
- InGameUI/(4018588879) → 2个子文档
- ShootingUI/(4018588884) → 1个子文档

### FolderDoc_03b → Client/UI/ (4018589745)（已完成）

- 根级7个文档 + Item/(4018589750)1个 + Shop/(4018589756)5个 + SignIn/(4018589762)3个 + IllustratedGuide/(4018589766)3个 + Turntable/(4018589767)7个 + Skin/(4018589771)1个 + SkillButton/(4018589774)1个

### FolderDoc_04 → API参考手册/DS/ (4018590565)（已完成）

- 根级3个文档 + Config/(4018590566)2个 + Handler/(4018590568)5个 + Subsystem/(4018590570)3个 + Shop/(4018590573)1个 + Draw/(4018590575)1个 + SignIn/(4018590579)1个 + IllustratedGuide/(4018590582)1个 + SimulateServer/(4018590585)1个 + Utils/(4018590586)3个

### FolderDoc_05 → Dev/(4018569491) + Common/(4018591021)（已完成）

- Dev/GMCheatManager.lua(4018590996) + Dev/Config/(4018590990) → GMConfig.lua(4018591002) + GMFuncConfig.lua(4018591009)
- Common/(4018591021) → UICanvas/(4018591022) → Action/(4018591024) → 5个 CanvasAction 文档

---

## 动态创建的 WIKI 节点（已完成）

> 以下节点在执行任务 2~7 过程中创建，docid 已全部填入。

### GamePlay/ 下新建的文件夹

| 文件夹名 | docid | 父级 |
|---------|-------|------|
| Core/ | 4018588518 | GamePlay/(4018569259) |
| Actor/ | 4018588519 | GamePlay/(4018569259) |
| Feature/ | 4018588522 | GamePlay/(4018569259) |
| SubSystem/ | 4018588523 | GamePlay/(4018569259) |
| Skill/ | 4018588526 | GamePlay/(4018569259) |
| Backpack/ | 4018588528 | GamePlay/(4018569259) |
| Component/ | 4018588530 | GamePlay/(4018569259) |
| Utils/ | 4018588532 | GamePlay/(4018569259) |

### Client/ 文件夹结构

| 文件夹名 | docid | 父级 |
|---------|-------|------|
| Client/ | 4018588867 | API参考手册(4018569206) |
| Client/Config/ | 4018588868 | Client/(4018588867) |
| Client/Handler/ | 4018588870 | Client/(4018588867) |
| Client/SubSystem/ | 4018588872 | Client/(4018588867) |
| Client/Shop/ | 4018588873 | Client/(4018588867) |
| Client/Draw/ | 4018588874 | Client/(4018588867) |
| Client/SignIn/ | 4018588875 | Client/(4018588867) |
| Client/IllustratedGuide/ | 4018588876 | Client/(4018588867) |
| Client/Result/ | 4018588877 | Client/(4018588867) |
| Client/InGameUI/ | 4018588879 | Client/(4018588867) |
| Client/ShootingUI/ | 4018588884 | Client/(4018588867) |
| Client/UI/ | 4018589745 | Client/(4018588867) |
| Client/UI/Item/ | 4018589750 | UI/(4018589745) |
| Client/UI/Shop/ | 4018589756 | UI/(4018589745) |
| Client/UI/SignIn/ | 4018589762 | UI/(4018589745) |
| Client/UI/IllustratedGuide/ | 4018589766 | UI/(4018589745) |
| Client/UI/Turntable/ | 4018589767 | UI/(4018589745) |
| Client/UI/Skin/ | 4018589771 | UI/(4018589745) |
| Client/UI/SkillButton/ | 4018589774 | UI/(4018589745) |

### DS/ 文件夹结构

| 文件夹名 | docid | 父级 |
|---------|-------|------|
| DS/ | 4018590565 | API参考手册(4018569206) |
| DS/Config/ | 4018590566 | DS/(4018590565) |
| DS/Handler/ | 4018590568 | DS/(4018590565) |
| DS/Subsystem/ | 4018590570 | DS/(4018590565) |
| DS/Shop/ | 4018590573 | DS/(4018590565) |
| DS/Draw/ | 4018590575 | DS/(4018590565) |
| DS/SignIn/ | 4018590579 | DS/(4018590565) |
| DS/IllustratedGuide/ | 4018590582 | DS/(4018590565) |
| DS/SimulateServer/ | 4018590585 | DS/(4018590565) |
| DS/Utils/ | 4018590586 | DS/(4018590565) |

### Common/ 文件夹结构

| 文件夹名 | docid | 父级 |
|---------|-------|------|
| Common/ | 4018591021 | API参考手册(4018569206) |
| Common/UICanvas/ | 4018591022 | Common/(4018591021) |
| Common/UICanvas/Action/ | 4018591024 | UICanvas/(4018591022) |

### Dev/Config/ 文件夹

| 文件夹名 | docid | 父级 |
|---------|-------|------|
| Dev/Config/ | 4018590990 | Dev/(4018569491) |
