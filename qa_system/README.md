# 智能质量保证系统 v3.0

一个整合需求、测试用例、BUG 的智能质量保证系统，通过数据分析和 AI 技术提升软件测试质量和效率。

**v3.0 更新**：采用文件驱动的数据管理，支持 Markdown 需求文档和 YAML 测试用例/BUG 文件，按模块组织数据。

## 🎯 核心功能

### 1. 质量分析与预测
- **缺陷密度分析**：识别用例多+BUG多的高风险区域
- **需求覆盖率**：对比需求 vs 用例 vs BUG，找出未被测试的需求
- **BUG 趋势预测**：基于历史数据训练模型，预测新版本可能出现的 BUG

### 2. AI 辅助测试
- **智能用例生成**：根据需求文档自动生成测试用例
- **BUG 根因分析**：新 BUG 出现时，AI 比对历史，推荐可能原因
- **用例推荐**：输入修改的代码文件，推荐需要回归的用例

### 3. 流程优化
- **需求变更影响分析**：改需求时，关联哪些用例和 BUG 需要更新
- **测试优先级排序**：历史 BUG 多的用例，每次优先执行
- **资源分配**：识别低效用例（从未发现过 BUG），优化测试集

### 4. 知识管理
- **新人培训**：整合文档，AI 问答，快速了解系统
- **经验沉淀**：历史 BUG + 修复方案，避免重复踩坑
- **智能搜索**：自然语言搜索，返回需求+用例+BUG 全链路信息

### 5. 智能报告
- **项目质量报告**：自动生成综合质量评估报告
- **模块质量报告**：各模块独立质量分析

## 📁 项目结构

```
qa_system/
├── main.py                      # FastAPI 主入口
├── requirements.txt             # Python 依赖
├── start.sh                     # Linux/Mac 启动脚本
├── start.bat                    # Windows 启动脚本
├── data/
│   ├── __init__.py
│   ├── file_provider.py         # 文件数据提供者（解析器）
│   ├── requirements/            # 需求文档（Markdown）
│   │   ├── 用户管理/
│   │   │   ├── REQ-001_用户登录功能.md
│   │   │   └── REQ-002_用户注册功能.md
│   │   └── 订单管理/
│   │       └── REQ-004_订单创建功能.md
│   ├── testcases/               # 测试用例（YAML + 索引）
│   │   ├── 用户管理/
│   │   │   ├── TC-001_手机号验证码正常流程.yaml
│   │   │   └── testcase_index.json
│   │   └── 订单管理/
│   │       └── testcase_index.json
│   └── bugs/                    # BUG 数据（YAML + 索引）
│       ├── 用户管理/
│       │   ├── BUG-001_登录锁定机制未生效.yaml
│       │   └── bug_index.json
│       └── 订单管理/
│           └── bug_index.json
├── modules/
│   ├── __init__.py
│   ├── models.py               # 数据模型定义
│   ├── quality_analysis.py     # 质量分析与预测模块
│   ├── ai_assisted_testing.py  # AI 辅助测试模块
│   ├── process_optimization.py # 流程优化模块
│   ├── knowledge_management.py # 知识管理模块
│   └── smart_report.py         # 智能报告模块
├── mcp_tools/
│   ├── __init__.py
│   └── qa_tools.py             # MCP 工具服务（供 LLM 调用）
├── api/                        # API 路由（预留）
├── config/                     # 配置文件（预留）
└── utils/                      # 工具函数（预留）
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- pip

### 安装与启动

#### 方式一：使用启动脚本（推荐）

**Mac/Linux:**
```bash
cd qa_system
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
cd qa_system
start.bat
```

#### 方式二：手动安装

```bash
# 1. 进入项目目录
cd qa_system

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动服务
python main.py
```

### 访问服务

服务启动后，访问以下地址：

- **API 文档（Swagger UI）**: http://localhost:8000/docs
- **API 文档（ReDoc）**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 📖 API 接口说明

### 数据查询

| 接口 | 说明 | 参数 |
|------|------|------|
| `GET /api/data/requirements` | 获取需求列表 | `module` (可选) |
| `GET /api/data/test-cases` | 获取测试用例列表 | `module`, `requirement_id` (可选) |
| `GET /api/data/bugs` | 获取BUG列表 | `module`, `status` (可选) |
| `GET /api/data/modules` | 获取模块列表 | - |
| `GET /api/data/statistics` | 获取数据统计信息 | - |

### 质量分析

| 接口 | 说明 |
|------|------|
| `GET /api/quality/analysis` | 综合分析质量 |
| `GET /api/quality/bug-trend` | BUG趋势预测 |
| `GET /api/quality/bug-prediction` | 模块BUG预测 |

### AI 辅助测试

| 接口 | 说明 | 参数 |
|------|------|------|
| `GET /api/ai/generate-test-cases` | 生成测试用例 | `requirement_id` |
| `GET /api/ai/bug-analysis` | BUG根因分析 | `bug_id` |
| `GET /api/ai/recommend-test-cases` | 推荐测试用例 | `code_files`, `module` |
| `POST /api/ai/assisted-test` | AI辅助测试（综合） | 多种参数可选 |

### 流程优化

| 接口 | 说明 | 参数 |
|------|------|------|
| `GET /api/process/change-impact` | 需求变更影响分析 | `requirement_id` |
| `GET /api/process/prioritize-test-cases` | 测试优先级排序 | `limit` |
| `GET /api/process/inefficient-test-cases` | 低效用例识别 | - |
| `GET /api/process/optimization` | 流程优化（综合） | `requirement_id` (可选) |

### 知识管理

| 接口 | 说明 | 参数 |
|------|------|------|
| `GET /api/knowledge/training` | 培训材料 | - |
| `GET /api/knowledge/historical-bugs` | 历史BUG案例 | `limit` |
| `GET /api/knowledge/search` | 智能搜索 | `query` |
| `GET /api/knowledge/qa` | 常见问答 | - |

### 智能报告

| 接口 | 说明 | 参数 |
|------|------|------|
| `GET /api/report/project` | 项目质量报告 | - |
| `GET /api/report/module` | 模块质量报告 | `module` |
| `GET /api/report/all-modules` | 所有模块报告 | - |

## 🔌 MCP 工具服务

系统提供 MCP Server 服务，供 LLM 调用获取质量保障系统数据。

### 启动 MCP Server

```bash
python -m mcp_tools.qa_tools
```

### 可用工具

| 工具名 | 说明 |
|--------|------|
| `list_modules` | 获取所有模块列表 |
| `get_data_statistics` | 获取数据统计信息 |
| `get_all_requirements` | 获取所有需求数据 |
| `get_all_test_cases` | 获取所有测试用例数据 |
| `get_all_bugs` | 获取所有BUG数据 |
| `get_requirements_by_module` | 根据模块获取需求 |
| `get_test_cases_by_module` | 根据模块获取测试用例 |
| `get_bugs_by_module` | 根据模块获取BUG |
| `get_test_cases_by_requirement` | 根据需求ID获取测试用例 |
| `get_bugs_by_test_case` | 根据测试用例ID获取BUG |
| `get_bugs_by_requirement` | 根据需求ID获取BUG |
| `get_module_overview` | **获取模块完整概览（管理后台核心）** |

## 📝 数据管理

### 添加需求

在 `data/requirements/模块名/` 目录下创建 Markdown 文件：

```markdown
# REQ-006: 新功能名称

