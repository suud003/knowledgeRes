# iWiki MCP API 参考文档

本文档详细说明 iWiki MCP 提供的所有工具 API 的参数和返回值。

## 文档搜索类

### aiSearchDocument

AI 语义搜索 iWiki 文档内容。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| query | string | ✅ | 搜索关键词或短语 |
| limit | number | ❌ | 返回结果数量，默认 5，推荐 10 |
| space_ids | string | ❌ | 限定搜索的空间 ID，多个用逗号分隔 |
| topic_ids | string | ❌ | 限定搜索的专题 ID，多个用逗号分隔 |
| doc_objs | array | ❌ | 指定搜索的文档对象列表，每项包含 `doc_id`(number) 和 `is_folder`(boolean) |

**返回：**
```json
[{
  "docid": "123456",
  "title": "文档标题",
  "content": "匹配的内容片段...",
  "url": "https://iwiki.woa.com/p/123456",
  "source": "来源",
  "update_time": "2025-01-01T00:00:00Z",
  "file_type": "MD",
  "attachment_id": null
}]
```

### searchDocument

传统关键词搜索，支持多维度筛选。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| query | string | ✅ | 搜索关键词 |
| search_type | string[] | ❌ | 搜索类型：space/comment/attachment/page/all |
| space_id | string[] | ❌ | 空间 ID 列表 |
| tags | string | ❌ | 标签，多个用英文逗号分隔 |
| author | string[] | ❌ | 作者列表 |
| from | string | ❌ | 来源：iWiki/km/all |

### glossaryTermSearch

搜索词库中的词条信息。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| keyword | string | ✅ | 搜索关键词 |
| limit | number | ❌ | 返回数量限制，默认 10 |

---

## 文档读取类

### getDocument

获取文档完整内容（Markdown 格式）。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | string | ✅ | 文档 ID |

**返回：** Markdown 格式的文档正文内容

### metadata

获取文档元数据信息。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | string | ✅ | 文档 ID |

**返回：**
```json
{
  "id": 123456,
  "title": "文档标题",
  "content_type": "MD",
  "creator": "creator_name",
  "create_time": "2025-01-01T00:00:00Z",
  "modifier": "modifier_name",
  "modify_time": "2025-01-01T00:00:00Z",
  "space_id": 12345
}
```

### getSpacePageTree

获取空间目录树结构。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| parentid | string | ✅ | 父级文档 ID |

**返回：**
```json
[{
  "docid": 123456,
  "title": "子文档标题",
  "parentid": 67890,
  "has_children": true
}]
```

### listImages

获取文档内的图片附件 ID 列表。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | string | ✅ | 文档 ID |

**返回：** 附件 ID 数组 `["111", "222", "333"]`

### getAttachmentDownloadUrl

获取附件的临时下载 URL。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| attachmentid | string | ✅ | 附件 ID |

**返回：** 临时下载链接

---

## 文档写入类

### createDocument

创建新文档。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spaceid | number | ✅ | 空间 ID |
| parentid | number | ✅ | 父文档 ID |
| title | string | ✅ | 文档标题 |
| body | string | ✅ | 文档内容（**不能为空**） |
| contenttype | string | ❌ | 类型：DOC/MD/FOLDER/VIKA，默认 MD |
| body_mode | string | ❌ | 内容格式，HTML 时指定为 "html" |

**返回：**
```json
{
  "id": 123456,
  "title": "新文档标题",
  "url": "https://iwiki.woa.com/p/123456"
}
```

### saveDocument

完整更新文档内容。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | number | ✅ | 文档 ID |
| title | string | ✅ | 文档标题 |
| body | string | ✅ | 文档内容（**不能为空**） |

### saveDocumentParts

局部更新文档（在头部或尾部追加内容）。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | number | ✅ | 文档 ID |
| title | string | ✅ | 文档标题 |
| before | string | ❌ | 插入到文档开头的内容 |
| after | string | ❌ | 追加到文档结尾的内容 |

### moveDocument

移动文档位置。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | number | ✅ | 要移动的文档 ID |
| new_parentid | number | ✅ | 新父目录 ID，不变传 0 |
| position | string | ❌ | 位置：append/below/above，默认 append |
| target_docid | number | ❌ | 目标文档 ID（position 为 below/above 时需要） |

---

## 标签管理类

### getDocumentTags

获取文档标签列表。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | string | ✅ | 文档 ID |

### addDocumentTags

批量添加标签。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docids | number[] | ✅ | 文档 ID 列表 |
| labels | string[] | ✅ | 标签名称列表 |

### deleteDocumentTag

删除单个标签。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | number | ✅ | 文档 ID |
| labelName | string | ✅ | 要删除的标签名称 |

---

## 评论类

### getComments

获取文档评论（分页）。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | number | ✅ | 文档 ID |
| pageIndex | number | ❌ | 页码，默认 1，每页 10 条 |

**返回说明：**
- `next_level_comments` 字段包含回复评论
- `total` 字段为评论总数，可计算总页数

### addComment

添加评论或回复。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | number | ✅ | 文档 ID |
| content | string | ✅ | 评论内容（Markdown 格式） |
| parent_id | number | ❌ | 父评论 ID，顶级评论传 0 或不传 |

---

## 引用关系类

### getDocQuoteList

获取当前文档引用的其他文档。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | string | ✅ | 文档 ID |
| start | number | ❌ | 起始位置，默认 1 |
| limit | number | ❌ | 每页数量，默认 10 |

### getDocQuoteListBy

获取引用了当前文档的其他文档。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| docid | string | ✅ | 文档 ID |
| start | number | ❌ | 起始位置，默认 1 |
| limit | number | ❌ | 每页数量，默认 10 |

