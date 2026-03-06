# Playwright 常用模式参考

## 选择器优先级

推荐的选择器使用顺序（从高到低）：

1. **data-testid** - `[data-testid="submit-btn"]` 最稳定
2. **role + name** - `role=button[name="Submit"]` 语义化
3. **placeholder/label** - `input[placeholder="Email"]` 用户可见
4. **text 匹配** - `text=Sign In` 简单直观
5. **CSS 选择器** - `#login-form .submit` 精确但脆弱
6. **XPath** - `//div[@class="content"]` 最后的手段

## 等待策略

```python
# 页面级等待
await page.wait_for_load_state("domcontentloaded")  # DOM 解析完成（最快）
await page.wait_for_load_state("load")               # 所有资源加载完
await page.wait_for_load_state("networkidle")         # 网络空闲（最慢但最稳）

# 元素级等待
await page.wait_for_selector("#result")                # 元素出现
await page.wait_for_selector("#spinner", state="hidden")  # 元素消失

# 条件等待
await page.wait_for_url("**/dashboard")               # URL 匹配
await page.wait_for_function("window.dataReady")       # JS 条件
await page.wait_for_timeout(2000)                      # 固定等待（尽量避免）
```

## 常见交互模式

### 登录流程
```
1. open <login-url>
2. snapshot               → 识别表单元素
3. fill <email> "xxx"
4. fill <password> "xxx"
5. click <submit>
6. wait url:**/dashboard  → 验证登录成功
7. state save auth.json   → 保存状态供后续使用
```

### 表单填写
```
1. open <form-url>
2. snapshot               → 识别所有表单字段
3. fill / select / check  → 逐一填写
4. screenshot             → 截图确认
5. click <submit>
6. wait networkidle       → 等待提交完成
```

### 内容抓取
```
1. open <url>
2. wait networkidle
3. extract --mode full    → 智能提取正文
   或:
   get text <selector>   → 提取特定元素文本
   screenshot --full     → 全页截图
```

### 无限滚动页面
```
1. open <url>
2. 循环:
   - scroll down 1000
   - wait 1500
   - get count ".item"   → 检查元素数量
   - 直到数量不再增长
3. extract / screenshot
```

## 处理弹窗和对话框

```python
# 监听对话框（alert/confirm/prompt）
page.on("dialog", lambda d: d.accept())

# 处理新窗口/标签页
async with context.expect_page() as new_page_info:
    await page.click("a[target='_blank']")
new_page = await new_page_info.value
```

## iframe 处理

```python
# 切换到 iframe
frame = page.frame_locator("#iframe-id")
await frame.locator("button").click()

# 或通过 frame 名称
frame = page.frame(name="content-frame")
await frame.click("button")
```

## 文件上传

```python
# 设置要上传的文件
async with page.expect_file_chooser() as fc_info:
    await page.click("#upload-button")
file_chooser = await fc_info.value
await file_chooser.set_files("/path/to/file.pdf")
```

## 网络拦截

```python
# 拦截请求
await page.route("**/api/**", lambda route: route.fulfill(
    status=200,
    body=json.dumps({"mock": True}),
    headers={"Content-Type": "application/json"}
))

# 阻止图片加载（加速页面）
await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
```

## 反检测最佳实践

1. 设置真实的 User-Agent
2. 注入 `navigator.webdriver = undefined`
3. 伪造 `navigator.plugins` 和 `navigator.languages`
4. 添加随机延迟模拟人类操作
5. 设置真实的 viewport 尺寸
6. 使用 `--disable-blink-features=AutomationControlled`

## 性能优化

- 使用 `domcontentloaded` 而非 `networkidle`（速度差 2-5x）
- 阻止不必要的资源加载（图片、字体、CSS）
- 复用浏览器上下文而非每次重建
- 使用 `state save/load` 跳过重复登录
