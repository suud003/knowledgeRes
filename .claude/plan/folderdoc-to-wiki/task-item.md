# 实施计划

> **总体说明**：本 Skill 负责将 `raw data/type_record/` 下 6 个 FolderDoc md 文件（00、02、03a、03b、04、05）改写并映射到 iWiki 的"5.1 偷走脑腐"文档树中。每个任务对应处理一个 FolderDoc，按依赖顺序排列（先创建父级文件夹，再创建子文档）。

---

- [x] 1. 编写 SKILL.md 主文件和 references 参考资料
  - 在 `.codebuddy/skills/folderdoc-to-wiki/` 下创建 `SKILL.md`，定义 Skill 的触发条件、执行流程、改写规则
  - 在 `references/` 下创建 `wiki_mapping.md`，记录所有 WIKI ID 常量和文件夹/文档映射关系
  - 在 `references/` 下创建 `rewrite_style_guide.md`，记录改写风格规范（基于 FolderDoc_01 → API参考手册的已有范例）
  - 在 `references/` 下创建 `sample_rewrite.md`，从已整理好的 API参考手册/Config/ 子文档中提取 2-3 个典型改写前后对照样板（配置文件、Actor 类、Feature 类）
  - _需求：3.1、5.1、5.2、7.1_

- [x] 2. 处理 FolderDoc_00：整合到"快速开始"文档
  - 读取 FolderDoc_00_Game_Overview.md（431行/16.91KB），包含 7 个章节：游戏简介、完整游玩流程、核心系统详解、技术架构、模块关系、关键决策、项目规模
  - 读取已有"快速开始"文档（ID: 4018569234）的当前内容
  - 按改写规则合并到"快速开始"文档中（保留已有结构，以追加/合并方式整合新增内容）
  - 使用 `saveDocument(docid=4018569234)` 更新文档
  - _需求：2.1、3.2、4.3_

- [x] 3. 处理 FolderDoc_02：创建 GamePlay/ 下的子文件夹和文档
  - [ ] 3.1 在 GamePlay/(4018569259) 下创建 8 个子文件夹：Core/、Actor/、Feature/、SubSystem/、Skill/、Backpack/、Component/、Utils/
    - 使用 `createDocument(contenttype="FOLDER")` 创建每个文件夹，记录 docid
    - _需求：2.2、4.1、5.2_
  - [ ] 3.2 Core/ 下创建 6 个子文档
    - PlanBTGameMode.lua（207行）、PlanBTGameState.lua（78行）、PlanBTPlayerController.lua（326行）、PlanBTPlayerCharacter.lua（651行）、PlanBTPlayerState.lua（54行）、PlanBTNewFakeAIController.lua（174行）
    - 改写规则：`# 职责` → `# Feature 注入`(如有) → `# RPC 方法`(如有) → `# 值复制属性`(如有) → `# 核心函数`（表格） → `# 关键流程`(如有)
    - _需求：2.2、3.1、4.2_
  - [ ] 3.3 Actor/ 下创建 13 个子文档
    - MonsterBaseActor.lua（2220行★超大）、MonsterActor.lua（1788行★超大）、MonsterFactoryActor.lua（954行★大）、MonsterRecycleBinActor.lua（94行）、MonsterCountdownBillboardActor.lua（383行）、CoinActor.lua（444行）、DoorActor.lua（263行）、DrawActor.lua（133行）、ShopActor.lua（165行）、PartnerGhost.lua（315行）、Trap.lua（437行）、TrapCheckArea.lua（37行）、PistalTaser.lua（104行）
    - 超大文件重点保留：核心数据结构、网络同步属性表、函数分类总览，移除逐行解读
    - _需求：2.2、3.1、3.3_
  - [ ] 3.4 Feature/ 下创建 8 个子文档
    - MonsterInteractionFeature.lua（1192行★超大）、CoinFeature.lua（501行）、PlayerRebirthFeature.lua（279行）、MonsterWarehouseFeature.lua（457行）、SkinFeature.lua（280行）、ActiveFeature.lua（58行）、NewbieGuideFeature.lua（317行）、PlayerPartnerGhostFeature.lua（177行）
    - 改写规则：`# 职责` → `# 挂载对象` → `# RPC 方法`(表格) → `# 核心函数`(表格) → `# 关键流程`(如有)
    - _需求：2.2、3.1_
  - [ ] 3.5 SubSystem/ 下创建 2 个子文档
    - MonsterBaseSubsystem.lua（1046行★大）、PlanBTMainSubsystem.lua（32行）
    - MonsterBaseSubsystem 保留 38 函数分类表和玩家首次加入流程
    - _需求：2.2、3.1、3.3_
  - [ ] 3.6 Skill/ 下创建 7 个子文档
    - SkillConfig.lua（63行）、SkillAction_ChangeTrapState.lua（30行）、SkillAction_TakeTrap.lua（52行）、SkillCondition_TrapCheckArea.lua（28行）、Skill_Template_RecoverEnergy_4300950.lua（67行）、Skill_Melee_Pan_4300951.lua（403行）、Skill_Trap_4300952.lua（15行）
    - _需求：2.2、3.1_
  - [ ] 3.7 Backpack/(1个)、Component/(1个)、Utils/(3个) 共创建 5 个子文档
    - Backpack/MeleeWeaponItemHandle.lua（25行）、Component/BackpackComponent.lua（80行）、Utils/MiscUtils.lua（105行）、Utils/SpawnUtils.lua（65行）、Utils/ShopUtils.lua（16行）
    - _需求：2.2、3.1_