---

## 空间管理类

### getSpaceInfoByKey

根据空间 Key 获取信息。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spaceKey | string | ✅ | 空间 Key（如 `~myname` 或 `woa`） |

### getSpaceInfoByName

根据空间名称获取信息。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spaceName | string | ✅ | 空间名称（支持模糊匹配） |

### getFavoriteSpaces

获取当前用户收藏的空间列表。

**参数：** 无

### getManageSpaces

获取当前用户管理的空间列表。

**参数：** 无

---

## 多维表格（Smartsheet）类

### smartsheetGetFields

获取表格字段定义。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | string | ✅ | 多维表格文档 ID |
| viewId | string | ❌ | 视图 ID |

### smartsheetAddField

添加新字段。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | number | ✅ | 多维表格文档 ID |
| name | string | ✅ | 字段名称 |
| type | string | ✅ | 字段类型（见下方支持的类型） |
| property | object | ✅ | 字段属性配置 |

**支持的字段类型：**
```
SingleText, Text, SingleSelect, MultiSelect, Number, Currency,
Percent, DateTime, Attachment, Member, Checkbox, Rating, URL,
Phone, Email, WorkDoc, OneWayLink, TwoWayLink, MagicLookUp,
Formula, AutoNumber, CreatedTime, LastModifiedTime, CreatedBy,
LastModifiedBy, Button
```

### smartsheetDeleteField

删除字段。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | string | ✅ | 多维表格文档 ID |
| fieldId | string | ✅ | 要删除的字段 ID |

### smartsheetGetViews

获取视图列表。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | string | ✅ | 多维表格文档 ID |
| view_type | string | ❌ | 视图类型筛选 |

**支持的视图类型：**
```
Grid, Gallery, Kanban, Gantt, Calendar, Architecture
```

### smartsheetGetRecords

查询记录数据。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | string | ✅ | 多维表格文档 ID |
| pageNum | number | ❌ | 页码，默认 1 |
| pageSize | number | ❌ | 每页数量，默认 100，最大 200 |
| viewId | string | ❌ | 视图 ID |
| maxRecords | number | ❌ | 最大返回记录数 |
| sort | string | ❌ | 排序规则 |
| recordIds | string | ❌ | 记录 ID 列表（逗号分隔） |
| fields | string | ❌ | 字段列表（逗号分隔） |
| filterByFormula | string | ❌ | 筛选公式 |
| cellFormat | string | ❌ | 单元格格式 |
| fieldKey | string | ❌ | 字段键类型：id/name |

### smartsheetAddRecords

批量添加记录。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | number | ✅ | 多维表格文档 ID |
| fieldKey | string | ✅ | 字段键类型：id/name |
| records | array | ✅ | 记录数组，每条含 fields 对象 |
| viewId | string | ❌ | 视图 ID |

**records 格式示例：**
```json
[
  { "fields": { "字段名1": "值1", "字段名2": "值2" } },
  { "fields": { "字段名1": "值3", "字段名2": "值4" } }
]
```

### smartsheetUpdateRecords

批量更新记录。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | number | ✅ | 多维表格文档 ID |
| fieldKey | string | ✅ | 字段键类型：id/name |
| records | array | ✅ | 记录数组，含 recordId 和 fields |
| viewId | string | ❌ | 视图 ID |

**records 格式示例：**
```json
[
  { "recordId": "rec123", "fields": { "字段名": "新值" } }
]
```

### smartsheetDeleteRecords

批量删除记录。

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| doc_id | string | ✅ | 多维表格文档 ID |
| record_ids | string[] | ✅ | 要删除的记录 ID 数组 |

---

## 文档导入类

### importDocument

导入文件到 iWiki（通过 HTTP `POST /import` 端点）。支持将本地文件（如 Markdown、Word 等）上传并导入为 iWiki 文档。

**请求方式：** `POST /import`（`multipart/form-data`）

**参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file | File | ✅ | 要导入的文件（最大 50MB） |
| parent_id | number | ✅ | 父文档/目录 ID，文件将导入到该目录下 |
| task_type | string | ❌ | 导入任务类型，默认 `md_import` |
| cover | boolean | ❌ | 是否覆盖同名文档，默认 `true` |

**请求头：**
| 请求头 | 描述 |
|--------|------|
| x-rio-timestamp | RIO 时间戳 |
| x-rio-signature | RIO 签名 |
| x-rio-nonce | RIO 随机数 |
| x-tai-identity | TAI 身份标识 |

**返回：**
```json
{
  "success": true,
  "msg": "导入成功",
  "data": [
    {
      "status": "finish",
      "task_id": "123456"
    }
  ]
}
```

**错误返回：**
```json
{
  "success": false,
  "msg": "错误信息"
}
```

**内部流程：**
1. 获取预签名 URL（`GetImportPresign`）
2. 上传文件到 COS 对象存储（`UploadImportFile`）
3. 启动导入任务（`StartImport`）
4. 轮询等待导入完成（最多 60 次，间隔 3 秒）

**限制：**
- 文件大小不超过 50MB
- 不支持审批流程文档的导入

**Python 客户端调用示例：**
```python
client = MCPClient()
result = client.upload_file(
    file_path="./doc.md",
    parent_id=4017403457,
    task_type="md_import",
    cover=True,
)
```

**命令行调用示例：**
```bash
# 上传 Markdown 文件到指定父目录
python connect_mcp.py upload ./doc.md 4017403457

# 指定任务类型
python connect_mcp.py upload ./doc.docx 4017403457 --task-type md_import

# 不覆盖同名文档
python connect_mcp.py upload ./doc.md 4017403457 --no-cover
```
