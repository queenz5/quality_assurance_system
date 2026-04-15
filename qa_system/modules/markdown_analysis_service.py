"""
Markdown结构化分析服务
LLM直接输出带标注的结构化Markdown文档
符合 qa_system/data/requirements 目录的标准格式
"""
import os
import uuid
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from modules.requirement_analyzer import RequirementAnalyzer
from config.llm_config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage


class MarkdownAnalysisService:
    """Markdown结构化分析服务"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
        self.data_dir = Path(data_dir)
        self.drafts_dir = self.data_dir / "drafts"
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        
        self.analyzer = RequirementAnalyzer()

    def analyze_to_markdown(
        self, 
        content: str, 
        source_name: str = "未知来源"
    ) -> Dict[str, Any]:
        """
        分析需求文档，输出带标注的结构化Markdown
        
        Returns:
            {
                "draft_id": "草稿ID",
                "markdown": "完整Markdown文本(包含所有需求)",
                "requirements": [{"id", "title", "module", "content"}],
                "issues": [...],
                "summary": "分析摘要"
            }
        """
        # 1. 先分析问题
        analysis_result = self.analyzer.analyze_requirement_document(content, source_name)
        
        # 2. 构建Prompt，让LLM输出标准格式的Markdown
        markdown_prompt = self._build_markdown_prompt(content, source_name, analysis_result)
        
        # 3. 调用LLM生成Markdown
        llm = get_llm()
        messages = [
            SystemMessage(content=markdown_prompt),
            HumanMessage(content=f"请将以下需求文档转换为结构化的需求文档:\n\n{content[:5000]}")
        ]
        
        print("🔍 正在调用LLM生成Markdown...")
        response = llm.invoke(messages)
        markdown_text = response.content if hasattr(response, 'content') else str(response)
        
        print(f"✅ LLM调用完成，返回内容长度: {len(markdown_text)} 字符")
        print(f"📄 返回内容预览:\n{markdown_text[:300]}")
        
        # 清理Markdown
        markdown_text = self._clean_markdown(markdown_text)
        
        if not markdown_text or len(markdown_text.strip()) < 100:
            print(f"⚠️ 警告: LLM返回内容为空或过短，使用兜底方案")
            markdown_text = self._generate_default_markdown(content, source_name, analysis_result)
            print(f"✅ 兜底方案生成，长度: {len(markdown_text)} 字符")
        
        # 4. 从Markdown中解析出需求列表
        requirements = self._parse_requirements(markdown_text)

        print(f"📋 解析到 {len(requirements)} 个需求")
        if requirements:
            print(f"   第一个需求: {requirements[0]}")

        # 5. 重新编号需求 ID（确保从正确的编号开始）
        requirements = self._renumber_requirements(requirements)

        # 更新 Markdown 中的 ID
        markdown_text = self._update_markdown_ids(markdown_text, requirements)

        # 5. 使用第一个需求的标题和模块作为草稿的标题和模块
        draft_title = requirements[0].get("title", source_name) if requirements else source_name
        draft_module = requirements[0].get("module", "未分类") if requirements else "未分类"
        
        print(f"📝 草稿标题: {draft_title}, 模块: {draft_module}")
        
        # 创建草稿
        draft_id = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"

        draft_data = {
            "draft_id": draft_id,
            "source_name": source_name,
            "title": draft_title,
            "module": draft_module,
            "markdown_content": markdown_text,
            "requirements": requirements,
            "analysis_summary": analysis_result.analysis_summary,
            "issues": [
                {
                    "id": issue.requirement_issue_id,
                    "type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "field_name": issue.field_name,
                    "description": issue.description,
                    "suggestion": issue.suggestion
                }
                for issue in analysis_result.issues
            ],
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # 保存草稿
        draft_file = self.drafts_dir / f"{draft_id}.md"
        meta_file = self.drafts_dir / f"{draft_id}.json"

        # Markdown文件（供编辑）
        draft_file.write_text(markdown_text, encoding='utf-8')

        # JSON元数据（供列表展示）
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 草稿保存成功: {draft_id}, {len(requirements)} 个需求")

        return {
            "draft_id": draft_id,
            "markdown": markdown_text,
            "requirements": requirements,
            "issues": draft_data["issues"],
            "summary": analysis_result.analysis_summary,
            "total_issues": len(analysis_result.issues),
            "critical_issues": analysis_result.critical_issues,
            "major_issues": analysis_result.major_issues,
            "minor_issues": analysis_result.minor_issues
        }

    def get_draft_markdown(self, draft_id: str) -> Optional[str]:
        """获取草稿的Markdown内容"""
        draft_file = self.drafts_dir / f"{draft_id}.md"
        if not draft_file.exists():
            return None
        return draft_file.read_text(encoding='utf-8')

    def save_draft_markdown(self, draft_id: str, markdown: str) -> bool:
        """保存编辑后的Markdown"""
        draft_file = self.drafts_dir / f"{draft_id}.md"
        meta_file = self.drafts_dir / f"{draft_id}.json"

        if not meta_file.exists():
            return False

        # 保存 Markdown
        draft_file.write_text(markdown, encoding='utf-8')

        # 更新元数据中的需求列表、标题和模块
        requirements = self._parse_requirements(markdown)
        
        import json
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        meta["requirements"] = requirements
        if requirements:
            meta["title"] = requirements[0].get("title", meta.get("title", ""))
            meta["module"] = requirements[0].get("module", meta.get("module", "未分类"))
        meta["updated_at"] = datetime.now().isoformat()

        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return True

    def _parse_requirements(self, markdown: str) -> List[Dict[str, Any]]:
        """
        从Markdown中解析出各个需求
        使用与发布逻辑相同的正则表达式，确保一致性
        """
        requirements = []

        # 匹配 # REQ-XXX: 标题（与发布逻辑一致）
        pattern = r'^#\s+(REQ-\d+):\s+(.+)$'
        matches = list(re.finditer(pattern, markdown, re.MULTILINE))

        if not matches:
            print(f"⚠️ 警告: 未能解析到任何需求")
            print(f"Markdown前500字符:\n{markdown[:500]}")
            return requirements

        for i, match in enumerate(matches):
            req_id = match.group(1)
            req_title = match.group(2).strip()

            # 获取该需求的内容（到下一个需求或文件末尾）
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            req_content = markdown[start:end].strip()

            # 提取模块（与发布逻辑一致）
            module_match = re.search(r'-\s*\*\*模块\*\*:\s*(.+)', req_content)
            module = module_match.group(1).strip() if module_match else "未分类"

            requirements.append({
                "id": req_id,
                "title": req_title,
                "module": module,
                "content": req_content
            })

            print(f"✅ 解析到需求: {req_id} - {req_title} (模块: {module})")

        return requirements

    def _renumber_requirements(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重新编号需求 ID，确保从正确的编号开始"""
        if not requirements:
            return requirements

        # 获取下一个可用的需求 ID
        from pathlib import Path
        import json
        requirements_dir = Path(__file__).parent.parent / "data" / "requirements"
        index_file = requirements_dir / "_index.json"
        next_req_num = 1

        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                next_req_num = index_data.get("last_req_id", 0) + 1
            except:
                pass

        # 重新编号
        for i, req in enumerate(requirements):
            req["id"] = f"REQ-{next_req_num + i:03d}"

        return requirements

    def _update_markdown_ids(self, markdown: str, requirements: List[Dict[str, Any]]) -> str:
        """更新 Markdown 中的需求 ID"""
        import re

        # 找到所有 # REQ-XXX: 标题 的行
        pattern = r'^(#\s+)REQ-\d+:\s+'
        matches = list(re.finditer(pattern, markdown, re.MULTILINE))

        if len(matches) != len(requirements):
            print(f"⚠️ 警告: Markdown 中的需求数量 ({len(matches)}) 与 requirements 列表 ({len(requirements)}) 不匹配")
            return markdown

        # 从后往前替换，避免位置偏移问题
        result = markdown
        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            new_id = requirements[i]["id"]
            new_prefix = f"{match.group(1)}{new_id}: "
            result = result[:match.start()] + new_prefix + result[match.end():]

        return result

    def _build_markdown_prompt(self, content: str, source_name: str, analysis_result) -> str:
        """构建Markdown生成Prompt"""
        # 获取当前最大需求 ID
        from pathlib import Path
        import json
        requirements_dir = Path(__file__).parent.parent / "data" / "requirements"
        index_file = requirements_dir / "_index.json"
        next_req_num = 1

        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                next_req_num = index_data.get("last_req_id", 0) + 1
            except:
                pass

        return f"""你是一个专业的高级需求分析师。你的任务是将以下需求文档转换为结构化的需求文档。

## 输出格式要求

你必须严格按照以下格式输出，每个需求单独成一个文档：

**重要：需求 ID 必须从 REQ-{next_req_num:03d} 开始递增！** 例如：REQ-{next_req_num:03d}, REQ-{next_req_num+1:03d}, REQ-{next_req_num+2:03d}...

```markdown
# REQ-{next_req_num:03d}: [需求标题]

## 基本信息
- **模块**: [模块名称]
- **子模块**: [子模块名称，可选]
- **优先级**: 高/中/低
- **状态**: 待开发
- **创建时间**: YYYY-MM-DD

## 需求描述
[详细的需求描述文本]

## 功能点
1. [功能点1描述]
   - 业务规则: [规则1]; [规则2]
   - 约束条件: [约束1]
2. [功能点2描述]
   - 业务规则: [规则1]
   - 约束条件: [约束1]

## 前置条件
- [条件1]
- [条件2]

## 后置条件
- [条件1]
- [条件2]

## 业务规则
| 规则编号 | 规则描述 | 优先级 |
|---------|---------|--------|
| BR-001 | [描述] | 高/中/低 |

## 异常处理
- **[异常场景]**: [预期处理]
- **[异常场景]**: [预期处理]

## 标签
标签1、标签2、标签3

## 依赖关系
- 前置需求: 无
- 后续需求: 无

## 变更历史
| 日期 | 操作 | 说明 | 操作人 |
|------|------|------|--------|
| YYYY-MM-DD | 创建 | AI 解析生成 | AI |
```

## 编号规则

1. **需求编号**: REQ-001, REQ-002... (模块内唯一，从001开始)
2. **业务规则**: BR-001, BR-002... (需求内唯一，从001开始)
3. **功能点**: 使用列表序号 (1., 2., 3.)，不使用编号

## 关键要求

1. 每个需求以 `# REQ-XXX: 标题` 开头
2. **模块**字段必须准确填写
3. 功能点用列表序号，不用FP-XXX
4. 业务规则用表格格式
5. 异常处理用列表格式 `- **[场景]**: 处理`
6. 保持原文档的所有信息
7. 如果信息不足，可以合理推断

现在，请将以下需求文档转换为结构化格式：
"""

    def _clean_markdown(self, markdown: str) -> str:
        """清理Markdown文本"""
        lines = markdown.split('\n')
        cleaned_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if not in_code_block:
                cleaned_lines.append(line)

        result = '\n'.join(cleaned_lines).strip()
        
        if len(result) < 100:
            return markdown.strip()
        
        return result

    def _generate_default_markdown(self, content: str, source_name: str, analysis_result) -> str:
        """生成默认的Markdown格式（当LLM返回空时使用）"""
        lines = []
        
        lines.append(f"# REQ-001: 待分析需求")
        lines.append("")
        lines.append("## 基本信息")
        lines.append(f"- **模块**: 未分类")
        lines.append(f"- **优先级**: 中")
        lines.append(f"- **状态**: 待开发")
        lines.append(f"- **创建时间**: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("")
        lines.append("## 需求描述")
        lines.append("AI未能自动解析，以下为原始内容：")
        lines.append("")
        lines.append("```")
        lines.append(content[:3000])
        lines.append("```")
        lines.append("")
        lines.append("## 变更历史")
        lines.append("| 日期 | 操作 | 说明 | 操作人 |")
        lines.append("|------|------|------|--------|")
        lines.append(f"| {datetime.now().strftime('%Y-%m-%d')} | 创建 | AI解析失败，手动生成 | AI |")
        lines.append("")
        
        return '\n'.join(lines)
