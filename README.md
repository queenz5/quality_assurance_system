# 智能质量保障系统 (Intelligent QA System)

> 基于 AI/ML 的全链路智能质量保障平台，覆盖需求管理、测试用例、缺陷追踪全流程

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

智能质量保障系统是一个整合**需求管理**、**测试用例管理**、**缺陷追踪**的全链路质量保障平台。通过集成 **LLM**、**RAG 检索**、**机器学习预测**等 AI/ML 技术，实现需求智能解析、测试用例自动生成、BUG 根因分析、质量趋势预测、知识管理和智能报告生成，全面提升软件质量保障效率。

### 核心亮点

- 🤖 **AI 驱动**: LangChain + LLM实现需求智能解析、用例自动生成、影响分析
- 🔍 **RAG 混合检索**: FAISS 向量检索 + BM25 关键词检索，支持全链路语义检索
- 📊 **ML 预测**: scikit-learn 线性回归模型实现 BUG 趋势预测与置信区间分析
- 🔗 **MCP 协议集成**: 12 个 MCP 工具供 LLM 直接调用 QA 系统数据
- 🎯 **智能评分**: 多维度质量评分算法 (覆盖率 + 缺陷密度 + 风险控制 + 修复率 + 执行率)
- 📝 **结构化需求**: 从非结构化 PRD 自动提取模块、功能点、业务规则等

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│   Web 前端 (React 19 + Material-UI)    LLM 代理 (MCP)       │
└──────────────────────┬──────────────────────┬────────────────┘
                       │ HTTP/REST            │ MCP Protocol
                       ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 服务层                          │
│                25+ RESTful API 端点                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     业务逻辑层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │需求分析  │ │质量分析  │ │AI辅助测试│ │知识管理  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐                                  │
│  │RAG检索   │ │智能报告  │                                  │
│  └──────────┘ └──────────┘                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     数据访问层                               │
│              FileDataProvider (Markdown + YAML + JSON)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| **FastAPI** 0.109+ | 高性能异步 Web 框架，自动 OpenAPI/Swagger 文档 |
| **Pydantic** 2.5+ | 数据验证与序列化 (30+ 数据模型) |
| **LangChain** 1.2+ | LLM 应用框架，编排需求解析、影响分析等 AI 流程 |
| **LLM ** | LLM 推理引擎 (qwen-turbo)，兼容 OpenAI 接口 |
| **scikit-learn** 1.3+ | 机器学习 — LinearRegression 用于 BUG 趋势预测 |
| **FAISS** 1.7+ | Facebook 向量检索库，语义相似度检索 |
| **BM25 / rank_bm25** | 关键词检索，与 FAISS 构成混合检索 |
| **MCP** 0.9+ | Model Context Protocol，12 个可调用的 QA 工具 |
| **NumPy / Pandas** | 数值计算与统计分析 |

### 前端

| 技术 | 用途 |
|------|------|
| **React** 19 | UI 框架 |
| **Vite** 8 | 构建工具 |
| **Material-UI** 9 | 组件库与设计系统 |
| **React Router** 7 | 客户端路由 |
| **Recharts** 3 | 数据可视化图表 |
| **@uiw/react-md-editor** | Markdown 编辑器 (需求草稿在线编辑) |
| **Axios** | HTTP 客户端 |

---

## 📦 核心模块

### 1. 需求智能分析
- **非结构化需求 → 结构化需求**: LLM 自动解析原始需求文档，提取模块、功能点、业务规则、前置/后置条件、异常处理、依赖关系
- **质量问题检测**: 自动检测 6 类问题（缺失信息、模糊描述、矛盾冲突、不完整、优先级不合理、缺少前置条件/异常处理），按严重/一般/轻微分级
- **草稿版本管理**: 支持多版本历史、在线 Markdown 编辑、一键发布为正式文档

### 2. 质量分析与预测
- **缺陷密度计算**: 缺陷密度 = BUG 数 / 测试用例数，按模块统计
- **需求覆盖率分析**: 有测试用例覆盖的需求占比
- **高风险模块识别**: 多维度风险评分（缺陷密度 + 覆盖率 + 历史趋势）
- **BUG 趋势预测**: sklearn LinearRegression 模型，预测未来 7 天 BUG 趋势并提供置信区间
- **模块 BUG 预测**: 按模块预测新增 BUG 数量，识别风险因素