## 基本信息
- **模块**: 模块名
- **优先级**: 高/中/低
- **状态**: 已完成/进行中/未开始
- **创建时间**: 2026-04-10
- **更新时间**: 2026-04-10

## 需求描述
功能描述...

## 功能点
1. 功能点1
2. 功能点2

## 标签
标签1、标签2

## 变更历史
| 日期 | 操作 | 说明 |
|------|------|------|
| 2026-04-10 | 创建 | 初始版本 |
```

### 添加测试用例

1. 在 `data/testcases/模块名/` 目录下创建 YAML 文件：

```yaml
id: TC-007
title: 测试用例标题
description: 测试用例描述
requirement_id: REQ-006
module: 模块名
priority: 高
status: 已执行
case_type: 基本功能
steps:
  - "步骤1: ..."
  - "步骤2: ..."
expected_result: 期望结果
actual_result: 实际结果
bugs_found: []
execution_count: 0
last_executed_at: null
created_at: "2026-04-10T10:00:00"
updated_at: "2026-04-10T10:00:00"
```

2. 更新 `testcase_index.json` 添加索引条目

### 添加BUG

1. 在 `data/bugs/模块名/` 目录下创建 YAML 文件：

```yaml
id: BUG-005
title: BUG标题
description: BUG描述
test_case_id: TC-007
requirement_id: REQ-006
module: 模块名
severity: 严重/一般/轻微
status: 已修复/修复中/未修复
root_cause: 根因分析
root_cause_category: 编码错误/设计缺陷/需求理解偏差
fix_solution: 修复方案
fixed_in_version: v1.0.1
assignee: 指派人
reporter: 报告人
created_at: "2026-04-10T10:00:00"
updated_at: "2026-04-10T10:00:00"
fixed_at: "2026-04-10T15:00:00"
```

2. 更新 `bug_index.json` 添加索引条目

## 💡 使用示例

### 1. 查看项目质量报告

```bash
curl http://localhost:8000/api/report/project | jq .
```

### 2. 分析特定BUG的根因

```bash
curl "http://localhost:8000/api/ai/bug-analysis?bug_id=BUG-001" | jq .
```

### 3. 根据代码变更推荐测试用例

```bash
curl "http://localhost:8000/api/ai/recommend-test-cases?code_files=user.py,order.py" | jq .
```

### 4. 搜索知识库

```bash
curl "http://localhost:8000/api/knowledge/search?query=用户登录" | jq .
```

## 🎨 核心设计亮点

### 1. 文件驱动的数据管理
- 使用 Markdown 管理需求文档（可读、可版本控制）
- 使用 YAML 管理测试用例和 BUG（结构化、易编辑）
- 使用 JSON 索引文件实现快速查询和关联

### 2. 按模块组织
- 数据按模块分目录，清晰隔离
- 支持管理后台按模块展示完整概览
- 需求、测试用例、BUG 通过 ID 关联，形成完整链路

### 3. 模块化架构
- 清晰的模块划分，每个模块职责单一
- 易于扩展和维护

### 4. 统一的数据模型
- 使用 Pydantic 定义严格的数据模型
- 支持 JSON 模式输出，方便 API 序列化

### 5. MCP 集成
- 提供 MCP 工具服务供 LLM 调用
- 支持 AI 智能体与质量系统交互

### 6. 智能算法
- 使用 scikit-learn 进行 BUG 趋势预测
- 基于统计分析的质量评估

## 🔄 后续扩展

- [ ] 接入真实数据库（MySQL/PostgreSQL）
- [ ] 集成 CI/CD 系统
- [ ] 支持更多 AI 模型（OpenAI、Claude 等）
- [ ] 前端界面开发
- [ ] 测试覆盖率可视化
- [ ] 自动化测试集成

## 📝 开发约定

### 代码风格
- 遵循 PEP 8 规范
- 使用类型注解
- 函数和类都要有文档字符串

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构代码
test: 测试相关
chore: 构建/辅助工具
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
