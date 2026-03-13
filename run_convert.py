#!/usr/bin/env python3
"""一次性转换脚本：将 UGC 平台 API 输出分层需求文档.md 转为 Excel.

使用方法：
    cd g:\\tianyishao\\Moos-share
    python run_convert.py

运行后在同目录生成 UGC平台API输出分层需求文档.xlsx，完成后可删除本脚本。
"""

import sys
from pathlib import Path

# 加载已有的转换脚本
script_dir = Path(__file__).parent / ".codebuddy" / "skills" / "md-to-excel" / "scripts"
sys.path.insert(0, str(script_dir))

from md_to_excel import write_structured_to_excel, parse_md_tables, parse_md_structure

# 源文件和目标文件
src = Path(__file__).parent / "UGC平台API输出分层需求文档.md"
dst = src.with_suffix(".xlsx")

if not src.exists():
    print(f"❌ 源文件不存在: {src}")
    sys.exit(1)

content = src.read_text(encoding="utf-8")

# 使用 document 模式（全文档结构化写入单 Sheet）
result = write_structured_to_excel(content, str(dst), mode="document")

# 统计信息
tables = parse_md_tables(content)
blocks = parse_md_structure(content)
print(f"✅ 转换完成！")
print(f"📄 源文件: {src.name}")
print(f"📊 输出文件: {result}")
print(f"📋 模式: document（全文档结构化）")
print(f"📊 内容统计:")
print(f"   标题: {sum(1 for b in blocks if b['type'] == 'heading')} 个")
print(f"   段落: {sum(1 for b in blocks if b['type'] == 'paragraph')} 个")
print(f"   表格: {len(tables)} 个")
print(f"   列表: {sum(1 for b in blocks if b['type'] == 'list')} 个")
print(f"   代码块: {sum(1 for b in blocks if b['type'] == 'code')} 个")
print(f"\n🗑️  转换完成后可以删除本脚本: del run_convert.py")
