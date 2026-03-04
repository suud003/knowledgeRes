# Moos MCP 服务器配置指南

## 问题描述

MCP服务器启动时出现权限错误：`PermissionError: [Errno 13] Permission denied: '.'`

## 问题根因

配置文件 `config.yaml` 中使用了相对路径：
```yaml
sync:
  raw_dir: "data/raw"
  context_dir: "data/context"
```

但MCP服务器启动时没有正确设置工作目录，导致相对路径解析错误。

## 解决方案

在Claude Code的MCP配置中，必须指定正确的 `cwd`（当前工作目录）参数。

### 1. 正确的MCP配置

在Claude Code的设置中，添加以下MCP服务器配置：

```json
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"],
      "cwd": "g:\\tianyishao\\Moos-share"
    }
  }
}
```

**关键点：**
- `cwd` 必须设置为项目的绝对路径
- Windows路径需要使用双反斜杠 `\\` 转义

### 2. 验证配置

重启Claude Code后，可以通过以下方式验证MCP服务器是否正常工作：

```python
# 测试MCP工具
list_topics()  # 应该返回主题列表
add_note(content="测试笔记", topic="test")  # 应该成功添加笔记
```

### 3. 常见错误

**错误配置示例：**
```json
// 缺少cwd参数
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"]
    }
  }
}
```

**错误配置示例：**
```json
// cwd路径错误
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"],
      "cwd": "Moos-share"  // 相对路径，错误！
    }
  }
}
```

### 4. 路径修复说明

我们已经修复了代码中的路径处理问题：

1. **配置加载**：在 `src/pa/config/settings.py` 中，`load_config` 函数现在会将相对路径解析为绝对路径
2. **路径处理**：在 `src/pa/mcp_server.py` 中，所有路径操作都使用 `Path().resolve()` 确保绝对路径
3. **工作目录**：在 `src/pa/mcp_server.py` 的 `main()` 函数中设置了正确的工作目录

### 5. 测试步骤

1. 按照上述配置更新Claude Code的MCP设置
2. 重启Claude Code
3. 尝试使用MCP工具：
   - `list_topics()` - 列出所有主题
   - `add_note(content="测试", topic="test")` - 添加测试笔记
   - `collect_content(url="https://example.com", html="<html>...</html>")` - 测试内容收集

### 6. 故障排除

如果仍然遇到问题：

1. **检查路径**：确认 `cwd` 路径是否正确
2. **检查权限**：确认对项目目录有读写权限
3. **查看日志**：检查Claude Code的控制台输出
4. **验证依赖**：确保已安装所有依赖包：`pip install -e .`

## 技术细节

- **项目根目录**：`g:\\tianyishao\\Moos-share`
- **数据目录**：`data/raw` 和 `data/context`（相对于项目根目录）
- **MCP入口**：`src/pa/mcp_server.py`
- **依赖管理**：通过 `setup.py` 安装

## 总结

MCP服务器配置的关键是正确设置 `cwd` 参数，确保相对路径能够正确解析为绝对路径。按照上述指南配置后，MCP服务器应该能够正常工作。