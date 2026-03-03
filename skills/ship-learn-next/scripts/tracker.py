"""Ship-Learn-Next 迭代跟踪器."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


class IterationTracker:
    """跟踪 Ship-Learn-Next 计划的执行进度."""

    def __init__(self, plans_dir: Path | None = None):
        """初始化跟踪器.
        
        Args:
            plans_dir: 计划文件存储目录
        """
        if plans_dir is None:
            skills_dir = Path(__file__).parent.parent
            plans_dir = skills_dir / "plans"
        self.plans_dir = plans_dir
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def track_iteration(
        self,
        plan_id: str,
        week: int,
        ship_result: str,
        learn_reflection: str,
        next_adjustment: str = "",
    ) -> dict[str, Any]:
        """记录一次迭代的结果.
        
        Args:
            plan_id: 计划ID（文件名）
            week: 周次（1-4）
            ship_result: SHIP 交付物描述
            learn_reflection: LEARN 反思内容
            next_adjustment: NEXT 调整建议（可选）
            
        Returns:
            更新后的计划信息
        """
        # 查找计划文件
        plan_file = self._find_plan_file(plan_id)
        if not plan_file:
            return {"error": f"未找到计划: {plan_id}"}
        
        # 读取现有内容
        content = plan_file.read_text(encoding="utf-8")
        
        # 更新进度跟踪表
        content = self._update_progress_table(content, week, ship_result)
        
        # 添加详细记录
        content = self._add_iteration_record(
            content, week, ship_result, learn_reflection, next_adjustment
        )
        
        # 更新文件
        plan_file.write_text(content, encoding="utf-8")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "week": week,
            "status": "completed",
            "file": str(plan_file),
        }

    def get_plan_status(self, plan_id: str) -> dict[str, Any]:
        """获取计划执行状态.
        
        Args:
            plan_id: 计划ID
            
        Returns:
            计划状态信息
        """
        plan_file = self._find_plan_file(plan_id)
        if not plan_file:
            return {"error": f"未找到计划: {plan_id}"}
        
        content = plan_file.read_text(encoding="utf-8")
        
        # 解析进度
        completed_weeks = self._parse_completed_weeks(content)
        total_weeks = self._parse_total_weeks(content)
        
        return {
            "plan_id": plan_id,
            "file": str(plan_file),
            "completed_weeks": completed_weeks,
            "total_weeks": total_weeks,
            "progress": f"{len(completed_weeks)}/{total_weeks}",
            "status": "completed" if len(completed_weeks) >= total_weeks else "in_progress",
        }

    def list_active_plans(self) -> list[dict[str, Any]]:
        """列出所有进行中的计划."""
        plans = []
        
        for plan_file in self.plans_dir.glob("Plan-*.md"):
            plan_id = plan_file.stem
            status = self.get_plan_status(plan_id)
            
            if "error" not in status:
                # 提取计划名称
                parts = plan_id.split("-")
                if len(parts) >= 3:
                    plan_name = "-".join(parts[1:-1])
                    date_str = parts[-1]
                    
                    plans.append({
                        "plan_id": plan_id,
                        "name": plan_name,
                        "date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}",
                        "progress": status["progress"],
                        "status": status["status"],
                        "file": str(plan_file),
                    })
        
        # 按日期倒序排序
        plans.sort(key=lambda x: x["date"], reverse=True)
        return plans

    def _find_plan_file(self, plan_id: str) -> Path | None:
        """查找计划文件."""
        # 直接匹配
        plan_file = self.plans_dir / f"{plan_id}.md"
        if plan_file.exists():
            return plan_file
        
        # 模糊匹配（尝试添加 Plan- 前缀）
        if not plan_id.startswith("Plan-"):
            plan_file = self.plans_dir / f"Plan-{plan_id}.md"
            if plan_file.exists():
                return plan_file
        
        # 部分匹配
        for file in self.plans_dir.glob("*.md"):
            if plan_id in file.stem:
                return file
        
        return None

    def _update_progress_table(self, content: str, week: int, ship_result: str) -> str:
        """更新进度跟踪表."""
        date_str = datetime.now().strftime("%m/%d")
        
        # 查找并更新对应周的行
        # 匹配 | Week X | 状态 | 交付物 | 完成日期 | 反思记录 |
        pattern = rf"(\| Week {week} \| )[^|]*( \| )[^|]*( \| )[^|]*( \| )[^|]*( \|)"
        replacement = rf"\1✅ 已完成\2{ship_result[:30]}...\2{date_str}\2已记录\4"
        
        updated_content = re.sub(pattern, replacement, content)
        
        return updated_content

    def _add_iteration_record(
        self,
        content: str,
        week: int,
        ship_result: str,
        learn_reflection: str,
        next_adjustment: str,
    ) -> str:
        """添加迭代详细记录."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        record = f"""