- [x] 4. 处理 FolderDoc_03a：创建 Client/ 文件夹和基础层文档
  - [ ] 4.1 在 API参考手册(4018569206) 下创建 Client/ 文件夹，然后在 Client/ 下创建子文件夹：Config/、Handler/、SubSystem/、Shop/、Draw/、SignIn/、IllustratedGuide/、Result/、InGameUI/、ShootingUI/（共10个子文件夹）
    - _需求：2.3、4.1、5.2_
  - [ ] 4.2 Client/ 根级创建 1 个子文档：ClientLogicEntry.lua（34行）
    - _需求：2.3、3.1_
  - [ ] 4.3 Client/Config/ 下创建 4 个子文档
    - UIConfig.lua（259行）、NewbieGuideConfig.lua（177行）、ScreenMarkConfig.lua（36行）、TeamPanelUIConfig.lua（9行）
    - _需求：2.3、3.1_
  - [ ] 4.4 Client/Handler/ 下创建 5 个子文档
    - PlanBT_PlanBTShop_Client_Handler.lua（139行）、PlanBT_PlanBTDraw_Client_Handler.lua（81行）、PlanBT_PlanBTSignIn_Client_Handler.lua（53行）、PlanBT_PlanBTIllustratedGuide_Client_Handler.lua（62行）、PlanBT_PlanBTPlayerData_Client_Handler.lua（38行）
    - _需求：2.3、3.1_
  - [ ] 4.5 Client/SubSystem/ 下创建 1 个子文档：PlanBTMonsterBaseSubSystemClient.lua（64行）
    - _需求：2.3、3.1_
  - [ ] 4.6 Client 子系统文件夹下各创建 1 个子文档（共 5 个）
    - Shop/PlanBTShopSubsystem_Client.lua（492行）、Draw/PlanBTDrawSubSystem_Client.lua（245行）、SignIn/PlanBTSignInSubsystem_Client.lua（235行）、IllustratedGuide/PlanBTIllustratedGuideSubsystem_Client.lua（370行）、Result/PlanBTResultSubsystem.lua（46行）
    - _需求：2.3、3.1_
  - [ ] 4.7 Client/InGameUI/ 下创建 2 个子文档、ShootingUI/ 下创建 1 个子文档
    - InGameUI/FightingStateStateMachine.lua（36行）、InGameUI/PlayMonsterState.lua（59行）、ShootingUI/ShootingUIPanelMain.lua（26行）
    - _需求：2.3、3.1_

