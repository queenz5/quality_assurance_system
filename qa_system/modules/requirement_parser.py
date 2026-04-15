"""
需求拆解模块
将原始 PRD/需求文档拆解为结构化的需求数据

功能：
1. 读取原始 PRD（PDF/Word/Markdown/TXT）
2. 从 SKILL 文件读取 Prompt（不再硬编码）
3. AI 解析需求文档，识别功能模块、功能点、业务规则等
4. 生成结构化需求文件，保存到 qa_system/data/requirements/
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from modules.models import (
    StructuredRequirement, FunctionPoint, BusinessRule, ExceptionHandling,
    ChangeHistory, RequirementParseResult, RequirementStatus, Priority
)
from config.llm_config import get_llm


class RequirementParser:
    """需求解析器"""
    
    def __init__(self, output_dir: str = None, skill_dir: str = None):
        """
        初始化需求解析器
        
        Args:
            output_dir: 结构化需求输出目录，默认为临时目录
            skill_dir: Skill 目录路径，用于读取 SKILL.md 中的 Prompt
        """
        import tempfile
        if output_dir is None:
            # 如果没有指定输出目录，使用临时目录
            self.output_dir = Path(tempfile.mkdtemp(prefix="req_parse_"))
            self._is_temp_dir = True
        else:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self._is_temp_dir = False
        
        # 设置 Skill 目录
        if skill_dir is None:
            # 默认 Skill 目录
            self.skill_dir = Path(__file__).parent.parent.parent / "skills" / "prd-to-structured-requirements"
        else:
            self.skill_dir = Path(skill_dir)
        
        # 加载 Prompt
        self._system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """从 SKILL.md 文件加载系统 Prompt"""
        skill_file = self.skill_dir / "SKILL.md"
        
        if not skill_file.exists():
            # 如果 Skill 文件不存在，使用默认 Prompt
            print(f"⚠️  警告: Skill 文件不存在: {skill_file}，使用默认 Prompt")
            return self._get_default_system_prompt()
        
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # 解析 SKILL.md，提取 Prompt 部分
            # SKILL.md 的结构：
            # ---
            # frontmatter
            # ---
            # # 标题
            # 内容...
            # ## 工作流
            # ## 结构化需求格式
            # ...
            
            # 跳过 frontmatter
            if content.startswith('---'):
                # 找到第二个 ---
                second_dash = content.find('---', 3)
                if second_dash > 0:
                    content = content[second_dash + 3:].strip()
            
            # 提取关键部分
            # 我们只需要工作流和格式部分，不需要示例
            sections = []
            current_section = ""
            
            for line in content.split('\n'):
                if line.startswith('# '):
                    # 主标题
                    current_section = "title"
                    sections.append(line)
                elif line.startswith('## 工作流') or line.startswith('## 结构化需求格式') or line.startswith('## 字段说明') or line.startswith('## 解析原则') or line.startswith('## 输出要求'):
                    # 关键章节
                    current_section = "content"
                    sections.append(line)
                elif line.startswith('## '):
                    # 其他章节（如示例等），停止收录
                    if line.startswith('## 示例') or line.startswith('## 常见场景'):
                        break
                    current_section = "content"
                    sections.append(line)
                elif current_section in ["title", "content"]:
                    sections.append(line)
            
            prompt_content = '\n'.join(sections)
            
            if not prompt_content.strip():
                # 如果提取失败，使用整个文件内容
                print("⚠️  警告: 无法从 SKILL.md 提取 Prompt，使用整个文件内容")
                return content
            
            print(f"✅ 从 SKILL.md 加载 Prompt 成功")
            return prompt_content
            
        except Exception as e:
            print(f"❌ 加载 SKILL.md 失败: {str(e)}，使用默认 Prompt")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """默认系统 Prompt（备用）"""
        return """你是一个高级需求分析师。你的任务是将原始需求文档拆解为结构化的需求数据。

你需要：
1. 识别所有功能模块和子模块
2. 为每个模块提取功能点、业务规则、约束条件
3. 分析前置条件、后置条件、异常处理
4. 识别需求间的依赖关系

