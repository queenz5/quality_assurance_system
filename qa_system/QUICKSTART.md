# 快速启动指南 v3.0

## 📦 5分钟快速开始

### 1️⃣ 安装依赖

```bash
cd qa_system

# Mac/Linux
chmod +x start.sh
./start.sh

# Windows
start.bat
```

### 2️⃣ 访问 API 文档

服务启动后，打开浏览器访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3️⃣ 运行演示脚本

在另一个终端窗口：

```bash
cd qa_system
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows

python demo.py
```

### 4️⃣ 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 获取模块列表
curl http://localhost:8000/api/data/modules | jq .

# 获取模块概览
curl http://localhost:8000/api/data/modules/用户管理/overview | jq .

# 质量分析
curl http://localhost:8000/api/quality/analysis | jq .

# 项目质量报告
curl http://localhost:8000/api/report/project | jq .
```

## 🎯 常用场景

### 场景1：查看模块列表

```bash
curl http://localhost:8000/api/data/modules | jq .
```

### 场景2：查看模块完整概览（管理后台核心）

```bash
curl http://localhost:8000/api/data/modules/用户管理/overview | jq '{
  module: .module,
  summary: .summary,
  requirements_count: (.requirements | length)
}'
```

### 场景3：分析特定模块质量

```bash
curl "http://localhost:8000/api/report/module?module=用户管理" | jq .
```

### 场景4：根据需求生成测试用例

```bash
curl "http://localhost:8000/api/ai/generate-test-cases?requirement_id=REQ-001" | jq .
```

### 场景5：分析BUG根因

```bash
curl "http://localhost:8000/api/ai/bug-analysis?bug_id=BUG-001" | jq .
```

### 场景6：代码变更后推荐测试用例

```bash
curl "http://localhost:8000/api/ai/recommend-test-cases?code_files=user.py,auth.py" | jq .
```

### 场景7：需求变更影响分析

```bash
curl "http://localhost:8000/api/process/change-impact?requirement_id=REQ-001" | jq .
```

### 场景8：搜索知识库

```bash
curl "http://localhost:8000/api/knowledge/search?query=用户登录" | jq .
```

## 📂 数据文件说明

系统采用文件管理数据，示例数据位于 `data/` 目录：

### 当前示例数据

- **2个模块**: 用户管理、订单管理
- **5个需求**: Markdown 文档，位于 `data/requirements/`
- **6个测试用例**: YAML 文件，位于 `data/testcases/`
- **4个BUG**: YAML 文件，位于 `data/bugs/`

### 文件结构

```
data/
├── requirements/模块名/REQ-*.md    # 需求文档
├── testcases/模块名/TC-*.yaml      # 测试用例
├── testcases/模块名/testcase_index.json  # 测试用例索引
├── bugs/模块名/BUG-*.yaml          # BUG 数据
└── bugs/模块名/bug_index.json      # BUG 索引
```

### 如何添加新数据

**添加需求**: 在 `data/requirements/模块名/` 下创建 Markdown 文件，按现有格式编写。

**添加测试用例**: 
1. 在 `data/testcases/模块名/` 下创建 YAML 文件
2. 更新 `testcase_index.json` 添加索引条目

**添加BUG**: 
1. 在 `data/bugs/模块名/` 下创建 YAML 文件
2. 更新 `bug_index.json` 添加索引条目

详见 [README.md](README.md#-数据管理) 中的详细格式说明。

## 🔌 MCP 工具服务

如需使用 MCP 功能：

```bash
cd qa_system
source venv/bin/activate
python -c "from mcp_tools.qa_tools import server; server.run()"
```

或在代码中导入：

```python
from mcp_tools.qa_tools import server

# 查看所有工具
print(server._tool_manager._tools.keys())

# 调用工具
import asyncio
async def use_tools():
    # 获取模块列表
    modules = await server._tool_manager.call_tool("list_modules", {})
    print(modules)
    
    # 获取模块概览
    overview = await server._tool_manager.call_tool("get_module_overview", {"module": "用户管理"})
    print(overview)

asyncio.run(use_tools())
```

## 🛠️ 开发模式

```bash
# 启动开发服务器（自动重载）
python main.py

# 或直接使用 uvicorn
uvicorn main:app --reload --port 8000
```

## 📝 查看 API 文档

启动服务后访问：
- http://localhost:8000/docs - Swagger UI（可交互）
- http://localhost:8000/redoc - ReDoc（只读）

## ❓ 常见问题

**Q: 端口被占用怎么办？**

A: 修改 `main.py` 最后一行的端口号：
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

**Q: 如何替换为数据库（MySQL/PostgreSQL）？**

A: 创建新的数据提供者类（如 `DatabaseDataProvider`），实现与 `FileDataProvider` 相同的接口，然后在 `data/__init__.py` 中替换默认实现。文件数据可以定期同步到数据库。

**Q: 如何添加新功能？**

A: 在 `modules/` 下创建新模块，然后在 `main.py` 中添加路由。

**Q: 如何添加新模块的数据？**

A: 
1. 在 `data/requirements/新模块名/` 下创建需求 Markdown 文件
2. 在 `data/testcases/新模块名/` 下创建测试用例 YAML 文件和 `testcase_index.json`
3. 在 `data/bugs/新模块名/` 下创建 BUG YAML 文件和 `bug_index.json`
4. 系统会自动识别新模块

## 🎉 开始使用

现在你已经了解了基础知识，开始探索智能质量保证系统吧！
