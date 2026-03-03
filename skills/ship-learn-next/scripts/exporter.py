"""Ship-Learn-Next 计划导出器 - 与 huashu-slides 联动."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class PlanExporter:
    """将 Ship-Learn-Next 计划导出为 PPT."""

    def __init__(
        self,
        plans_dir: Path | None = None,
        huashu_slides_dir: Path | None = None,
    ):
        """初始化导出器.
        
        Args:
            plans_dir: 计划文件目录
            huashu_slides_dir: huashu-slides Skill 目录
        """
        if plans_dir is None:
            skills_dir = Path(__file__).parent.parent
            plans_dir = skills_dir / "plans"
        self.plans_dir = plans_dir
        
        if huashu_slides_dir is None:
            # 默认与 ship-learn-next 同级
            self.huashu_slides_dir = plans_dir.parent.parent / "huashu-slides"
        else:
            self.huashu_slides_dir = Path(huashu_slides_dir)

    def export_to_ppt(
        self,
        plan_id: str,
        style: str = "snoopy",
        output_name: str | None = None,
    ) -> dict[str, Any]:
        """将计划导出为 PPT.
        
        Args:
            plan_id: 计划ID
            style: 视觉风格（参考 huashu-slides 风格）
            output_name: 输出文件名（可选）
            
        Returns:
            导出结果
        """
        # 读取计划内容
        plan_data = self._read_plan(plan_id)
        if "error" in plan_data:
            return plan_data
        
        # 生成 HTML slides
        html_files = self._generate_html_slides(plan_data, style)
        if not html_files:
            return {"error": "生成 HTML slides 失败"}
        
        # 调用 huashu-slides 转换为 PPTX
        output_file = self._convert_to_pptx(html_files, output_name or plan_id)
        
        if output_file and Path(output_file).exists():
            return {
                "success": True,
                "plan_id": plan_id,
                "output_file": output_file,
                "slide_count": len(html_files),
                "style": style,
            }
        else:
            return {"error": "PPT 导出失败"}

    def _read_plan(self, plan_id: str) -> dict[str, Any]:
        """读取计划文件."""
        # 查找计划文件
        plan_file = None
        
        # 直接匹配
        candidate = self.plans_dir / f"{plan_id}.md"
        if candidate.exists():
            plan_file = candidate
        
        # 尝试添加 Plan- 前缀
        if not plan_file and not plan_id.startswith("Plan-"):
            candidate = self.plans_dir / f"Plan-{plan_id}.md"
            if candidate.exists():
                plan_file = candidate
        
        # 部分匹配
        if not plan_file:
            for file in self.plans_dir.glob("*.md"):
                if plan_id in file.stem:
                    plan_file = file
                    break
        
        if not plan_file:
            return {"error": f"未找到计划: {plan_id}"}
        
        # 读取内容
        content = plan_file.read_text(encoding="utf-8")
        
        # 解析计划信息
        return self._parse_plan_content(content, plan_file)

    def _parse_plan_content(self, content: str, file: Path) -> dict[str, Any]:
        """解析计划内容."""
        data = {
            "file": str(file),
            "filename": file.stem,
            "content": content,
        }
        
        # 提取计划名称
        title_match = re.search(r"# Ship-Learn-Next Plan - (.+)", content)
        data["name"] = title_match.group(1) if title_match else "未命名计划"
        
        # 提取创建日期
        date_match = re.search(r"创建日期[:：]\s*(.+)", content)
        data["created_date"] = date_match.group(1).strip() if date_match else ""
        
        # 提取学习目标
        goal_match = re.search(r"学习目标\n+(.+?)(?=\n##|\n###|$)", content, re.DOTALL)
        data["learning_goal"] = goal_match.group(1).strip() if goal_match else ""
        
        # 提取知识摘要
        summary_match = re.search(r"知识来源摘要\n+(.+?)(?=\n##|\n###|$)", content, re.DOTALL)
        data["knowledge_summary"] = summary_match.group(1).strip() if summary_match else ""
        
        # 提取所有周计划
        weeks = []
        for week_match in re.finditer(r"### Week (\d+): (.+?)\n(.+?)(?=### Week|\n## 🎯|$)", content, re.DOTALL):
            week_num = int(week_match.group(1))
            week_theme = week_match.group(2)
            week_content = week_match.group(3)
            
            # 提取 SHIP 任务
            ship_match = re.search(r"SHIP \(交付\)\n+(.+?)(?=\n####|\n###|\n##|$)", week_content, re.DOTALL)
            ship_task = ship_match.group(1).strip() if ship_match else ""
            
            # 提取 NEXT 方向
            next_match = re.search(r"NEXT \(迭代\)\n+(.+?)(?=\n####|\n###|\n##|$)", week_content, re.DOTALL)
            next_focus = next_match.group(1).strip() if next_match else ""
            
            weeks.append({
                "number": week_num,
                "theme": week_theme,
                "ship_task": ship_task,
                "next_focus": next_focus,
            })
        
        data["weeks"] = weeks
        data["total_weeks"] = len(weeks)
        
        return data

    def _generate_html_slides(self, plan_data: dict, style: str) -> list[Path]:
        """生成 HTML 幻灯片."""
        slides_dir = self.plans_dir / "slides" / plan_data["filename"]
        slides_dir.mkdir(parents=True, exist_ok=True)
        
        html_files = []
        
        # Slide 1: 封面
        cover_html = self._generate_cover_slide(plan_data, style)
        cover_file = slides_dir / "slide-01-cover.html"
        cover_file.write_text(cover_html, encoding="utf-8")
        html_files.append(cover_file)
        
        # Slide 2: 学习目标
        goal_html = self._generate_goal_slide(plan_data, style)
        goal_file = slides_dir / "slide-02-goal.html"
        goal_file.write_text(goal_html, encoding="utf-8")
        html_files.append(goal_file)
        
        # Slide 3: 知识摘要
        summary_html = self._generate_summary_slide(plan_data, style)
        summary_file = slides_dir / "slide-03-summary.html"
        summary_file.write_text(summary_html, encoding="utf-8")
        html_files.append(summary_file)
        
        # Slides 4+: 每周计划
        for i, week in enumerate(plan_data["weeks"], start=4):
            week_html = self._generate_week_slide(plan_data, week, style, i)
            week_file = slides_dir / f"slide-{i:02d}-week{week['number']}.html"
            week_file.write_text(week_html, encoding="utf-8")
            html_files.append(week_file)
        
        # 最后一页：总结
        final_num = len(html_files) + 1
        final_html = self._generate_final_slide(plan_data, style)
        final_file = slides_dir / f"slide-{final_num:02d}-final.html"
        final_file.write_text(final_html, encoding="utf-8")
        html_files.append(final_file)
        
        return html_files

    def _generate_cover_slide(self, plan_data: dict, style: str) -> str:
        """生成封面幻灯片."""
        # 简化版 HTML 模板
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{plan_data['name']}</title>
    <style>
        body {{ margin: 0; padding: 40px; font-family: 'Segoe UI', sans-serif; }}
        .slide {{ width: 1280px; height: 720px; display: flex; flex-direction: column; justify-content: center; align-items: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        h1 {{ font-size: 56px; margin-bottom: 20px; text-align: center; }}
        .subtitle {{ font-size: 28px; opacity: 0.9; }}
        .meta {{ font-size: 20px; margin-top: 40px; opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="slide">
        <h1>🚀 {plan_data['name']}</h1>
        <div class="subtitle">Ship-Learn-Next 实践计划</div>
        <div class="meta">{plan_data.get('created_date', '')}</div>
    </div>
</body>
</html>"""

    def _generate_goal_slide(self, plan_data: dict, style: str) -> str:
        """生成目标幻灯片."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>学习目标</title>
    <style>
        body {{ margin: 0; padding: 40px; font-family: 'Segoe UI', sans-serif; }}
        .slide {{ width: 1280px; height: 720px; padding: 60px; background: #f8f9fa; box-sizing: border-box; }}
        h2 {{ font-size: 42px; color: #333; margin-bottom: 40px; }}
        .content {{ font-size: 28px; line-height: 1.8; color: #555; }}
    </style>
</head>
<body>
    <div class="slide">
        <h2>🎯 学习目标</h2>
        <div class="content">{plan_data.get('learning_goal', '将知识转化为实践能力')}</div>
    </div>
</body>
</html>"""

    def _generate_summary_slide(self, plan_data: dict, style: str) -> str:
        """生成知识摘要幻灯片."""
        summary = plan_data.get('knowledge_summary', '')[:300]
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>知识来源</title>
    <style>
        body {{ margin: 0; padding: 40px; font-family: 'Segoe UI', sans-serif; }}
        .slide {{ width: 1280px; height: 720px; padding: 60px; background: #fff; box-sizing: border-box; }}
        h2 {{ font-size: 42px; color: #333; margin-bottom: 40px; }}
        .content {{ font-size: 24px; line-height: 1.8; color: #555; }}
    </style>
</head>
<body>
    <div class="slide">
        <h2>📚 知识来源</h2>
        <div class="content">{summary}...</div>
    </div>
</body>
</html>"""

    def _generate_week_slide(self, plan_data: dict, week: dict, style: str, num: int) -> str:
        """生成周计划幻灯片."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Week {week['number']}</title>
    <style>
        body {{ margin: 0; padding: 40px; font-family: 'Segoe UI', sans-serif; }}
        .slide {{ width: 1280px; height: 720px; padding: 60px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); box-sizing: border-box; }}
        h2 {{ font-size: 42px; color: #333; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 24px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .section-content {{ font-size: 22px; color: #555; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="slide">
        <h2>🔄 Week {week['number']}: {week['theme']}</h2>
        <div class="section">
            <div class="section-title">SHIP (交付)</div>
            <div class="section-content">{week['ship_task']}</div>
        </div>
        <div class="section">
            <div class="section-title">NEXT (迭代)</div>
            <div class="section-content">{week['next_focus']}</div>
        </div>
    </div>
</body>
</html>"""

    def _generate_final_slide(self, plan_data: dict, style: str) -> str:
        """生成总结幻灯片."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>开始行动</title>
    <style>
        body {{ margin: 0; padding: 40px; font-family: 'Segoe UI', sans-serif; }}
        .slide {{ width: 1280px; height: 720px; display: flex; flex-direction: column; justify-content: center; align-items: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        h2 {{ font-size: 48px; margin-bottom: 30px; }}
        .quote {{ font-size: 28px; font-style: italic; opacity: 0.9; max-width: 800px; text-align: center; }}
        .cta {{ font-size: 32px; margin-top: 50px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="slide">
        <h2>🚀 开始你的 Ship-Learn-Next 之旅</h2>
        <div class="quote">"100次重复胜过100小时学习"</div>
        <div class="cta">SHIP → LEARN → NEXT</div>
    </div>
</body>
</html>"""

    def _convert_to_pptx(self, html_files: list[Path], output_name: str) -> str | None:
        """调用 huashu-slides 转换为 PPTX."""
        if not self.huashu_slides_dir.exists():
            print(f"警告: 未找到 huashu-slides 目录: {self.huashu_slides_dir}")
            return None
        
        # 输出目录
        output_dir = self.plans_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{output_name}.pptx"
        
        # 构建命令
        html2pptx_script = self.huashu_slides_dir / "scripts" / "html2pptx.js"
        
        if not html2pptx_script.exists():
            print(f"警告: 未找到 html2pptx.js: {html2pptx_script}")
            return None
        
        # 构建文件列表参数
        file_list = " ".join([str(f) for f in html_files])
        cmd = f'node "{html2pptx_script}" {file_list} -o "{output_file}"'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode == 0 and output_file.exists():
                return str(output_file)
            else:
                print(f"转换失败: {result.stderr}")
                return None
        except Exception as e:
            print(f"调用 html2pptx 出错: {e}")
            return None


if __name__ == "__main__":
    # 测试
    exporter = PlanExporter()
    
    # 列出所有计划
    plans_dir = exporter.plans_dir
    if plans_dir.exists():
        for plan_file in plans_dir.glob("Plan-*.md"):
            print(f"找到计划: {plan_file.stem}")
