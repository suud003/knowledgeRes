"""Ship-Learn-Next 计划生成器."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class ShipLearnPlanner:
    """生成 Ship-Learn-Next 迭代学习计划."""

    def __init__(self, plans_dir: Path | None = None):
        """初始化规划器.
        
        Args:
            plans_dir: 计划文件存储目录，默认使用 skills/ship-learn-next/plans/
        """
        if plans_dir is None:
            skills_dir = Path(__file__).parent.parent
            plans_dir = skills_dir / "plans"
        self.plans_dir = plans_dir
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def create_plan(
        self,
        plan_name: str,
        source_topic: str,
        knowledge_content: str,
        learning_goal: str = "",
        duration_weeks: int = 4,
    ) -> dict[str, Any]:
        """创建 Ship-Learn-Next 计划.
        
        Args:
            plan_name: 计划名称（如 "Prompt工程实践"）
            source_topic: 知识来源主题（如 "reading", "ai"）
            knowledge_content: 知识内容文本
            learning_goal: 学习目标（可选）
            duration_weeks: 计划周期（默认4周）
            
        Returns:
            包含计划信息的字典
        """
        # 提取知识要点
        knowledge_summary = self._extract_knowledge_summary(knowledge_content)
        
        # 如果没有指定学习目标，自动生成
        if not learning_goal:
            learning_goal = f"将{source_topic}主题中的知识转化为实际能力"
        
        # 生成预期成果
        expected_outcomes = self._generate_expected_outcomes(plan_name, duration_weeks)
        
        # 生成每周迭代计划
        weeks = self._generate_weeks(plan_name, knowledge_summary, duration_weeks)
        
        # 生成计划文档
        plan_data = {
            "plan_name": plan_name,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "updated_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source_topic": source_topic,
            "learning_goal": learning_goal,
            "knowledge_summary": knowledge_summary,
            "expected_outcomes": expected_outcomes,
            "duration_weeks": duration_weeks,
            "weeks": weeks,
        }
        
        # 保存计划文件
        plan_file = self._save_plan(plan_data)
        plan_data["plan_file"] = str(plan_file)
        plan_data["plan_id"] = plan_file.stem
        
        return plan_data

    def _extract_knowledge_summary(self, content: str) -> str:
        """从知识内容中提取关键要点."""
        # 简单实现：提取前 500 字符作为摘要
        # 实际可以接入 LLM 进行更智能的摘要
        lines = content.strip().split("\n")
        summary_lines = []
        
        for line in lines[:20]:  # 取前20行
            line = line.strip()
            # 跳过空行和纯标记行
            if not line or line.startswith("---") or line.startswith("==="):
                continue
            # 提取标题行
            if line.startswith("#") or line.startswith("-") or line.startswith("*"):
                summary_lines.append(line.lstrip("#-* ").strip()[:100])
            # 提取正文
            elif len(line) > 10 and not line.startswith(">"):
                summary_lines.append(line[:100])
        
        summary = " | ".join(summary_lines[:5])  # 取前5个要点
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return summary if summary else "从知识库提取的学习内容"

    def _generate_expected_outcomes(self, plan_name: str, weeks: int) -> str:
        """生成预期成果描述."""
        outcomes = [
            f"完成{weeks}轮 Ship-Learn-Next 迭代循环",
            "形成可复用的实践经验",
            "产出可分享的学习成果",
        ]
        return "\n".join(f"- {o}" for o in outcomes)

    def _generate_weeks(
        self, plan_name: str, knowledge_summary: str, duration: int
    ) -> list[dict[str, Any]]:
        """生成每周迭代计划."""
        weeks = []
        base_date = datetime.now()
        
        # 根据计划名称推断任务类型
        task_type = self._detect_task_type(plan_name)
        
        for i in range(duration):
            week_num = i + 1
            start_date = base_date + timedelta(days=i * 7)
            end_date = start_date + timedelta(days=6)
            
            # 生成每周的具体任务
            ship_task, ship_criteria = self._generate_ship_task(task_type, week_num)
            next_focus = self._generate_next_focus(week_num, duration)
            
            weeks.append({
                "number": week_num,
                "theme": f"第{week_num}轮迭代",
                "start_date": start_date.strftime("%m/%d"),
                "end_date": end_date.strftime("%m/%d"),
                "ship_task": ship_task,
                "ship_criteria": ship_criteria,
                "next_focus": next_focus,
            })
        
        return weeks

    def _detect_task_type(self, plan_name: str) -> str:
        """根据计划名称检测任务类型."""
        name_lower = plan_name.lower()
        
        if any(k in name_lower for k in ["prompt", "ai", "gpt", "claude"]):
            return "ai_learning"
        elif any(k in name_lower for k in ["产品", "prd", "需求", "设计", "原型"]):
            return "product_design"
        elif any(k in name_lower for k in ["代码", "编程", "开发", "python", "js"]):
            return "coding"
        elif any(k in name_lower for k in ["写作", "文章", "博客", "公众号"]):
            return "writing"
        elif any(k in name_lower for k in ["读书", "阅读", "学习", "课程"]):
            return "learning"
        else:
            return "general"

    def _generate_ship_task(self, task_type: str, week: int) -> tuple[str, str]:
        """生成 SHIP 任务和验收标准."""
        tasks = {
            "ai_learning": {
                1: ("用学到的 AI 技巧完成 1 个实际工作场景的优化", "产出优化前后的对比文档"),
                2: ("用学到的 AI 技巧完成 3 个不同场景的实践", "每个场景都有明确的效果对比"),
                3: ("将有效技巧整理成个人 Prompt 模板库", "至少包含 5 个可复用模板"),
                4: ("撰写学习总结文章或制作分享 PPT", "形成可传播的输出物"),
            },
            "product_design": {
                1: ("完成产品原型的第一个版本", "可交互的原型或流程图"),
                2: ("进行 3-5 个用户访谈", "访谈记录和洞察总结"),
                3: ("根据反馈迭代原型", "迭代前后的对比说明"),
                4: ("撰写产品需求文档或方案", "完整的 PRD 或产品方案"),
            },
            "coding": {
                1: ("完成 MVP 的第一个功能模块", "可运行的代码 + 测试"),
                2: ("重构代码并添加单元测试", "测试覆盖率 > 60%"),
                3: ("添加文档和 README", "完整的项目文档"),
                4: ("发布或部署项目", "可访问的 demo 或仓库"),
            },
            "writing": {
                1: ("完成文章初稿", "不少于 1000 字的初稿"),
                2: ("根据反馈修改文章", "修改前后的对比"),
                3: ("优化标题和配图", "3 个备选标题 + 配图"),
                4: ("发布文章并收集反馈", "发布链接 + 数据截图"),
            },
            "learning": {
                1: ("完成第 1 章/第 1 节的学习和实践", "学习笔记 + 实践产出"),
                2: ("完成第 2 章/第 2 节的学习和实践", "学习笔记 + 实践产出"),
                3: ("完成第 3 章/第 3 节的学习和实践", "学习笔记 + 实践产出"),
                4: ("完成全书/全课程总结", "知识地图 + 行动清单"),
            },
            "general": {
                1: ("完成第一次实践尝试", "可展示的具体产出"),
                2: ("根据反思优化方案", "优化后的版本"),
                3: ("扩大实践范围", "更多场景的应用"),
                4: ("总结经验并分享", "总结文档或分享"),
            },
        }
        
        # 获取任务，如果没有则使用 general 的循环
        task_map = tasks.get(task_type, tasks["general"])
        if week in task_map:
            return task_map[week]
        else:
            # 超过 4 周时循环使用
            cycle_week = ((week - 1) % 4) + 1
            return task_map.get(cycle_week, tasks["general"][4])

    def _generate_next_focus(self, week: int, total: int) -> str:
        """生成 NEXT 阶段的改进方向."""
        if week < total:
            return f"基于 Week {week} 的反思，优化 Week {week + 1} 的执行方案"
        else:
            return "完成整个计划，总结可复用的方法论"

    def _save_plan(self, plan_data: dict[str, Any]) -> Path:
        """保存计划到文件."""
        # 生成文件名
        safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', plan_data["plan_name"])
        date_str = plan_data["created_date"].replace("-", "")
        filename = f"Plan-{safe_name}-{date_str}.md"
        filepath = self.plans_dir / filename
        
        # 读取模板
        template_path = Path(__file__).parent.parent / "templates" / "plan-template.md"
        
        # 如果模板存在，使用模板渲染
        if template_path.exists():
            template_content = template_path.read_text(encoding="utf-8")
            # 简单的模板替换（实际可以用 Jinja2）
            content = self._render_template(template_content, plan_data)
        else:
            # 使用默认格式
            content = self._render_default_format(plan_data)
        
        # 写入文件
        filepath.write_text(content, encoding="utf-8")
        
        return filepath

    def _render_template(self, template: str, data: dict[str, Any]) -> str:
        """渲染模板（Jinja2 风格）."""
        try:
            # 尝试使用 jinja2
            from jinja2 import Template
            jinja_template = Template(template)
            return jinja_template.render(**data)
        except ImportError:
            # 如果没有 jinja2，使用简单替换
            return self._simple_render(template, data)

    def _simple_render(self, template: str, data: dict[str, Any]) -> str:
        """简单的模板渲染（备用）."""
        content = template
        
        # 替换简单变量
        for key, value in data.items():
            if isinstance(value, str):
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, value)
        
        # 处理 weeks 列表（for 循环）
        import re
        
        # 匹配 {% for week in weeks %}...{% endfor %}
        for_pattern = r"{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}"
        
        def replace_for(match):
            var_name = match.group(1)
            list_name = match.group(2)
            template_body = match.group(3)
            
            items = data.get(list_name, [])
            results = []
            
            for item in items:
                item_content = template_body
                # 替换 item 的属性
                if isinstance(item, dict):
                    for key, val in item.items():
                        placeholder = f"{{{{{var_name}.{key}}}}}"
                        item_content = item_content.replace(placeholder, str(val))
                results.append(item_content)
            
            return "".join(results)
        
        content = re.sub(for_pattern, replace_for, content, flags=re.DOTALL)
        
        return content

    def _render_default_format(self, data: dict[str, Any]) -> str:
        """使用默认格式渲染."""
        lines = [
            f"# Ship-Learn-Next Plan - {data['plan_name']}",
            "",
            f"> 创建日期: {data['created_date']}",
            f"> 知识来源: {data['source_topic']}",
            f"> 计划周期: {data['duration_weeks']} 周",
            "",
            "## 学习目标",
            data['learning_goal'],
            "",
            "## 知识摘要",
            data['knowledge_summary'],
            "",
            "## 预期成果",
            data['expected_outcomes'],
            "",
            "## 迭代计划",
            "",
        ]
        
        for week in data['weeks']:
            lines.extend([
                f"### Week {week['number']}",
                f"**SHIP**: {week['ship_task']}",
                f"**验收**: {week['ship_criteria']}",
                f"**NEXT**: {week['next_focus']}",
                "",
            ])
        
        lines.append("---")
        lines.append(f"*更新时间: {data['updated_date']}*")
        
        return "\n".join(lines)

    def list_plans(self) -> list[dict[str, Any]]:
        """列出所有计划."""
        plans = []
        for plan_file in sorted(self.plans_dir.glob("Plan-*.md"), reverse=True):
            # 解析文件名获取基本信息
            parts = plan_file.stem.split("-")
            if len(parts) >= 3:
                plan_name = "-".join(parts[1:-1])
                date_str = parts[-1]
                plans.append({
                    "plan_id": plan_file.stem,
                    "name": plan_name,
                    "date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}",
                    "file": str(plan_file),
                })
        return plans


if __name__ == "__main__":
    # 测试
    planner = ShipLearnPlanner()
    
    # 模拟测试
    test_content = """
    # Prompt Engineering
    
    ## 核心技巧
    - 使用清晰的具体指令
    - 提供示例（Few-shot）
    - 分解复杂任务
    - 让模型解释思考过程
    
    ## 应用场景
    - 代码生成
    - 文案创作
    - 数据分析
    """
    
    plan = planner.create_plan(
        plan_name="Prompt工程实践",
        source_topic="ai",
        knowledge_content=test_content,
        learning_goal="掌握 Prompt Engineering 并在工作中实际应用",
        duration_weeks=4,
    )
    
    print(f"计划已创建: {plan['plan_file']}")
    print(f"计划ID: {plan['plan_id']}")