- [x] 5. 处理 FolderDoc_03b：创建 Client/UI/ 文件夹和 UI 文档
  - [ ] 5.1 在 Client/ 下创建 UI/ 文件夹，然后在 UI/ 下创建子文件夹：Item/、Shop/、SignIn/、IllustratedGuide/、Turntable/、Skin/、SkillButton/（共7个子文件夹）
    - _需求：2.4、4.1_
  - [ ] 5.2 UI/ 根级创建 7 个子文档
    - PlanBT_Layout_UIBP.lua（370行）、PlanBTMainUI.lua（48行）、PlayerRebirthUI.lua（413行）、FaceIntroUI.lua（73行）、PlanBT_BeginnerGuide_UIBP.lua（105行）、PlanBT_Ranking_Popup_UIBP.lua（74行）、OfflineEarningsPopup.lua（51行）
    - _需求：2.4、3.1_
  - [ ] 5.3 UI/Item/ 下创建 1 个子文档：PlanBT_Ranking_Item_UIBP.lua（74行）
    - _需求：2.4、3.1_
  - [ ] 5.4 UI/Shop/ 下创建 5 个子文档
    - PlanBT_Shop_Prop_UIBP.lua（173行）、PlanBT_Prop_Item_UIBP.lua（122行）、PlanBT_Giftpack_Item_UIBP.lua（170行）、PlanBT_PurchaseGoods_Details_Item_UIBP.lua（137行）、PlanBT_PurchaseGoods_Icon_Item_UIBP.lua
    - _需求：2.4、3.1_
  - [ ] 5.5 UI/SignIn/ 下创建 3 个子文档
    - PlanBT_SignIn_UIBP.lua（138行）、PlanBT_SignIn_GetReward_UIBP.lua（70行）、PlanBT_SignIn_Item_UIBP.lua（127行）
    - _需求：2.4、3.1_
  - [ ] 5.6 UI/IllustratedGuide/ 下创建 3 个子文档
    - PlanBT_IllustratedGuide_UIBP.lua（171行）、PlanBT_IllustratedGuide_Popup_UIBP.lua（188行）、PlanBT_IllustratedGuide_Item_UIBP.lua（88行）
    - _需求：2.4、3.1_
  - [ ] 5.7 UI/Turntable/ 下创建 7 个子文档
    - PlanBT_Turntable_UIBP.lua（257行）、PlanBT_Turntable_DrawOne_UIBP.lua（77行）、PlanBT_Turntable_DrawTen_UIBP.lua（106行）、PlanBT_Turntable_Item_UIBP.lua（33行）、PlanBT_Lua_Item_UIBP.lua（85行）、PlanBT_Lua_DrawTen_Item.lua（29行）、PlanBT_Probability_Item_UIBP.lua（30行）
    - _需求：2.4、3.1_
  - [ ] 5.8 UI/Skin/(1个) + UI/SkillButton/(1个) 共创建 2 个子文档
    - SkinUI.lua（145行）、TrapSkillButtonUI.lua（68行）
    - _需求：2.4、3.1_

