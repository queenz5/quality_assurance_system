# 需求拆解流程使用指南

## 📋 功能说明

需求拆解模块用于将原始 PRD/需求文档自动拆解为结构化的需求数据，包括：
- 功能模块识别
- 功能点提取
- 业务规则分析
- 前置/后置条件
- 异常处理
- 需求依赖关系

## 🚀 使用方式

### 方式 1：通过 API 接口

#### 1.1 分析需求并创建草稿

**API 端点**: `POST /api/requirements/analyze-and-create-draft`

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/requirements/analyze-and-create-draft \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# 用户需求\n\n用户可以通过手机号登录...",
    "source_name": "用户需求文档"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "draft_id": "draft-12345",
  "source_name": "用户需求文档",
  "analysis_summary": "成功解析 3 个模块，8 个功能点",
  "total_issues": 0,
  "critical_issues": 0,
  "major_issues": 0,
  "minor_issues": 0,
  "total_modules": 3,
  "total_function_points": 8,
  "total_requirements": 5,
  "issues": [],
  "requirements": [
    {
      "id": "REQ-001",
      "title": "用户登录功能",
      "module": "用户管理",
      "sub_module": "登录",
      "priority": "高",
      "description": "用户登录功能描述",
      "function_points_count": 3,
      "function_points": [],
      "preconditions": [],
      "postconditions": [],
      "business_rules": [],
      "exception_handling": [],
      "prerequisite_requirements": [],
      "dependent_requirements": [],
      "tags": []
    }
  ]
}
```

#### 1.2 获取草稿列表

**API 端点**: `GET /api/requirements/drafts`

**响应示例**:
```json
{
  "success": true,
  "total": 1,
  "drafts": [
    {
      "draft_id": "draft-12345",
      "source_name": "用户需求文档",
      "created_at": "2026-04-15T10:00:00",
      "updated_at": "2026-04-15T10:00:00",
      "total_requirements": 5
    }
  ]
}
```

#### 1.3 发布草稿为正式文档

**API 端点**: `POST /api/requirements/draft/{draft_id}/publish`

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/requirements/draft/draft-12345/publish \
  -H "Content-Type: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "草稿已发布为正式文档,共保存 5 个文件",
  "saved_files": [
    "/path/to/requirements/用户管理/REQ-001_用户登录功能.md"
  ]
}
```

#### 1.4 获取正式需求列表

**API 端点**: `GET /api/requirements/formal`

**响应示例**:
```json
{
  "success": true,
  "total": 5,
  "modules": ["用户管理", "订单管理"],
  "requirements": [
    {
      "file_name": "REQ-001_用户登录功能.md",
      "title": "用户登录功能",
      "module": "用户管理",
      "path": "/path/to/requirements/用户管理/REQ-001_用户登录功能.md",
      "updated_at": "2026-04-15T10:00:00",
      "size_kb": 1.2
    }
  ]
}
```

### 方式 2：通过 Python 代码

```python
from modules.requirement_analysis_service import RequirementAnalysisService

# 创建服务实例
service = RequirementAnalysisService(data_dir="/path/to/data")

# 分析和解析需求
content = "# 用户需求\n\n用户可以通过手机号登录..."
source_name = "用户需求文档"

analysis_result = service.analyze_and_parse(content, source_name)

print(f"解析了 {analysis_result.total_modules} 个模块")
print(f"识别了 {analysis_result.total_function_points} 个功能点")
print(f"生成了 {len(analysis_result.parsed_requirements)} 个需求")

# 创建草稿
draft_id = service.create_draft(analysis_result, source_name, "AI自动解析生成")
print(f"草稿创建成功: {draft_id}")

# 发布为正式文档
success, saved_files = service.publish_to_formal(draft_id)
print(f"发布成功: {len(saved_files)} 个文件")
```

## 📂 输出格式

### 目录结构

```
qa_system/data/requirements/
├── _index.json                    # 全局需求索引
├── TEMPLATE.md                    # 需求模板
├── 用户管理/
│   ├── REQ-001_用户登录功能.md
│   └── REQ-002_用户注册功能.md
└── 订单管理/
    └── REQ-003_订单创建功能.md
```

### 需求文件格式

每个需求保存为独立的 Markdown 文件，包含：
- 基本信息（模块、优先级、状态）
- 需求描述
- 功能点列表（含业务规则、约束）
- 前置/后置条件
- 业务规则表
- 异常处理
- 标签
- 依赖关系
- 变更历史

## 🎯 完整工作流

```
1. 准备原始 PRD
   ↓
   skills/prd-to-xmind-testcases/requirements/
   └── 产品需求说明书.pdf

2. 调用 API 解析需求
   ↓
   POST /api/requirements/parse-from-file
   {
     "file_path": "/path/to/prd.pdf",
     "save_to_data": true
   }

3. 查看解析结果
   ↓
   qa_system/data/requirements/
   ├── _index.json
   ├── 用户管理/
   │   ├── REQ-001_用户登录功能.md
   │   └── REQ-002_用户注册功能.md
   └── 订单管理/
       └── REQ-003_订单创建功能.md

4. 人工审核和调整
   ↓
   检查生成的需求文件，补充遗漏内容

5. 进入下一阶段：生成测试用例
   ↓
   （等待实现）
```

## ⚙️ 配置说明

### LLM 配置

需求解析依赖 LLM，需要在 `.env` 文件中配置：

```env
LLM_API_KEY=your_api_key
LLM_MODEL=qwen-turbo
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_TEMPERATURE=0.7
```

### 支持的文件格式

- **Markdown** (`.md`) - 推荐
- **纯文本** (`.txt`)
- **PDF** (`.pdf`) - 需要安装 `PyPDF2` 或 `pdfplumber`
- **Word** (`.docx`) - 需要安装 `python-docx`

安装依赖：
```bash
pip install PyPDF2 python-docx
```

## 📝 注意事项

1. **需求 ID 唯一性**：AI 会自动分配 REQ-XXX 编号，如需调整请手动修改
2. **内容长度限制**：当前限制输入 8000 字符，超长 PRD 建议分段解析
3. **质量检查**：AI 解析后建议人工审核，特别是：
   - 功能点是否完整
   - 业务规则是否准确
   - 依赖关系是否合理
4. **增量更新**：多次解析同一 PRD 会覆盖已有文件，注意备份

## 🔧 故障排除

### 问题 1：LLM 调用失败
- 检查 `.env` 配置是否正确
- 检查网络连接
- 查看 API Key 是否有效

### 问题 2：PDF 解析失败
- 安装依赖：`pip install PyPDF2`
- 如果仍失败，尝试导出为 Markdown 后解析

### 问题 3：JSON 解析失败
- AI 返回格式可能不标准
- 查看 warnings 字段了解具体问题
- 可尝试调整 Prompt 或更换 LLM 模型

## 📚 相关文档

- [需求模板](data/requirements/TEMPLATE.md)
- [格式规范](../FORMAT_SPECIFICATION.md)
- [API 文档](http://localhost:8000/docs) - 启动服务器后访问
