#!/usr/bin/env python3
"""一键转换脚本：将 UGC平台API输出分层需求文档.md 转换为 Excel 文件.

用法: 在 g:\tianyishao\Moos-share 目录下运行:
    python convert_ugc_doc.py
"""

import sys
from pathlib import Path

# 添加 md_to_excel 脚本路径
SKILL_DIR = Path(__file__).parent / ".codebuddy" / "skills" / "md-to-excel" / "scripts"
sys.path.insert(0, str(SKILL_DIR))

from md_to_excel import write_structured_to_excel

def main():
    base_dir = Path(__file__).parent
    md_path = base_dir / "UGC平台API输出分层需求文档.md"
    output_path = base_dir / "UGC平台API输出分层需求文档.xlsx"

    if not md_path.exists():
        print(f"❌ 找不到源文件: {md_path}")
        sys.exit(1)

    print(f"📄 源文件: {md_path}")
    print(f"📊 输出文件: {output_path}")
    print(f"📋 模式: document (全文档结构化)")
    print()

    md_content = md_path.read_text(encoding="utf-8")
    result = write_structured_to_excel(md_content, str(output_path), mode="document")

    print(f"✅ Markdown → Excel 转换完成!")
    print(f"📂 文件已保存到: {result}")

if __name__ == "__main__":
    main()
