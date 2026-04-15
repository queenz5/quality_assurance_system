# Skill 整合完成说明

## ✅ 完成内容

已将结构化需求生成的 Prompt 从代码硬编码整合到 Skill 文件中。

---

## 📁 新增文件

### 1. Skill 主文件
```
skills/prd-to-structured-requirements/SKILL.md
```

包含：
- Skill 描述和触发条件
- 完整工作流定义
- 结构化需求格式规范
- 字段说明和编号规则
- 解析原则
- 输出要求
- 常见场景处理
- 示例

### 2. 需求目录说明
```
skills/prd-to-structured-requirements/requirements/README.md
```

### 3. 格式参考文档
```
skills/prd-to-structured-requirements/references/structured-requirement-format.md
```

---

## 🔄 修改的文件

### `qa_system/modules/requirement_parser.py`

#### 修改内容

**之前（硬编码）**：
```python
def _get_system_prompt(self) -> str:
    """获取系统提示词"""
    return """你是一个高级需求分析师..."""  # 硬编码的 Prompt
```

**现在（从 Skill 加载）**：
```python
def __init__(self, output_dir: str = None, skill_dir: str = None):
    # 设置 Skill 目录
    if skill_dir is None:
        self.skill_dir = Path(__file__).parent.parent.parent / "skills" / "prd-to-structured-requirements"
    
    # 加载 Prompt
    self._system_prompt = self._load_system_prompt()

def _load_system_prompt(self) -> str:
    """从 SKILL.md 文件加载系统 Prompt"""
    skill_file = self.skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        return self._get_default_system_prompt()
    
    # 解析 SKILL.md，提取 Prompt 部分
    content = skill_file.read_text(encoding='utf-8')
    # ... 解析逻辑 ...
    
    return prompt_content
```

#### 新增方法
- `__init__()` - 增加 `skill_dir` 参数
- `_load_system_prompt()` - 从 SKILL.md 加载 Prompt
- `_get_default_system_prompt()` - 默认 Prompt（备用）

#### 删除方法
- `_get_system_prompt()` - 已被 `_load_system_prompt()` 替代

---

## 📊 工作流程

```
初始化 RequirementParser
    │
    ├─ 设置 Skill 目录
    │   └─ skills/prd-to-structured-requirements/
    │
    ├─ 调用 _load_system_prompt()
    │   │
    │   ├─ 读取 SKILL.md
    │   │
    │   ├─ 解析文件结构
    │   │   ├─ 跳过 frontmatter (---...---)
    │   │   ├─ 提取关键章节
    │   │   │   ├─ ## 工作流
    │   │   │   ├─ ## 结构化需求格式
    │   │   │   ├─ ## 字段说明
    │   │   │   ├─ ## 解析原则
    │   │   │   └─ ## 输出要求
    │   │   └─ 排除示例部分
    │   │
    │   └─ 返回提取的 Prompt
    │
    └─ 保存到 self._system_prompt
         │
         ▼
    调用 LLM 时使用
    SystemMessage(content=self._system_prompt)
```

---

## 🎯 优势

### 1. Prompt 与代码分离
- ✅ Prompt 在 `SKILL.md` 中维护
- ✅ 非技术人员也能修改 Prompt
- ✅ 支持 Markdown 格式，易于阅读

### 2. 版本控制
- ✅ SKILL.md 纳入 Git 管理
- ✅ 可以追踪 Prompt 变更历史
- ✅ 支持分支和回滚

### 3. 热加载（无需重启）
- ✅ 每次创建 `RequirementParser` 实例时重新加载
- ✅ 修改 SKILL.md 后，下次解析自动生效
- ⚠️ 当前实现：重启后端服务更稳妥

### 4. 容错机制
- ✅ 如果 SKILL.md 不存在，使用默认 Prompt
- ✅ 如果解析失败，使用整个文件内容
- ✅ 详细的日志输出，便于调试

---

## 📝 如何修改 Prompt

### 步骤 1：编辑 SKILL.md

```bash
# 打开文件
vim skills/prd-to-structured-requirements/SKILL.md
```

修改关键章节：
- `## 工作流` - 修改解析流程
- `## 结构化需求格式` - 修改输出格式
- `## 字段说明` - 修改字段定义
- `## 解析原则` - 修改解析策略
- `## 输出要求` - 修改输出规范

### 步骤 2：保存文件

```bash
# 保存后无需重启（推荐重启更稳妥）
```

### 步骤 3：测试

上传一个新的 PDF 文件，查看解析结果是否符合预期。

---

## 🔍 调试技巧

### 查看 Prompt 加载日志

启动后端后，上传文件时会看到：

```
✅ 从 SKILL.md 加载 Prompt 成功
```

如果加载失败：

```
⚠️  警告: Skill 文件不存在: /path/to/SKILL.md，使用默认 Prompt
```

或

```
❌ 加载 SKILL.md 失败: xxx，使用默认 Prompt
```

### 查看实际使用的 Prompt

在代码中临时添加：

```python
def _parse_with_ai(self, content: str, source_name: str) -> RequirementParseResult:
    # 临时打印 Prompt 查看内容
    print("📋 当前使用的 System Prompt:")
    print(self._system_prompt[:500])  # 打印前 500 字符
    ...
```

---

## 📚 Skill 目录结构

```
skills/prd-to-structured-requirements/
├── SKILL.md                           # Skill 主文件（包含 Prompt）
├── requirements/                      # 原始 PRD 目录
│   └── README.md                      # 使用说明
└── references/                        # 参考文档
    └── structured-requirement-format.md  # 格式规范
```

---

## 🚀 下一步

### 建议优化

1. **Prompt 热加载**
   - 监听 SKILL.md 文件变更
   - 自动重新加载，无需重启

2. **Prompt 版本管理**
   - 使用 Git 标签标记重要版本
   - 维护 CHANGELOG.md

3. **Prompt 测试**
   - 创建测试用例集
   - 自动化测试 Prompt 效果

4. **多 Skill 支持**
   - 测试用例生成 Skill
   - Bug 分析 Skill
   - 质量评估 Skill

---

## ⚠️ 注意事项

1. **SKILL.md 格式**
   - 必须包含 `## 工作流`、`## 结构化需求格式` 等关键章节
   - 如果格式变更，需要更新 `_load_system_prompt()` 解析逻辑

2. **编码**
   - 所有文件使用 UTF-8 编码
   - 避免特殊字符导致解析失败

3. **性能**
   - SKILL.md 文件不宜过大（建议 < 50KB）
   - 过长的 Prompt 会增加 LLM 调用成本

4. **安全性**
   - SKILL.md 不应包含敏感信息
   - API Key 等机密信息使用环境变量

---

## 📖 相关文档

- [Skill 主文件](./skills/prd-to-structured-requirements/SKILL.md)
- [格式规范](./skills/prd-to-structured-requirements/references/structured-requirement-format.md)
- [需求解析器代码](./qa_system/modules/requirement_parser.py)
