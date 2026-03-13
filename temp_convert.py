import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"g:\tianyishao\Moos-share\.codebuddy\skills\md-to-excel\scripts")))
from md_to_excel import write_structured_to_excel

md_path = Path(r"g:\tianyishao\Moos-share\UGC平台API输出分层需求文档.md")
output_path = Path(r"g:\tianyishao\Moos-share\UGC平台API输出分层需求文档.xlsx")

md_content = md_path.read_text(encoding="utf-8")
result = write_structured_to_excel(md_content, str(output_path), mode="document")
print(f"Done: {result}")