### Week {week} 执行记录（更新于 {now}）

**实际交付物**: 
{ship_result}

**执行反思**:
{learn_reflection}

**改进建议**:
{next_adjustment or "基于反思自动生成的改进方向"}

---
"""
        
        # 查找 Week X 执行记录的位置并替换
        section_header = f"### Week {week} 执行记录"
        
        if section_header in content:
            # 已存在，替换内容
            pattern = rf"({re.escape(section_header)}.*?)(### Week {week + 1}|## 🎯 最终总结|$)"
            replacement = rf"{record.strip()}\n\n\2"
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # 不存在，在 Week X 章节后添加
            insert_marker = f"### Week {week} 执行记录"
            if insert_marker not in content:
                # 在进度跟踪表后添加
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "进度跟踪" in line and i < len(lines) - 1:
                        # 在进度跟踪表后找到合适位置插入
                        pass
                
                # 简单方案：在文件末尾前添加
                if "## 🎯 最终总结" in content:
                    content = content.replace(
                        "## 🎯 最终总结",
                        f"{record}\n## 🎯 最终总结"
                    )
                else:
                    content = content + "\n" + record
        
        return content

    def _parse_completed_weeks(self, content: str) -> list[int]:
        """解析已完成的周次."""
        completed = []
        
        # 查找进度表中的完成状态
        for match in re.finditer(r"\| Week (\d+) \| ✅ 已完成", content):
            week = int(match.group(1))
            completed.append(week)
        
        return sorted(completed)

    def _parse_total_weeks(self, content: str) -> int:
        """解析计划总周数."""
        # 查找 "计划周期: X 周"
        match = re.search(r"计划周期[:：]\s*(\d+)\s*周", content)
        if match:
            return int(match.group(1))
        
        # 查找所有 Week X
        weeks = re.findall(r"Week (\d+)", content)
        if weeks:
            return max(int(w) for w in weeks)
        
        return 4  # 默认 4 周

    def generate_summary(self, plan_id: str) -> dict[str, Any]:
        """生成计划执行总结.
        
        Args:
            plan_id: 计划ID
            
        Returns:
            总结信息
        """
        plan_file = self._find_plan_file(plan_id)
        if not plan_file:
            return {"error": f"未找到计划: {plan_id}"}
        
        content = plan_file.read_text(encoding="utf-8")
        
        # 提取关键信息
        completed = self._parse_completed_weeks(content)
        total = self._parse_total_weeks(content)
        
        # 提取所有反思
        reflections = re.findall(
            r"执行反思[:：]\s*\n(.+?)(?=\n\*\*改进建议|\n---|$)",
            content,
            re.DOTALL
        )
        
        # 提取所有交付物
        deliverables = re.findall(
            r"实际交付物[:：]\s*\n(.+?)(?=\n\*\*执行反思|\n---|$)",
            content,
            re.DOTALL
        )
        
        return {
            "plan_id": plan_id,
            "total_weeks": total,
            "completed_weeks": len(completed),
            "progress_percentage": round(len(completed) / total * 100, 1),
            "reflections_count": len(reflections),
            "deliverables_count": len(deliverables),
            "key_insights": self._extract_key_insights(reflections),
        }

    def _extract_key_insights(self, reflections: list[str]) -> list[str]:
        """从反思中提取关键洞察."""
        insights = []
        
        for reflection in reflections:
            lines = reflection.strip().split("\n")
            for line in lines:
                line = line.strip().lstrip("- * 1234567890.")
                if len(line) > 10 and len(line) < 200:
                    insights.append(line)
        
        # 去重并返回前 5 条
        unique_insights = list(dict.fromkeys(insights))
        return unique_insights[:5]


if __name__ == "__main__":
    # 测试
    tracker = IterationTracker()
    
    # 列出所有计划
    plans = tracker.list_active_plans()
    print(f"找到 {len(plans)} 个计划")
    for plan in plans:
        print(f"  - {plan['name']}: {plan['progress']}")
