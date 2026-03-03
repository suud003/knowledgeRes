# Huashu Slides - 环境设置指南

## 概述

本 Skill 提供华树风格 PPT 幻灯片制作能力，包含：
- 🎨 AI 图像生成（支持 GLM CogView 和 Gemini）
- 📄 HTML 到 PowerPoint 转换
- 🖼️ 设计参考与风格库

## 快速开始

### 1. Python 环境设置

```bash
cd skills/huashu-slides

# 方式 A: 使用 uv（推荐）
uv pip install -r requirements.txt

# 方式 B: 使用 pip
pip install -r requirements.txt
```

### 2. Node.js 环境设置

```bash
cd skills/huashu-slides

# 安装依赖
npm install

# 安装 Playwright 浏览器
npx playwright install chromium
```

### 3. API Key 配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，**至少配置一个** API Key：

```bash
# 智谱 GLM CogView (推荐中文场景)
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# Google Gemini (可选)
# GEMINI_API_KEY=your_gemini_api_key_here
```

**获取 API Key：**
- 智谱 GLM：https://open.bigmodel.cn/
- Google Gemini：https://aistudio.google.com/apikey

## 脚本使用

### 生成图片 (generate_image.py)

支持两个 AI 提供商：
- **GLM CogView-4**：智谱出品，中文理解更好
- **Gemini**：Google 出品，支持图片编辑

```bash
# 自动检测（根据环境变量选择提供商）
uv run scripts/generate_image.py \
  --prompt "一只可爱的猫咪在草地上玩耍" \
  --filename "cat.png"

# 指定使用 GLM CogView
uv run scripts/generate_image.py \
  --prompt "中国山水画风景" \
  --filename "landscape.png" \
  --provider glm \
  --size 1344x768

# 指定使用 Gemini
uv run scripts/generate_image.py \
  --prompt "Abstract geometric art" \
  --filename "abstract.png" \
  --provider gemini \
  --resolution 2K

# 编辑现有图片（仅 Gemini 支持）
uv run scripts/generate_image.py \
  --prompt "Add a rainbow to the sky" \
  --input-image "input.png" \
  --filename "edited.png" \
  --provider gemini
```

**参数说明:**

| 参数 | 说明 | 适用 |
|------|------|------|
| `--prompt, -p` | 图片描述（必需） | 全部 |
| `--filename, -f` | 输出文件名（必需） | 全部 |
| `--provider` | 指定提供商 (glm/gemini) | 全部 |
| `--api-key, -k` | API Key（覆盖环境变量） | 全部 |
| `--size, -s` | 图片尺寸 | GLM |
| `--resolution, -r` | 分辨率 (1K/2K/4K) | Gemini |
| `--input-image, -i` | 输入图片（编辑模式） | Gemini |

**GLM 支持的尺寸：**
- `1024x1024` (默认，正方形)
- `768x1344` / `1344x768` (竖版/横版)
- `864x1152` / `1152x864`
- `1440x720` / `720x1440` (超宽/超高)

### HTML 转 PowerPoint (html2pptx.js)

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('./scripts/html2pptx');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';

// 转换 HTML 文件到 PPT 幻灯片
const { slide, placeholders } = await html2pptx('slide.html', pptx);

// 如果有占位符，可以添加图表等
if (placeholders.length > 0) {
  slide.addChart(pptx.charts.LINE, data, placeholders[0]);
}

await pptx.writeFile('output.pptx');
```

**HTML 文件要求:**
- `body` 尺寸必须匹配 PPT 布局（16:9 = 960x540px）
- 文本必须包裹在 `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>` 标签中
- 背景支持纯色或图片
- 支持 CSS 属性：字体、颜色、边距、旋转等

## 目录结构

```
skills/huashu-slides/
├── SKILL.md              # Skill 定义文件
├── README.md             # 本文件
├── requirements.txt      # Python 依赖
├── package.json          # Node.js 依赖
├── .env.example          # 环境变量模板
├── scripts/
│   ├── generate_image.py # Gemini 图像生成
│   ├── create_slides.py  # 幻灯片创建辅助
│   └── html2pptx.js      # HTML 转 PPTX
├── references/
│   ├── prompt-templates.md      # 提示词模板
│   ├── proven-styles-gallery.md # 验证过的风格库
│   ├── proven-styles-snoopy.md  # Snoopy 风格参考
│   ├── design-movements.md      # 设计流派参考
│   └── design-principles.md     # 设计原则
└── assets/
    ├── style-samples/    # 风格样本图片
    ├── character/        # 角色素材
    └── workflow.html     # 工作流示意
```

## 故障排查

### Playwright 浏览器未安装
```bash
npx playwright install chromium
```

### Gemini API 错误
1. 检查 API Key 是否正确
2. 确认账户有配额
3. 检查网络连接（可能需要代理）

### 图片生成失败
- 确保提示词清晰具体
- 避免包含敏感内容
- 尝试调整分辨率

## 相关资源

- [Gemini API 文档](https://ai.google.dev/docs)
- [PptxGenJS 文档](https://gitbrent.github.io/PptxGenJS/)
- [Playwright 文档](https://playwright.dev/)
