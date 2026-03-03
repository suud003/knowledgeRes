# Ship-Learn-Next Plan - {{plan_name}}

> 🚀 **核心理念**: 100次重复胜过100小时学习  
> 📅 **创建日期**: {{created_date}}  
> 🎯 **知识来源**: {{source_topic}}  
> ⏱️ **计划周期**: {{duration_weeks}} 周

---

## 📋 任务概述

### 学习目标
{{learning_goal}}

### 知识来源摘要
{{knowledge_summary}}

### 预期成果
{{expected_outcomes}}

---

## 🔄 迭代计划

{% for week in weeks %}
### Week {{week.number}}: {{week.theme}}

**时间**: {{week.start_date}} - {{week.end_date}}

#### SHIP (交付)
{{week.ship_task}}

**验收标准**:
- [ ] {{week.ship_criteria}}

#### LEARN (反思)
完成交付后，回答以下问题：

1. **什么有效？**
   - 

2. **什么无效？**
   - 

3. **有什么意外发现？**
   - 

4. **下次如何改进？**
   - 

#### NEXT (迭代)
基于反思，下一轮的改进方向：
{{week.next_focus}}

---
{% endfor %}

## 📊 进度跟踪

| 周次 | 状态 | 交付物 | 完成日期 | 反思记录 |
|------|------|--------|----------|----------|
{% for week in weeks %}
| Week {{week.number}} | ⏳ 待开始 | - | - | - |
{% endfor %}

**图例**: ⏳ 待开始 | 🔄 进行中 | ✅ 已完成

---

## 📝 详细记录

### Week 1 执行记录

**实际交付物**: 

**执行反思**:

**改进建议**:

---

### Week 2 执行记录

**实际交付物**: 

**执行反思**:

**改进建议**:

---

### Week 3 执行记录

**实际交付物**: 

**执行反思**:

**改进建议**:

---

### Week 4 执行记录

**实际交付物**: 

**执行反思**:

**改进建议**:

---

## 🎯 最终总结

### 成果回顾

### 关键收获

### 后续建议

---

*计划由 Ship-Learn-Next Skill 自动生成*  
*更新时间: {{updated_date}}*