### 3. AI 辅助测试
- **智能用例生成**: 根据需求自动生成测试用例（LLM 驱动）
- **BUG 根因分析**: 基于历史 BUG 数据，统计根因分布、计算 Jaccard 相似度推荐相似 BUG，生成修复建议与置信度
- **代码变更推荐回归测试**: 综合历史 BUG 数(权重×3)、优先级、执行状态、时间衰减四维度评分推荐回归用例
- **新需求影响分析**: RAG 检索 + LLM 分析，自动识别受影响的历史需求、推荐回归测试用例、生成风险等级

### 4. RAG 混合检索
- **BM25 + FAISS 双引擎检索**: 关键词检索 + 语义向量检索
- **RRF 融合去重**: 多源结果融合排序
- **全链路检索**: 需求、测试用例、BUG 三类文档统一索引
- **LLM 上下文生成**: 自动格式化检索结果为 LLM 可用的 Prompt 上下文

### 5. 知识管理
- **新人培训材料**: 按模块自动生成培训材料（需求摘要、用例摘要、常见 BUG、最佳实践）
- **历史 BUG 案例库**: 按严重程度排序，自动生成经验教训
- **智能搜索**: 自然语言关键词搜索，跨需求/用例/BUG 全链路检索
- **问答对生成**: 基于统计数据自动生成常见 QA 对

### 6. 智能报告
- **项目质量报告**: 多维度质量评分（覆盖率 25 分 + 缺陷密度 25 分 + 高风险 20 分 + BUG 修复率 15 分 + 测试执行率 15 分 = 满分 100）
- **模块质量报告**: 按模块生成质量评分、风险评估、改进建议
- **执行摘要**: 自动根据分数生成文字版质量评估

### 7. MCP 工具服务
- **12 个 MCP 工具**: `list_modules`, `get_data_statistics`, `get_all_requirements`, `get_all_test_cases`, `get_all_bugs` 等
- 使 LLM 代理可直接调用 QA 系统数据，实现 AI 驱动的质量管理

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 安装

#### 1. 克隆项目

```bash
git clone <repository-url>
cd quality_assurance_system
```

#### 2. 启动后端

```bash
cd qa_system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 启动服务
python main.py
# 或使用脚本: ./start.sh
```

后端服务启动后访问: http://localhost:8000/docs 查看 API 文档

#### 3. 启动前端 (新终端)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 或使用脚本: ./start.sh
```

前端应用启动后访问: http://localhost:3000

### 环境变量配置

在 `qa_system/.env` 文件中配置:

```env
# LLM API 配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL_NAME=qwen-turbo

