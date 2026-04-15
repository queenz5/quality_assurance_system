"""
需求分析服务层模块
统一编排需求分析和解析流程,提供完整的草稿管理功能

功能:
1. 分析需求文档,检测问题
2. 解析为结构化需求
3. 草稿管理(创建、更新、删除、保存、发布)
4. 版本管理
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from modules.models import (
    StructuredRequirement, FunctionPoint, BusinessRule, ExceptionHandling,
    ChangeHistory, RequirementParseResult, RequirementStatus, Priority,
    RequirementAnalysisResult, RequirementIssue, IssueType, IssueSeverity
)
from modules.requirement_analyzer import RequirementAnalyzer
from modules.requirement_parser import RequirementParser


class DraftVersion:
    """草稿版本模型"""
    def __init__(
        self,
        version_id: str,
        parent_id: Optional[str] = None,
        version_number: int = 1,
        is_draft: bool = True,
        content: Optional[Dict] = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        comment: str = ""
    ):
        self.version_id = version_id
        self.parent_id = parent_id
        self.version_number = version_number
        self.is_draft = is_draft
        self.content = content or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.comment = comment

    def to_dict(self) -> Dict:
        return {
            "version_id": self.version_id,
            "parent_id": self.parent_id,
            "version_number": self.version_number,
            "is_draft": self.is_draft,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "comment": self.comment
        }


class RequirementAnalysisService:
    """需求分析服务层"""

    def __init__(self, data_dir: str = None):
        """
        初始化服务

        Args:
            data_dir: 数据存储目录
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
        self.data_dir = Path(data_dir)
        self.drafts_dir = self.data_dir / "drafts"
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建分析器和解析器
        self.analyzer = RequirementAnalyzer()
        self.parser = RequirementParser()

    def analyze_and_parse(
        self, 
        content: str, 
        source_name: str = "未知来源"
    ) -> RequirementAnalysisResult:
        """
        分析并解析需求文档
        
        Args:
            content: 需求文档内容
            source_name: 来源名称
            
        Returns:
            分析结果(包含问题列表和结构化需求)
        """
        # 调用分析器
        result = self.analyzer.analyze_requirement_document(content, source_name)
        
        return result

    def create_draft(
        self,
        analysis_result: RequirementAnalysisResult,
        source_name: str = "未知来源",
        comment: str = ""
    ) -> str:
        """
        创建草稿
        
        Args:
            analysis_result: 分析结果
            source_name: 来源名称
            comment: 版本注释
            
        Returns:
            草稿ID
        """
        draft_id = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"
        version_id = f"V1"
        
        # 构建草稿内容
        content = {
            "draft_id": draft_id,
            "source_name": source_name,
            "original_content": analysis_result.original_content,
            "issues": [
                {
                    "id": issue.requirement_issue_id,
                    "type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "field_name": issue.field_name,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "location": issue.location
                }
                for issue in analysis_result.issues
            ],
            "requirements": [
                self._requirement_to_dict(req)
                for req in analysis_result.parsed_requirements
            ],
            "analysis_summary": analysis_result.analysis_summary,
            "total_issues": analysis_result.total_issues,
            "critical_issues": analysis_result.critical_issues,
            "major_issues": analysis_result.major_issues,
            "minor_issues": analysis_result.minor_issues,
            "total_modules": analysis_result.total_modules,
            "total_function_points": analysis_result.total_function_points
        }
        
        # 创建版本
        version = DraftVersion(
            version_id=version_id,
            version_number=1,
            is_draft=True,
            content=content,
            comment=comment or "AI自动解析生成"
        )
        
        # 保存草稿
        draft_data = {
            "draft_id": draft_id,
            "source_name": source_name,
            "title": content.get("requirements", [{}])[0].get("title", "未命名") if content.get("requirements") else "未命名",
            "module": content.get("requirements", [{}])[0].get("module", "未分类") if content.get("requirements") else "未分类",
            "current_version": version.to_dict(),
            "versions": [version.to_dict()],
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        draft_file = self.drafts_dir / f"{draft_id}.json"
        with open(draft_file, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, ensure_ascii=False, indent=2)
        
        return draft_id

    def get_draft(self, draft_id: str) -> Optional[Dict]:
        """
        获取草稿详情
        
        Args:
            draft_id: 草稿ID
            
        Returns:
            草稿数据
        """
        draft_file = self.drafts_dir / f"{draft_id}.json"
        
        if not draft_file.exists():
            return None
        
        with open(draft_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_drafts(self, module: str = None) -> List[Dict]:
        """
        获取草稿列表
        
        Args:
            module: 按模块筛选(可选)
            
        Returns:
            草稿列表
        """
        drafts = []
        
        for draft_file in self.drafts_dir.glob("DRAFT-*.json"):
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)
                
                # 如果指定了module,筛选
                if module:
                    requirements = draft_data.get("current_version", {}).get("content", {}).get("requirements", [])
                    if not any(req.get("module") == module for req in requirements):
                        continue
                
                # 提取摘要信息
                content = draft_data.get("current_version", {}).get("content", {})
                requirements = content.get("requirements", [])
                
                drafts.append({
                    "draft_id": draft_data.get("draft_id"),
                    "source_name": draft_data.get("source_name"),
                    "status": draft_data.get("status"),
                    "total_requirements": len(requirements),
                    "total_issues": content.get("total_issues", 0),
                    "modules": list(set(req.get("module") for req in requirements)),
                    "created_at": draft_data.get("created_at"),
                    "updated_at": draft_data.get("updated_at")
                })
            except Exception as e:
                print(f"⚠️ 读取草稿文件失败 {draft_file}: {e}")
        
        # 按更新时间倒序排序
        drafts.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return drafts

    def update_draft(
        self,
        draft_id: str,
        requirements: List[Dict],
        comment: str = ""
    ) -> bool:
        """
        更新草稿
        
        Args:
            draft_id: 草稿ID
            requirements: 更新后的需求列表
            comment: 版本注释
            
        Returns:
            是否成功
        """
        draft_data = self.get_draft(draft_id)
        
        if not draft_data:
            return False
        
        # 获取当前版本
        current_version = draft_data.get("current_version", {})
        content = current_version.get("content", {})
        
        # 创建新版本
        new_version_number = current_version.get("version_number", 1) + 1
        new_version_id = f"V{new_version_number}"
        
        # 更新内容
        content["requirements"] = requirements
        
        new_version = DraftVersion(
            version_id=new_version_id,
            parent_id=current_version.get("version_id"),
            version_number=new_version_number,
            is_draft=True,
            content=content,
            comment=comment or "手动编辑"
        )
        
        # 添加到版本历史
        draft_data["versions"].append(new_version.to_dict())
        draft_data["current_version"] = new_version.to_dict()
        draft_data["updated_at"] = datetime.now().isoformat()
        
        # 保存
        draft_file = self.drafts_dir / f"{draft_id}.json"
        with open(draft_file, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, ensure_ascii=False, indent=2)
        
        return True

    def delete_draft(self, draft_id: str) -> bool:
        """
        删除草稿
        
        Args:
            draft_id: 草稿ID
            
        Returns:
            是否成功
        """
        draft_file = self.drafts_dir / f"{draft_id}.json"
        
        if not draft_file.exists():
            return False
        
        try:
            draft_file.unlink()
            return True
        except Exception as e:
            print(f"❌ 删除草稿失败: {e}")
            return False

    def save_as_draft(
        self,
        content: str,
        source_name: str = "未知来源",
        draft_id: str = None,
        comment: str = ""
    ) -> str:
        """
        保存分析结果为草稿(如果draft_id存在则更新,否则创建)
        
        Args:
            content: 需求文档内容
            source_name: 来源名称
            draft_id: 草稿ID(如果存在则更新)
            comment: 版本注释
            
        Returns:
            草稿ID
        """
        # 分析和解析
        analysis_result = self.analyze_and_parse(content, source_name)
        
        if draft_id:
            # 更新现有草稿
            draft_data = self.get_draft(draft_id)
            if draft_data:
                # 更新当前版本内容
                current_version = draft_data.get("current_version", {})
                content_data = current_version.get("content", {})
                content_data["original_content"] = analysis_result.original_content
                content_data["issues"] = [
                    {
                        "id": issue.requirement_issue_id,
                        "type": issue.issue_type.value,
                        "severity": issue.severity.value,
                        "field_name": issue.field_name,
                        "description": issue.description,
                        "suggestion": issue.suggestion,
                        "location": issue.location
                    }
                    for issue in analysis_result.issues
                ]
                content_data["requirements"] = [
                    self._requirement_to_dict(req)
                    for req in analysis_result.parsed_requirements
                ]
                content_data["analysis_summary"] = analysis_result.analysis_summary
                content_data["total_issues"] = analysis_result.total_issues
                content_data["critical_issues"] = analysis_result.critical_issues
                content_data["major_issues"] = analysis_result.major_issues
                content_data["minor_issues"] = analysis_result.minor_issues
                content_data["total_modules"] = analysis_result.total_modules
                content_data["total_function_points"] = analysis_result.total_function_points
                
                # 创建新版本
                new_version_number = current_version.get("version_number", 1) + 1
                new_version = DraftVersion(
                    version_id=f"V{new_version_number}",
                    parent_id=current_version.get("version_id"),
                    version_number=new_version_number,
                    is_draft=True,
                    content=content_data,
                    comment=comment or "重新分析"
                )
                
                draft_data["versions"].append(new_version.to_dict())
                draft_data["current_version"] = new_version.to_dict()
                draft_data["updated_at"] = datetime.now().isoformat()
                
                # 保存
                draft_file = self.drafts_dir / f"{draft_id}.json"
                with open(draft_file, 'w', encoding='utf-8') as f:
                    json.dump(draft_data, f, ensure_ascii=False, indent=2)
                
                return draft_id
        
        # 创建新草稿
        return self.create_draft(analysis_result, source_name, comment)

    def publish_to_formal(
        self,
        draft_id: str,
        target_dir: str = None
    ) -> Tuple[bool, List[str]]:
        """
        将草稿发布为正式文档
        
        Args:
            draft_id: 草稿ID
            target_dir: 目标目录(默认为 data/requirements)
            
        Returns:
            (是否成功, 保存的文件路径列表)
        """
        draft_data = self.get_draft(draft_id)
        
        if not draft_data:
            return False, []
        
        content = draft_data.get("current_version", {}).get("content", {})
        requirements = content.get("requirements", [])
        
        if not requirements:
            return False, []
        
        # 确定目标目录
        if target_dir is None:
            target_dir = self.data_dir / "requirements"
        else:
            target_dir = Path(target_dir)
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存为正式文档
        saved_files = []
        saved_requirements = []

        for req_data in requirements:
            try:
                # 转换为 StructuredRequirement
                req = self._dict_to_requirement(req_data)

                # 创建模块目录
                module_dir = target_dir / req.module
                module_dir.mkdir(parents=True, exist_ok=True)

                # 生成文件名
                file_name = f"{req.id}_{req.title}.md"
                file_name = file_name.replace('/', '_').replace('\\', '_')
                file_path = module_dir / file_name

                # 生成 Markdown 内容
                markdown_content = self._generate_markdown(req)

                # 写入文件
                file_path.write_text(markdown_content, encoding='utf-8')
                saved_files.append(str(file_path))
                saved_requirements.append(req)

            except Exception as e:
                print(f"❌ 保存需求 {req_data.get('id')} 失败: {e}")

        # 更新需求索引
        if saved_requirements:
            from modules.requirement_parser import RequirementParser
            parser = RequirementParser(output_dir=str(target_dir))
            parser._update_requirements_index(saved_requirements)
        
        # 更新草稿状态
        if saved_files:
            draft_data["status"] = "formal"
            draft_data["current_version"]["is_draft"] = False
            draft_data["current_version"]["comment"] = "已发布为正式文档"
            draft_data["updated_at"] = datetime.now().isoformat()
            draft_data["formal_files"] = saved_files
            
            draft_file = self.drafts_dir / f"{draft_id}.json"
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False, indent=2)
        
        return len(saved_files) > 0, saved_files

    def _requirement_to_dict(self, req: StructuredRequirement) -> Dict:
        """将StructuredRequirement转换为字典"""
        return {
            "id": req.id,
            "title": req.title,
            "module": req.module,
            "sub_module": req.sub_module,
            "priority": req.priority.value,
            "status": req.status.value,
            "description": req.description,
            "function_points": [
                {
                    "id": fp.id,
                    "description": fp.description,
                    "business_rules": fp.business_rules,
                    "constraints": fp.constraints,
                    "priority": fp.priority.value
                }
                for fp in req.function_points
            ],
            "preconditions": req.preconditions,
            "postconditions": req.postconditions,
            "business_rules": [
                {
                    "id": br.id,
                    "description": br.description,
                    "priority": br.priority.value
                }
                for br in req.business_rules
            ],
            "exception_handling": [
                {
                    "scenario": eh.scenario,
                    "expected_handling": eh.expected_handling
                }
                for eh in req.exception_handling
            ],
            "prerequisite_requirements": req.prerequisite_requirements,
            "dependent_requirements": req.dependent_requirements,
            "tags": req.tags,
            "change_history": [
                {
                    "date": ch.date,
                    "action": ch.action,
                    "description": ch.description,
                    "operator": ch.operator
                }
                for ch in req.change_history
            ],
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "updated_at": req.updated_at.isoformat() if req.updated_at else None
        }

    def _dict_to_requirement(self, data: Dict) -> StructuredRequirement:
        """将字典转换为StructuredRequirement"""
        # 转换功能点
        function_points = []
        for fp_data in data.get("function_points", []):
            function_points.append(FunctionPoint(
                id=fp_data.get("id", ""),
                description=fp_data.get("description", ""),
                business_rules=fp_data.get("business_rules", []),
                constraints=fp_data.get("constraints", []),
                priority=self._parse_priority(fp_data.get("priority", "中"))
            ))
        
        # 转换业务规则
        business_rules = []
        for br_data in data.get("business_rules", []):
            business_rules.append(BusinessRule(
                id=br_data.get("id", ""),
                description=br_data.get("description", ""),
                priority=self._parse_priority(br_data.get("priority", "中"))
            ))
        
        # 转换异常处理
        exception_handling = []
        for eh_data in data.get("exception_handling", []):
            exception_handling.append(ExceptionHandling(
                scenario=eh_data.get("scenario", ""),
                expected_handling=eh_data.get("expected_handling", "")
            ))
        
        # 变更历史
        change_history = []
        for ch_data in data.get("change_history", []):
            change_history.append(ChangeHistory(
                date=ch_data.get("date", ""),
                action=ch_data.get("action", ""),
                description=ch_data.get("description", ""),
                operator=ch_data.get("operator", "")
            ))
        
        # 如果没有变更历史,添加默认记录
        if not change_history:
            change_history.append(ChangeHistory(
                date=datetime.now().strftime("%Y-%m-%d"),
                action="创建",
                description="草稿发布",
                operator="系统"
            ))
        
        # 解析时间
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data.get("created_at"))
            except:
                pass
        
        updated_at = None
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data.get("updated_at"))
            except:
                pass
        
        return StructuredRequirement(
            id=data.get("id", ""),
            title=data.get("title", ""),
            module=data.get("module", ""),
            sub_module=data.get("sub_module"),
            priority=self._parse_priority(data.get("priority", "中")),
            status=RequirementStatus.FORMAL,
            description=data.get("description", ""),
            function_points=function_points,
            preconditions=data.get("preconditions", []),
            postconditions=data.get("postconditions", []),
            business_rules=business_rules,
            exception_handling=exception_handling,
            prerequisite_requirements=data.get("prerequisite_requirements", []),
            dependent_requirements=data.get("dependent_requirements", []),
            tags=data.get("tags", []),
            change_history=change_history,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
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

    def _generate_markdown(self, req: StructuredRequirement) -> str:
        """生成需求Markdown文档"""
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