输出必须是严格的 JSON 格式，包含以下结构：
{
  "modules": [
    {
      "module_name": "模块名称",
      "requirements": [
        {
          "id": "REQ-001",
          "title": "需求标题",
          "sub_module": "子模块（可选）",
          "priority": "高/中/低",
          "description": "需求详细描述",
          "function_points": [
            {
              "id": "FP-001",
              "description": "功能点描述",
              "business_rules": ["规则1", "规则2"],
              "constraints": ["约束1"],
              "priority": "高/中/低"
            }
          ],
          "preconditions": ["前置条件1"],
          "postconditions": ["后置条件1"],
          "business_rules": [
            {
              "id": "BR-001",
              "description": "业务规则描述",
              "priority": "高/中/低"
            }
          ],
          "exception_handling": [
            {
              "scenario": "异常场景",
              "expected_handling": "预期处理方式"
            }
          ],
          "prerequisite_requirements": ["前置需求ID"],
          "dependent_requirements": ["后续需求ID"],
          "tags": ["标签1", "标签2"]
        }
      ]
    }
  ],
  "parse_summary": "解析总结",
  "warnings": ["警告列表"]
}

注意事项：
- 需求 ID 格式：REQ-XXX（三位数字，从 001 开始递增）
- 功能点 ID 格式：FP-XXX
- 业务规则 ID 格式：BR-XXX
- 优先级使用：高/中/低
- 不要遗漏任何功能点
- 如果某些信息不明确，可以根据常识推断，但要在 warnings 中标注"""
    
    def _get_next_requirement_id(self) -> str:
        """获取下一个可用的需求 ID（从文件索引读取）"""
        # 使用固定的索引文件路径
        requirements_dir = Path(__file__).parent.parent / "data" / "requirements"
        index_file = requirements_dir / "_index.json"

        # 确保目录存在
        requirements_dir.mkdir(parents=True, exist_ok=True)

        max_id = 0

        # 优先从索引文件读取
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                max_id = index_data.get("last_req_id", 0)
            except Exception as e:
                print(f"⚠️ 读取索引失败: {e}，尝试扫描文件")

        # 如果索引不存在或读取失败，扫描现有文件
        if max_id == 0:
            max_id = self._scan_existing_requirement_files(requirements_dir)

        # 返回下一个编号
        next_id = max_id + 1
        return f"REQ-{next_id:03d}"

    def _scan_existing_requirement_files(self, requirements_dir: Path) -> int:
        """扫描现有需求文件，找出最大编号"""
        max_id = 0

        if not requirements_dir.exists():
            return 0

        # 扫描所有 REQ-XXX_*.md 文件
        for file_path in requirements_dir.glob("REQ-*.md"):
            file_name = file_path.name
            # 提取 REQ-XXX 部分
            match = re.match(r'REQ-(\d+)_', file_name)
            if match:
                try:
                    req_num = int(match.group(1))
                    max_id = max(max_id, req_num)
                except:
                    pass

        if max_id > 0:
            print(f"📂 扫描到现有需求文件，最大编号: REQ-{max_id:03d}")

        return max_id

    def _update_requirements_index(self, requirements: List[StructuredRequirement]):
        """更新需求索引文件"""
        requirements_dir = Path(__file__).parent.parent / "data" / "requirements"
        index_file = requirements_dir / "_index.json"

        # 确保目录存在
        index_file.parent.mkdir(parents=True, exist_ok=True)

        # 加载现有索引
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            except Exception as e:
                print(f"⚠️ 读取索引失败: {e}，创建新索引")
                existing_index = {"last_req_id": 0, "requirements": []}
        else:
            existing_index = {"last_req_id": 0, "requirements": []}

        # 更新最大 ID 和需求列表
        for req in requirements:
            try:
                req_num = int(req.id.split("-")[1])
                if req_num > existing_index["last_req_id"]:
                    existing_index["last_req_id"] = req_num
            except:
                pass

            # 检查是否已存在（避免重复）
            existing_req = next(
                (r for r in existing_index["requirements"] if r.get("id") == req.id),
                None
            )

            if existing_req:
                # 更新现有记录
                existing_req.update({
                    "title": req.title,
                    "module": req.module,
                    "file": f"{req.id}_{req.title}.md",
                    "updated_at": req.updated_at.isoformat() if req.updated_at else datetime.now().isoformat()
                })
            else:
                # 添加新记录
                existing_index["requirements"].append({
                    "id": req.id,
                    "title": req.title,
                    "module": req.module,
                    "file": f"{req.id}_{req.title}.md",
                    "created_at": req.created_at.isoformat() if req.created_at else datetime.now().isoformat(),
                    "updated_at": req.updated_at.isoformat() if req.updated_at else datetime.now().isoformat()
                })

        # 写入索引文件
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(existing_index, f, ensure_ascii=False, indent=2)

        print(f"✅ 索引已更新: {len(requirements)} 个需求，最新 ID: REQ-{existing_index['last_req_id']:03d}")
    
    def _get_next_function_point_id(self, existing_ids: List[str]) -> str:
        """获取下一个可用的功能点 ID"""
        max_id = 0
        for fp_id in existing_ids:
            if fp_id.startswith("FP-"):
                try:
                    num = int(fp_id.split("-")[1])
                    max_id = max(max_id, num)
                except:
                    pass
        next_id = max_id + 1
        return f"FP-{next_id:03d}"
    
    def _get_next_business_rule_id(self, existing_ids: List[str]) -> str:
        """获取下一个可用的业务规则 ID"""
        max_id = 0
        for br_id in existing_ids:
            if br_id.startswith("BR-"):
                try:
                    num = int(br_id.split("-")[1])
                    max_id = max(max_id, num)
                except:
                    pass
        next_id = max_id + 1
        return f"BR-{next_id:03d}"
    
    def _renumber_requirements(self, result: RequirementParseResult) -> RequirementParseResult:
        """重新编号需求、功能点和业务规则，避免冲突"""
        if not result.parsed_requirements:
            return result

        # 获取下一个可用的需求 ID
        next_req_id = self._get_next_requirement_id()
        req_num = int(next_req_id.split("-")[1])

        # 重新编号每个需求
        for req in result.parsed_requirements:
            # 更新需求 ID
            req.id = f"REQ-{req_num:03d}"
            req_num += 1  # 递增编号

            # 重新编号功能点
            fp_counter = 1
            for fp in req.function_points:
                fp.id = f"FP-{req_num-1:03d}-{fp_counter:03d}"
                fp_counter += 1

            # 重新编号业务规则
            br_counter = 1
            for br in req.business_rules:
                br.id = f"BR-{req_num-1:03d}-{br_counter:03d}"
                br_counter += 1

        return result
    
    def parse_prd_file(self, file_path: str) -> RequirementParseResult:
        """
        解析 PRD 文件
        
        Args:
            file_path: PRD 文件路径（支持 .md, .txt）
        
        Returns:
            需求解析结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件内容
        content = self._read_file(file_path)
        
        # 使用 AI 解析
        return self._parse_with_ai(content, file_path.name)
    
    def parse_prd_text(self, text: str, source_name: str = "未知来源") -> RequirementParseResult:
        """
        解析 PRD 文本内容
        
        Args:
            text: PRD 文本内容
            source_name: 来源名称（用于日志和总结）
        
        Returns:
            需求解析结果
        """
        return self._parse_with_ai(text, source_name)
    
    def _read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.md', '.txt']:
            return file_path.read_text(encoding='utf-8')
        elif suffix == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif suffix == '.docx':
            return self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """从 PDF 提取文本"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            # 如果没有 PyPDF2，尝试使用 pdfplumber
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                raise ImportError(
                    "PDF 解析需要安装 PyPDF2 或 pdfplumber。\n"
                    "请运行: pip install PyPDF2 或 pip install pdfplumber"
                )
    
    def _extract_text_from_docx(self, file_path: Path) -> str:
        """从 DOCX 提取文本"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise ImportError(
                "DOCX 解析需要安装 python-docx。\n"
                "请运行: pip install python-docx"
            )
    
    def _parse_with_ai(self, content: str, source_name: str) -> RequirementParseResult:
        """使用 AI 解析需求文档"""
        
        # 构建 Prompt
        prompt = self._build_parse_prompt(content, source_name)
        
        # 调用 LLM
        try:
            llm = get_llm()
            from langchain_core.messages import SystemMessage, HumanMessage
            
            messages = [
                SystemMessage(content=self._system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = llm.invoke(messages)
            result_text = response.content
            
            # 解析 JSON 结果
            parsed_result = self._parse_json_response(result_text, content, source_name)
            
            # 重新编号，避免与已有需求冲突
            parsed_result = self._renumber_requirements(parsed_result)
            
            return parsed_result
            
        except Exception as e:
            # 如果 AI 调用失败，返回错误结果
            return RequirementParseResult(
                original_content=content[:200] + "...",
                parsed_requirements=[],
                parse_summary=f"AI 解析失败: {str(e)}",
                warnings=[f"解析失败: {str(e)}"],
                total_modules=0,
                total_function_points=0
            )
    
    def _build_parse_prompt(self, content: str, source_name: str) -> str:
        """构建解析 Prompt"""
        # 如果内容太长，截取前 8000 字符（避免超过 LLM 限制）
        max_length = 8000
        if len(content) > max_length:
            content = content[:max_length] + "\n...(内容过长，已截断)"
        
        return f"""请解析以下需求文档，并将其转换为结构化需求数据。

【需求文档来源】
{source_name}

【需求文档内容】
{content}

【输出要求】
请按照系统提示词中定义的 JSON 格式输出解析结果。

注意：
1. 仔细分析文档，识别所有功能模块
2. 为每个模块拆分独立的需求条目
3. 提取所有功能点、业务规则、约束条件
4. 分析前置/后置条件和异常处理
5. 识别需求间的依赖关系
6. 确保需求 ID 全局唯一且连续递增"""
    
    def _parse_json_response(self, response_text: str, original_content: str, source_name: str) -> RequirementParseResult:
        """解析 LLM 返回的 JSON"""
        
        # 清理可能的 markdown 代码块标记
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        try:
            data = json.loads(text.strip())
        except json.JSONDecodeError as e:
            return RequirementParseResult(
                original_content=original_content[:200] + "...",
                parsed_requirements=[],
                parse_summary=f"JSON 解析失败: {str(e)}",
                warnings=[f"JSON 解析失败: {str(e)}"],
                total_modules=0,
                total_function_points=0
            )
        
        # 转换为结构化需求对象
        parsed_requirements = []
        total_function_points = 0
        warnings = data.get("warnings", [])
        
        for module_data in data.get("modules", []):
            module_name = module_data.get("module_name", "")
            
            for req_data in module_data.get("requirements", []):
                req = self._convert_to_structured_requirement(req_data, module_name)
                parsed_requirements.append(req)
                total_function_points += len(req.function_points)
        
        return RequirementParseResult(
            original_content=original_content[:200] + "...",
            parsed_requirements=parsed_requirements,
            parse_summary=data.get("parse_summary", "解析完成"),
            warnings=warnings,
            total_modules=len(data.get("modules", [])),
            total_function_points=total_function_points
        )
    
    def _convert_to_structured_requirement(self, req_data: Dict, module_name: str) -> StructuredRequirement:
        """将 JSON 数据转换为 StructuredRequirement 对象"""
        
        # 转换功能点
        function_points = []
        for fp_data in req_data.get("function_points", []):
            function_points.append(FunctionPoint(
                id=fp_data.get("id", ""),
                description=fp_data.get("description", ""),
                business_rules=fp_data.get("business_rules", []),
                constraints=fp_data.get("constraints", []),
                priority=self._parse_priority(fp_data.get("priority", "中"))
            ))
        
        # 转换业务规则
        business_rules = []
        for br_data in req_data.get("business_rules", []):
            business_rules.append(BusinessRule(
                id=br_data.get("id", ""),
                description=br_data.get("description", ""),
                priority=self._parse_priority(br_data.get("priority", "中"))
            ))
        
        # 转换异常处理
        exception_handling = []
        for eh_data in req_data.get("exception_handling", []):
            exception_handling.append(ExceptionHandling(
                scenario=eh_data.get("scenario", ""),
                expected_handling=eh_data.get("expected_handling", "")
            ))
        
        # 变更历史
        change_history = [ChangeHistory(
            date=datetime.now().strftime("%Y-%m-%d"),
            action="创建",
            description="AI 自动解析生成",
            operator="AI"
        )]
        
        now = datetime.now()
        
        return StructuredRequirement(
            id=req_data.get("id", ""),
            title=req_data.get("title", ""),
            module=module_name,
            sub_module=req_data.get("sub_module"),
            priority=self._parse_priority(req_data.get("priority", "中")),
            status=RequirementStatus.NOT_STARTED,
            description=req_data.get("description", ""),
            function_points=function_points,
            preconditions=req_data.get("preconditions", []),
            postconditions=req_data.get("postconditions", []),
            business_rules=business_rules,
            exception_handling=exception_handling,
            prerequisite_requirements=req_data.get("prerequisite_requirements", []),
            dependent_requirements=req_data.get("dependent_requirements", []),
            tags=req_data.get("tags", []),
            change_history=change_history,
            created_at=now,
            updated_at=now
        )
    
    def _parse_priority(self, priority_str: str) -> Priority:
        """解析优先级字符串"""
        priority_map = {
            "高": Priority.HIGH,
            "中": Priority.MEDIUM,
            "低": Priority.LOW,
            "P0": Priority.HIGH,
            "P1": Priority.HIGH,
            "P2": Priority.MEDIUM,
            "P3": Priority.LOW
        }
        return priority_map.get(priority_str, Priority.MEDIUM)
    
    def save_structured_requirements(self, result: RequirementParseResult) -> List[str]:
        """
        保存结构化需求到文件
        
        Args:
            result: 需求解析结果
        
        Returns:
            保存的文件路径列表
        """
        saved_files = []
        updated_modules = set()
        
        for req in result.parsed_requirements:
            # 创建模块目录
            module_dir = self.output_dir / req.module
            module_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            file_name = f"{req.id}_{req.title}.md"
            # 替换文件名中的非法字符
            file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
            file_path = module_dir / file_name
            
            # 生成 Markdown 内容
            content = self._generate_requirement_markdown(req)
            
            # 写入文件
            file_path.write_text(content, encoding='utf-8')
            saved_files.append(str(file_path))
            updated_modules.add(req.module)
        
        # 更新需求索引文件
        self._update_requirements_index(result.parsed_requirements)

        return saved_files
    
    def _generate_requirement_markdown(self, req: StructuredRequirement) -> str:
        """生成需求 Markdown 文档"""
        
        lines = []
        lines.append(f"# {req.id}: {req.title}")
        lines.append("")
        lines.append("## 基本信息")
        lines.append(f"- **模块**: {req.module}")
        if req.sub_module:
            lines.append(f"- **子模块**: {req.sub_module}")
        lines.append(f"- **优先级**: {req.priority.value}")
        lines.append(f"- **状态**: {req.status.value}")
        if req.created_at:
            lines.append(f"- **创建时间**: {req.created_at.strftime('%Y-%m-%d')}")
        if req.updated_at:
            lines.append(f"- **更新时间**: {req.updated_at.strftime('%Y-%m-%d')}")
        lines.append("")
        
        lines.append("## 需求描述")
        lines.append(req.description)
        lines.append("")
        
        if req.function_points:
            lines.append("## 功能点")
            for i, fp in enumerate(req.function_points, 1):
                lines.append(f"{i}. {fp.description}")
                if fp.business_rules:
                    lines.append(f"   - 业务规则: {'; '.join(fp.business_rules)}")
                if fp.constraints:
                    lines.append(f"   - 约束条件: {'; '.join(fp.constraints)}")
            lines.append("")
        
        if req.preconditions:
            lines.append("## 前置条件")
            for condition in req.preconditions:
                lines.append(f"- {condition}")
            lines.append("")
        
        if req.postconditions:
            lines.append("## 后置条件")
            for condition in req.postconditions:
                lines.append(f"- {condition}")
            lines.append("")
        
        if req.business_rules:
            lines.append("## 业务规则")
            lines.append("| 规则编号 | 规则描述 | 优先级 |")
            lines.append("|---------|---------|--------|")
            for br in req.business_rules:
                lines.append(f"| {br.id} | {br.description} | {br.priority.value} |")
            lines.append("")
        
        if req.exception_handling:
            lines.append("## 异常处理")
            for eh in req.exception_handling:
                lines.append(f"- **{eh.scenario}**: {eh.expected_handling}")
            lines.append("")
        
        if req.tags:
            lines.append("## 标签")
            lines.append("、".join(req.tags))
            lines.append("")
        
        if req.prerequisite_requirements or req.dependent_requirements:
            lines.append("## 依赖关系")
            if req.prerequisite_requirements:
                lines.append(f"- 前置需求: {', '.join(req.prerequisite_requirements)}")
            if req.dependent_requirements:
                lines.append(f"- 后续需求: {', '.join(req.dependent_requirements)}")
            lines.append("")
        
        lines.append("## 变更历史")
        lines.append("| 日期 | 操作 | 说明 | 操作人 |")
        lines.append("|------|------|------|--------|")
        for ch in req.change_history:
            lines.append(f"| {ch.date} | {ch.action} | {ch.description} | {ch.operator} |")
        lines.append("")
        
        return "\n".join(lines)
    
    def _update_global_index(self, requirements: List[StructuredRequirement]):
        """更新全局需求索引"""
        index_file = self.output_dir / "_index.json"
        
        # 加载现有索引
        existing_index = {}
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            except:
                existing_index = {}
        
        # 更新索引
        if "requirements" not in existing_index:
            existing_index["requirements"] = []
            existing_index["modules"] = []
            existing_index["last_updated"] = ""
        
        # 按模块组织
        modules_set = set(existing_index.get("modules", []))
        
        for req in requirements:
            # 检查是否已存在（根据 ID）
            existing_req = next(
                (r for r in existing_index["requirements"] if r.get("id") == req.id),
                None
            )
            
            req_entry = {
                "id": req.id,
                "file": f"{req.id}_{req.title}.md",
                "module": req.module,
                "title": req.title,
                "priority": req.priority.value,
                "status": req.status.value,
                "function_points_count": len(req.function_points),
                "tags": req.tags
            }
            
            if existing_req:
                # 更新现有条目
                existing_req.update(req_entry)
            else:
                # 添加新条目
                existing_index["requirements"].append(req_entry)
            
            modules_set.add(req.module)
        
        existing_index["modules"] = sorted(list(modules_set))
        existing_index["last_updated"] = datetime.now().isoformat()
        
        # 写入索引文件
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(existing_index, f, ensure_ascii=False, indent=2)


# ============== 便捷函数 ==============

def parse_requirement_from_file(file_path: str, output_dir: str = None) -> RequirementParseResult:
    """
    从文件解析需求
    
    Args:
        file_path: 需求文件路径
        output_dir: 输出目录（默认为 qa_system/data/requirements/）
    
    Returns:
        需求解析结果
    """
    if output_dir is None:
        # 默认输出目录
        output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "requirements")
    
    parser = RequirementParser(output_dir)
    result = parser.parse_prd_file(file_path)
    
    # 保存结果
    if result.parsed_requirements:
        saved_files = parser.save_structured_requirements(result)
        print(f"✅ 成功解析 {len(result.parsed_requirements)} 个需求")
        print(f"📁 保存文件: {len(saved_files)} 个")
        for f in saved_files:
            print(f"   - {f}")
    
    return result


def parse_requirement_from_text(text: str, source_name: str = "未知来源", output_dir: str = None) -> RequirementParseResult:
    """
    从文本解析需求
    
    Args:
        text: 需求文本内容
        source_name: 来源名称
        output_dir: 输出目录
    
    Returns:
        需求解析结果
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "requirements")
    
    parser = RequirementParser(output_dir)
    result = parser.parse_prd_text(text, source_name)
    
    # 保存结果
    if result.parsed_requirements:
        saved_files = parser.save_structured_requirements(result)
        print(f"✅ 成功解析 {len(result.parsed_requirements)} 个需求")
        print(f"📁 保存文件: {len(saved_files)} 个")
    
    return result