# 可选
OPENAI_TEMPERATURE=0.1
EMBEDDING_MODEL_NAME=text-embedding-v3
```

---

## 📊 功能页面

| 页面 | 路径 | 核心功能 |
|------|------|----------|
| 仪表盘 | `/dashboard` | 统计卡片、质量指标可视化、模块对比、BUG 趋势 |
| 需求分析 | `/requirement-analysis` | 三步流程：上传/输入 → AI 解析预览 → 确认保存/发布 |
| 质量分析 | `/quality` | 缺陷密度/覆盖率分析、高风险模块识别、趋势预测 |
| AI 测试 | `/ai-testing` | 用例生成、BUG 根因分析、代码变更推荐测试 |
| 知识管理 | `/knowledge` | 智能搜索、培训材料、历史 BUG 案例、QA 问答 |
| 智能报告 | `/report` | 项目质量报告、模块报告、执行摘要 |

---

## 📁 项目结构

```
quality_assurance_system/
├── qa_system/                  # 后端服务
│   ├── main.py                 # FastAPI 入口 (25+ API 端点)
│   ├── modules/                # 业务模块
│   │   ├── models.py           # 30+ Pydantic 数据模型
│   │   ├── requirement_parser.py       # 需求解析器
│   │   ├── requirement_analysis_service.py  # 需求分析服务
│   │   ├── markdown_analysis_service.py   # Markdown 结构化服务
│   │   ├── quality_analysis.py         # 质量分析与 ML 预测
│   │   ├── ai_assisted_testing.py      # AI 辅助测试
│   │   ├── rag_retriever.py            # RAG 混合检索
│   │   ├── knowledge_management.py     # 知识管理
│   │   ├── smart_report.py             # 智能报告
│   │   ├── test_case_generator.py      # 测试用例生成
│   │   ├── test_case_generation_service.py
│   │   └── index_manager.py            # 索引管理
│   ├── data/                   # 数据存储
│   │   ├── file_provider.py    # 文件数据提供者
│   │   ├── requirements/       # 需求文档 (Markdown)
│   │   ├── testcases/          # 测试用例 (YAML)
│   │   └── bugs/               # 缺陷记录 (YAML)
│   ├── mcp_tools/              # MCP 工具服务
│   │   └── qa_tools.py         # 12 个 MCP 工具
│   ├── demo.py                 # 功能演示
│   ├── requirements.txt        # Python 依赖
│   ├── start.sh                # 启动脚本
│   └── .env                    # 环境变量
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── pages/              # 页面组件 (7 个页面)
│   │   ├── components/         # 公共组件
│   │   ├── services/           # API 服务
│   │   └── App.jsx             # 应用入口
│   ├── package.json
│   └── vite.config.js
│
├── skills/                     # AI Skill 定义
│   └── prd-to-structured-requirements/
│       ├── SKILL.md            # 需求结构化 Prompt
│       └── references/         # 格式参考
│
├── .gitignore                  # Git 忽略规则
└── README.md                   # 项目说明 (本文件)
```

---

## 📈 项目数据

| 指标 | 数量 |
|------|------|
| 后端代码 | ~7,200 行 Python |
| 数据模型 | 30+ Pydantic 模型 |
| REST API | 25+ 端点 |
| MCP 工具 | 12 个 |
| 前端页面 | 7 个 React 组件 |
| Mock 数据 | 5 模块 / 20+ 需求 / 83 用例 / 39 BUG |

---

## 🎯 使用场景

### 测试团队
1. 每日查看质量仪表盘了解整体质量
2. 使用 AI 生成测试用例提升效率
3. 利用优先级排序指导测试执行
4. 查看智能报告了解项目状态

### 开发团队
1. 代码变更后查看推荐回归测试
2. 分析 BUG 根因加速缺陷修复
3. 查看需求变更影响评估修改范围
4. 搜索历史 BUG避免重复问题

### 管理团队
1. 查看项目质量报告掌握质量趋势
2. 关注高风险模块及时调配资源
3. 根据趋势预测合理规划迭代
4. 利用知识管理培训新人

---

## 🌐 部署

### 开发环境

```bash
# 后端
cd qa_system && ./start.sh

# 前端
cd frontend && ./start.sh
```

### 生产环境

```bash
# 后端 - 使用 uvicorn 部署
cd qa_system
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 前端 - 构建静态文件
cd frontend
npm run build

# 使用 Nginx 部署 dist 目录
# nginx.conf 示例:
# server {
#     listen 80;
#     location / {
#         root /path/to/frontend/dist;
#         try_files $uri $uri/ /index.html;
#     }
#     location /api {
#         proxy_pass http://localhost:8000;
#     }
# }
```

---

## 🔮 后续规划

- [ ] 用户认证和授权 (JWT / OAuth)
- [ ] 真实数据库集成 (PostgreSQL / MySQL)
- [ ] 实时通知系统 (WebSocket)
- [ ] 数据导出 (Excel / PDF)
- [ ] 国际化支持 (i18n)
- [ ] 深色主题
- [ ] 移动端适配
- [ ] CI/CD 集成

---

## 📄 许可证

[MIT License](LICENSE)

---

## 📚 相关文档

- [架构设计文档](qa_system/ARCHITECTURE.md)
- [快速启动指南](qa_system/QUICKSTART.md)
- [需求解析器使用指南](qa_system/REQUIREMENT_PARSER_GUIDE.md)
- [前端需求分析指南](frontend/REQUIREMENT_ANALYSIS_GUIDE.md)
- [需求格式标准](REQUIREMENT_FORMAT_STANDARD.md)
- [Skill 集成说明](SKILL_INTEGRATION.md)

---

## 🤝 支持

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**开始使用**:

```bash
# 1. 启动后端
cd qa_system && ./start.sh

# 2. 启动前端 (新终端)
cd frontend && ./start.sh

# 3. 访问应用
# 前端: http://localhost:3000
# API文档: http://localhost:8000/docs
```

祝使用愉快！🚀
