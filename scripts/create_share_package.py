#!/usr/bin/env python3
"""创建可分享的代码包，移除敏感信息."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def create_share_package():
    """创建分享包."""
    project_root = Path(__file__).parent.parent
    share_dir = project_root.parent / "Moos-share"

    print(f"创建分享包: {share_dir}")

    # 如果已存在，先删除
    if share_dir.exists():
        print("  删除旧目录...")
        shutil.rmtree(share_dir)

    # 创建目录结构
    share_dir.mkdir(exist_ok=True)

    # 1. 复制源代码
    print("  复制源代码...")
    src_dir = project_root / "src"
    if src_dir.exists():
        shutil.copytree(src_dir, share_dir / "src")

    # 2. 复制脚本
    print("  复制脚本...")
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        shutil.copytree(scripts_dir, share_dir / "scripts")

    # 3. 复制文档示例（不包含个人数据）
    print("  复制文档...")
    docs_dir = project_root / "data" / "docs"
    if docs_dir.exists():
        (share_dir / "data" / "docs").mkdir(parents=True, exist_ok=True)
        for doc in docs_dir.glob("*.md"):
            if "setup" not in doc.name.lower():  # 跳过包含配置的文档
                shutil.copy2(doc, share_dir / "data" / "docs" / doc.name)

    # 4. 创建空的示例数据目录
    print("  创建示例数据目录...")
    (share_dir / "data" / "raw" / "generated" / "work").mkdir(parents=True, exist_ok=True)
    (share_dir / "data" / "raw" / "generated" / "dev").mkdir(parents=True, exist_ok=True)
    (share_dir / "data" / "context" / "__created").mkdir(parents=True, exist_ok=True)
    (share_dir / "data" / "context" / "__collected").mkdir(parents=True, exist_ok=True)

    # 添加 .gitkeep
    for d in [
        share_dir / "data" / "raw" / "generated" / "work",
        share_dir / "data" / "raw" / "generated" / "dev",
        share_dir / "data" / "context" / "__created",
        share_dir / "data" / "context" / "__collected",
    ]:
        (d / ".gitkeep").touch()

    # 5. 复制配置模板（安全版本）
    print("  复制配置模板...")
    config_example = project_root / "config.example.yaml"
    if config_example.exists():
        shutil.copy2(config_example, share_dir / "config.example.yaml")

    # 创建 config.yaml（安全版本，去掉真实值）
    safe_config = """# Personal Assistant 配置
# 复制此文件为 config.yaml 并填入实际值

# 飞书 API 配置（可选）
# 如需同步飞书多维表格，请在 https://open.feishu.cn/app 创建应用获取
feishu:
  app_id: "cli_xxxxxxxxxxxx"
  app_secret: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  bases:
    - name: "个人笔记"
      app_token: "xxxxxxxxxxxxxx"
      table_id: "tblxxxxxxxx"
      default_topic: "reflection"
      fields:
        title: "标题"
        content: "内容"
        tags: "标签"
        created_time: "创建时间"

# Context 主题配置
context:
  core_topics:
    personal:
      name: "个人信息"
      description: "个人身份、联系方式等相关信息"
      keywords: ["个人资料", "联系方式", "地址", "身份证", "姓名", "电话"]

    writing:
      name: "写作爱好"
      description: "写作相关的内容和想法"
      keywords: ["文章", "写作", "灵感", "读书笔记", "随笔", "创作"]

    tasks:
      name: "任务管理"
      description: "任务和日程安排"
      keywords: ["待办", "任务", "TODO", "截止日期", "计划", "安排"]

    preferences:
      name: "个人偏好"
      description: "个人喜好和设置"
      keywords: ["喜欢", "偏好", "设置", "习惯", "推荐", "收藏"]

    reflection:
      name: "日记反思"
      description: "每日情绪记录、反思和自我觉察"
      keywords: ["情绪", "反思", "心情", "感受", "日记", "期许", "事件"]

    product:
      name: "产品思考"
      description: "产品经理相关工作、思考和笔记"
      keywords: ["产品经理", "产品感", "商业模式", "用户观察", "增长", "UI", "UX"]

    work:
      name: "工作记录"
      description: "工作日记、复盘、经验"
      keywords: ["工作日记", "复盘", "团队管理", "面试", "招聘"]

    reading:
      name: "阅读学习"
      description: "读书笔记、待读清单、知识整理"
      keywords: ["阅读", "读书笔记", "知识体系", "思维模型"]

    ideas:
      name: "灵感想法"
      description: "灵光一闪、创意点子"
      keywords: ["灵光一闪", "想法", "创意", "金句"]

    ai:
      name: "AI 相关"
      description: "AI 产品、技术、思考"
      keywords: ["AI", "大模型", "ChatGPT", "Claude", "prompt", "人工智能"]

  custom_topics: {}

# 数据路由配置
routing:
  strategy: "keyword_match"
  threshold: 0.15
  allow_multi_topic: true