- [ ] 6. 处理 FolderDoc_04：创建 DS/ 文件夹和服务器端文档
  - [ ] 6.1 在 API参考手册(4018569206) 下创建 DS/ 文件夹，然后在 DS/ 下创建子文件夹：Config/、Handler/、Subsystem/、Shop/、Draw/、SignIn/、IllustratedGuide/、SimulateServer/、Utils/（共9个子文件夹）
    - _需求：2.5、4.1_
  - [ ] 6.2 DS/ 根级创建 3 个子文档
    - DSLogicEntry.lua（29行）、PlanBTGameSettlementModule.lua（15行）、PlanBTSyncProcessModule.lua（74行，含真人优先准入机制 mermaid 图）
    - _需求：2.5、3.1、3.4_
  - [ ] 6.3 DS/Config/ 下创建 2 个子文档
    - AIAccountConfig.lua（91行，3个难度档位配置表）、AIProcessModConfig.lua（63行，AI行为配置）
    - _需求：2.5、3.1_
  - [ ] 6.4 DS/Handler/ 下创建 5 个子文档
    - PlanBT_PlanBTShop_DS_Handler.lua（173行，13个协议函数）、PlanBT_PlanBTDraw_DS_Handler.lua、PlanBT_PlanBTSignIn_DS_Handler.lua、PlanBT_PlanBTIllustratedGuide_DS_Handler.lua、PlanBT_PlanBTPlayerData_DS_Handler.lua
    - _需求：2.5、3.1_
  - [ ] 6.5 DS/Subsystem/ 下创建 3 个子文档
    - DSActiveSubsystem.lua（289行，3个定时器+三级销毁状态机 mermaid 图）、MLAIPopulationSubSystem.lua（~893行，AI 填充/退出/行为调度）、PlanBTCommerceSubsystem_DS.lua（73行，商业化协议网关+本地/线上双模式切换）
    - _需求：2.5、3.1、3.4_
  - [ ] 6.6 DS 业务子系统文件夹下各创建 1 个子文档（共 5 个）
    - Shop/PlanBTShopSubsystem_DS.lua（603行，购买验证链流程）、Draw/PlanBTDrawSubSystem_DS.lua（356行）、SignIn/PlanBTSignInSubsystem_DS.lua（216行）、IllustratedGuide/PlanBTIllustratedGuideSubsystem_DS.lua（301行）、SimulateServer/PlanBT_Simulate_LobbyServer.lua（425行，10种模拟协议）
    - _需求：2.5、3.1_
  - [ ] 6.7 DS/Utils/ 下创建 3 个子文档
    - PlanBTShopUtils.lua（828行★大，购买校验+通知函数表）、PlanBTShopItemUtils.lua（~725行，物品类型分发流程）、PlanBTCurrencyUtils.lua（670行★大，同步队列机制 mermaid 图+7类函数分类总览）
    - _需求：2.5、3.1、3.4_

- [ ] 7. 处理 FolderDoc_05：更新 Dev/ 并创建 Common/ 文件夹
  - [ ] 7.1 在已有 Dev/(4018569491) 下创建 Config/ 子文件夹，然后创建 3 个子文档
    - GMCheatManager.lua（1491行★超大，DS端GM命令执行）、GMConfig.lua（175行，24个GM按钮配置）、GMFuncConfig.lua（951行★大，Client端GM面板实现）
    - 保留 mermaid 调用流程图
    - _需求：2.6、3.1、3.4_
  - [ ] 7.2 在 API参考手册(4018569206) 下创建 Common/ 文件夹和 UICanvas/Action/ 子文件夹（共2层），然后创建 5 个子文档
    - CanvasAction_CameraMode.lua（44行）、CanvasAction_CustomTags.lua（50行）、CanvasAction_EnterCameraDevice.lua（37行）、CanvasAction_EnterPet.lua（37行）、CanvasAction_EnterTransformation.lua（38行）
    - _需求：2.6、3.1_

- [ ] 8. 更新 wiki_mapping.md 映射配置文件
  - 在所有文档创建完成后，将每个新建文件夹和文档的 docid 更新到 `references/wiki_mapping.md` 中
  - 记录完整的 WIKI 文档树结构（文件夹名 → docid → 子文档列表）
  - _需求：7.1、7.2_

---

## 文档创建量统计

| FolderDoc | 文件夹数 | 文档数 | 合计操作 |
|-----------|---------|--------|---------|
| 00（快速开始） | 0 | 1（更新） | 1 |
| 02（Gameplay） | 8 | 41 | 49 |
| 03a（Client基础） | 11 | 19 | 30 |
| 03b（Client UI） | 7 | 28 | 35 |
| 04（DS） | 9 | 21 | 30 |
| 05（Dev+Common） | 3 | 8 | 11 |
| **总计** | **38** | **118** | **156** |

> 每个文档创建需 2 次 MCP 调用（createDocument + saveDocument），文件夹创建需 1 次。总计约 **274 次 MCP 调用**。建议按 FolderDoc 分批执行，每次处理一个 FolderDoc。
