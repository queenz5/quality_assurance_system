# 架构设计文档 v3.0

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     客户端层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Web 前端  │  │  CLI工具  │  │  LLM代理 │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼─────────────┼─────────────┼─────────────────────┘
        │             │             │
        │ HTTP/REST   │ HTTP/REST   │ MCP Protocol
┌───────┼─────────────┼─────────────┼─────────────────────┐
│       │             │             │      服务层           │
│  ┌────┴─────────────┴─────────────┴──────────────────┐  │
│  │              FastAPI 应用服务                       │  │
│  │  ┌──────────────────────────────────────────┐    │  │
│  │  │           API Router Layer               │    │  │
│  │  │  /api/data/*    - 数据查询                │    │  │
│  │  │  /api/requirements/* - 需求管理           │    │  │
│  │  │  /api/testcases/* - 测试用例管理          │    │  │
│  │  │  /api/quality/* - 质量分析                │    │  │
│  │  │  /api/ai/*      - AI辅助测试              │    │  │
│  │  │  /api/knowledge/* - 知识管理              │    │  │
│  │  │  /api/report/*  - 智能报告                │    │  │
│  │  └──────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
        │             │             │
┌───────┼─────────────┼─────────────┼─────────────────────┐
│       │             │             │      业务逻辑层       │
│  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────────────┐       │
│  │  quality  │ │   ai_    │ │ requirement_     │       │
│  │ _analysis │ │ assisted │ │ analysis_service│       │
│  │          │ │ _testing │ │                  │       │
│  └──────────┘ └──────────┘ └──────────────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐       │
│  │knowledge │ │  smart   │ │ markdown_analysis│       │
│  │_management│ │ _report  │ │ _service         │       │
│  │          │ │          │ │                  │       │
│  └──────────┘ └──────────┘ └──────────────────┘       │
└─────────────────────────────────────────────────────────┘
        │             │             │
┌───────┼─────────────┼─────────────┼─────────────────────┐
│       │             │             │      数据访问层       │
│  ┌────┴─────────────┴─────────────┴──────────────────┐  │
│  │          FileDataProvider                          │  │
│  │  - Markdown 需求文档解析                            │  │
│  │  - YAML 测试用例解析                                │  │
│  │  - YAML BUG 解析                                    │  │
│  │  - JSON 索引加载                                    │  │
│  │  - 模块概览查询                                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
        │
┌───────┼─────────────────────────────────────────────────┐
│  ┌────┴──────────────────────────────────────────────┐  │
│  │              文件存储                               │  │
│  │  data/requirements/模块/REQ-*.md                   │  │
│  │  data/testcases/模块/TC-*.yaml + index.json        │  │
│  │  data/bugs/模块/BUG-*.yaml + index.json            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  MCP Tools (独立服务)                     │
│  提供工具供 LLM 调用:                                     │
│  - list_modules                                         │
│  - get_module_overview (管理后台核心)                    │
│  - get_all_requirements                                 │
│  - get_all_test_cases                                   │
│  - get_all_bugs                                         │
│  - ...                                                  │
└─────────────────────────────────────────────────────────┘
```

## 数据文件组织

### 目录结构

```
data/
├── file_provider.py         # 文件数据提供者（解析器）
├── requirements/            # 需求文档（Markdown）
│   ├── 用户管理/
│   │   ├── REQ-001_用户登录功能.md
│   │   ├── REQ-002_用户注册功能.md
│   │   └── REQ-003_密码找回功能.md
│   └── 订单管理/
│       ├── REQ-004_订单创建功能.md
│       └── REQ-005_订单列表与详情功能.md
├── testcases/               # 测试用例（YAML + 索引）
│   ├── 用户管理/
│   │   ├── TC-001_手机号验证码正常流程.yaml
│   │   ├── TC-002_密码错误锁定测试.yaml
│   │   ├── TC-003_手机号注册正常流程.yaml
│   │   └── testcase_index.json
│   └── 订单管理/
│       ├── TC-004_订单创建正常流程.yaml
│       ├── TC-005_订单超时取消测试.yaml
│       ├── TC-006_订单列表分页筛选测试.yaml
│       └── testcase_index.json
└── bugs/                    # BUG 数据（YAML + 索引）
    ├── 用户管理/
    │   ├── BUG-001_登录锁定机制未生效.yaml
    │   ├── BUG-003_密码重置链接可重复使用.yaml
    │   └── bug_index.json
    └── 订单管理/
        ├── BUG-002_订单金额未包含运费.yaml
        ├── BUG-004_订单列表分页数量不正确.yaml
        └── bug_index.json
```

### 数据关联关系

```
需求文档 (Markdown)
    │
    ├─ 测试用例索引 (testcase_index.json)
    │     └─ 通过 requirement_id 关联需求
    │          └─ 每个测试用例指向一个需求
    │
    └─ BUG 索引 (bug_index.json)
          ├─ 通过 requirement_id 关联需求
          └─ 通过 test_case_id 关联测试用例（可选）

管理后台查询:
GET /api/modules/{module}/overview
  → 加载模块下所有需求文档
  → 加载 testcase_index.json
  → 加载 bug_index.json
  → 按需求组织返回
```

## 模块职责

### 1. data/file_provider.py - 数据层
**职责**: 从文件加载数据
- 解析 Markdown 需求文档
- 解析 YAML 测试用例和 BUG 文件
- 加载 JSON 索引文件
- 提供 CRUD 操作接口
- 支持按模块、需求ID等查询
- 生成模块概览

**关键类**:
- `FileDataProvider`: 文件数据提供者，封装所有数据操作

**关键方法**:
- `get_module_overview(module)`: 获取模块完整概览（管理后台核心）
- `get_requirements_by_module(module)`: 按模块获取需求
- `get_test_cases_by_requirement(requirement_id)`: 按需求获取测试用例
- `get_bugs_by_test_case(test_case_id)`: 按测试用例获取 BUG

### 2. modules/models.py - 数据模型
**职责**: 定义所有数据结构
- 使用 Pydantic 进行数据验证
- 支持 JSON 序列化
- 枚举类型定义

**关键模型**:
- `Requirement`, `TestCase`, `Bug`: 核心数据模型
- `QualityAnalysisResult`: 质量分析结果
- `AIAssistedTestResult`: AI辅助测试结果
- `ProcessOptimizationResult`: 流程优化结果
- `KnowledgeManagementResult`: 知识管理结果
- `ProjectQualityReport`: 项目质量报告

### 3. modules/quality_analysis.py - 质量分析
**职责**: 质量指标计算和预测
- 缺陷密度计算
- 需求覆盖率分析
- 高风险模块识别
- BUG趋势预测（使用 sklearn 线性回归）

**关键函数**:
- `analyze_quality()`: 综合分析
- `predict_bug_trend()`: BUG趋势预测
- `predict_bugs_by_module()`: 按模块预测

### 4. modules/ai_assisted_testing.py - AI辅助测试
**职责**: 智能测试辅助功能
- 根据需求生成测试用例
- BUG根因分析（基于历史数据）
- 代码变更推荐测试用例

**关键函数**:
- `generate_test_cases_from_requirement()`: 生成测试用例
- `analyze_bug_root_cause()`: BUG根因分析
- `recommend_test_cases_for_code_change()`: 推荐测试用例

### 5. modules/process_optimization.py - 流程优化
**职责**: 优化测试流程和资源分配
- 需求变更影响分析
- 测试用例优先级排序
- 低效用例识别

**关键函数**:
- `analyze_requirement_change_impact()`: 变更影响分析
- `prioritize_test_cases()`: 优先级排序
- `identify_inefficient_test_cases()`: 识别低效用例

### 6. modules/knowledge_management.py - 知识管理
**职责**: 知识积累和检索
- 新人培训材料生成
- 历史BUG案例收集
- 智能搜索
- 常见问答生成

**关键函数**:
- `generate_training_materials()`: 培训材料
- `collect_historical_bugs()`: 历史BUG案例
- `search_knowledge()`: 智能搜索

### 7. modules/smart_report.py - 智能报告
**职责**: 生成质量报告
- 项目质量报告
- 模块质量报告

**关键函数**:
- `generate_smart_report()`: 项目报告
- `generate_module_report()`: 模块报告

### 8. mcp_tools/qa_tools.py - MCP工具服务
**职责**: 提供 MCP 协议服务
- 为 LLM 提供数据访问工具
- 12个可用工具

**关键工具**:
- `get_module_overview(module)`: 获取模块完整概览
- `list_modules()`: 获取所有模块
- `get_all_requirements()`: 获取所有需求
- `get_all_test_cases()`: 获取所有测试用例
- `get_all_bugs()`: 获取所有BUG

### 9. main.py - API入口
**职责**: FastAPI 应用入口
- 路由定义
- CORS 配置
- 统一接口

## 数据流

### 质量分析流程
```
文件数据 → FileDataProvider 解析 → 计算缺陷密度 → 计算需求覆盖率 →
识别高风险模块 → 生成分析结果 → 返回API
```

### BUG预测流程
```
历史BUG数据 → 按日期统计 → 训练线性回归模型 →
预测未来趋势 → 返回预测结果
```

### AI辅助测试流程
```
输入(需求ID/BUG ID/代码文件) →
调用对应功能 →
生成结果 → 返回API
```

### 模块概览查询流程（管理后台核心）
```
GET /api/modules/{module}/overview
  → FileDataProvider.get_module_overview(module)
    → 解析 requirements/{module}/ 下所有 .md 文件
    → 加载 testcases/{module}/testcase_index.json
    → 加载 bugs/{module}/bug_index.json
    → 按需求组织关联数据
    → 返回 {summary, requirements: [{requirement, test_cases, bugs}]}
```

## 扩展点

### 1. 数据层扩展
当前使用文件存储，可以轻松替换或扩展为：
- **数据库同步**: 定期将文件同步到 MySQL/PostgreSQL
- **混合模式**: 文件 + 数据库双写
- **Elasticsearch**: 用于全文搜索

### 2. AI模型扩展
当前使用规则和统计方法，可以扩展为：
- OpenAI GPT
- Claude
- 本地 LLM

### 3. MCP工具扩展
可以添加更多工具：
- 创建/更新需求
- 执行测试用例
- 提交BUG报告

### 4. 前端扩展
可以开发：
- React/Vue 前端
- 数据可视化仪表板
- 实时通知系统

## 性能优化建议

1. **缓存**: 对频繁查询的模块概览使用缓存
2. **索引**: JSON 索引文件避免遍历所有文件
3. **异步**: 对耗时操作使用异步处理
4. **懒加载**: 大模块按需加载详细数据
5. **批量**: 批量操作减少文件读取

## 安全考虑

1. **认证**: 添加用户认证
2. **授权**: 基于角色的访问控制
3. **输入验证**: 严格验证所有输入
4. **速率限制**: 防止API滥用
5. **日志审计**: 记录所有关键操作
6. **文件安全**: 限制文件读取范围，防止路径穿越