# 同步配置
sync:
  raw_dir: "data/raw"
  context_dir: "data/context"
  keep_history: false
"""
    (share_dir / "config.yaml").write_text(safe_config, encoding="utf-8")

    # 6. 复制项目文件
    print("  复制项目文件...")
    files_to_copy = [
        ("pyproject.toml", None),
        ("README.md", None),
        ("article_content.md", None),
        (".gitignore", None),
    ]

    for src_name, dest_name in files_to_copy:
        src_file = project_root / src_name
        if src_file.exists():
            dest = share_dir / (dest_name or src_name)
            shutil.copy2(src_file, dest)

    # 6.5 复制 skills（排除 .env 文件）
    print("  复制 skills（排除 .env）...")
    skills_dir = project_root / "skills"
    if skills_dir.exists():
        for skill in skills_dir.iterdir():
            if skill.is_dir():
                dest_skill = share_dir / "skills" / skill.name
                shutil.copytree(skill, dest_skill, ignore=shutil.ignore_patterns(".env", "*.pyc", "__pycache__", "node_modules"))

    # 7. 创建分享说明
    print("  创建分享说明...")
    readme_share = """# Personal Assistant - 可分享版本

这是个人知识中枢系统的可分享版本，**已移除所有敏感信息**。

## 快速开始

1. **安装依赖**
   ```bash
   pip install -e .
   ```

2. **配置飞书同步（可选）**
   - 在 [飞书开放平台](https://open.feishu.cn/app) 创建应用
   - 获取 `app_id` 和 `app_secret`
   - 复制 `config.example.yaml` 为 `config.yaml`
   - 填入你的配置

3. **使用 MCP 功能**
   在 Claude Code / CodeBuddy 中配置 MCP：
   ```json
   {
     "mcpServers": {
       "personal-assistant": {
         "command": "python",
         "args": ["-m", "pa.mcp_server"]
       }
     }
   }
   ```

## 核心功能

- **网页内容收集**: `collect_content` - 自动提取正文并保存
- **知识库查询**: `query_context` - 检索已保存的知识
- **主题管理**: `manage_topic` - 自定义知识分类

## 文件说明

| 目录 | 说明 |
|------|------|
| `src/pa/` | 核心源代码 |
| `src/pa/extractors/` | 网页内容提取器 |
| `src/pa/formatters/` | Obsidian 格式化 |
| `src/pa/router/` | 内容路由引擎 |
| `data/context/` | 知识库存放位置 |
| `data/raw/` | 原始数据存储 |

## 注意事项

- `config.yaml` 中的配置已被脱敏，需要填入你自己的值
- 个人笔记数据未包含在此分享包中
- 如需同步飞书数据，需要自行配置 API 凭证

## 了解更多

参考文章：《我与AI共建了一套个人知识操作系统》
"""
    (share_dir / "README-SHARE.md").write_text(readme_share, encoding="utf-8")

    # 8. 创建空的 .gitignore
    gitignore_content = """# 环境配置（包含敏感信息）
.env
.env.local
.env.*.local
config.local.yaml

# 日志文件
*.log
logs/

# Python 缓存
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp

# 系统文件
.DS_Store
Thumbs.db
"""
    (share_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

    # 9. 清理脚本中的测试文件（如果有敏感信息）
    print("  检查并清理脚本...")
    test_extractor = share_dir / "scripts" / "test_extractor.py"
    if test_extractor.exists():
        # 检查是否包含真实 URL
        content = test_extractor.read_text(encoding="utf-8")
        if "weixin" in content or "zhihu" in content or "http" in content:
            # 替换为示例 URL
            safe_content = '''#!/usr/bin/env python3
"""测试内容提取器 - 示例脚本."""

from pa.extractors.web import WebContentExtractor

# 示例：替换为你要测试的 URL
url = "https://example.com/article"

extractor = WebContentExtractor()
result = extractor.extract(url)

print(f"标题: {result.title}")
print(f"作者: {result.author}")
print(f"内容长度: {len(result.content)} 字符")
'''
            test_extractor.write_text(safe_content, encoding="utf-8")

    print(f"\n[OK] 分享包创建完成: {share_dir}")
    print("\n[包含内容]")
    print("  - 完整源代码 (src/)")
    print("  - Skills (skills/)")
    print("  - 配置模板 (config.example.yaml)")
    print("  - 脱敏配置 (config.yaml)")
    print("  - 项目说明 (README-SHARE.md)")
    print("  - 依赖配置 (pyproject.toml)")
    print("\n[已排除]")
    print("  - 个人笔记数据 (data/raw/)")
    print("  - 真实 API 凭证 (config.yaml, .env)")
    print("  - 日志文件")
    print("  - 缓存文件 (__pycache__, node_modules)")

    return share_dir


if __name__ == "__main__":
    share_path = create_share_package()
    print(f"\n[TIP] 提示: 你可以将 {share_path} 压缩后分享给他人")
