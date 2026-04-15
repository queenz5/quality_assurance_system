"""
需求分析器模块
分析需求文档，检测问题并生成结构化需求

功能：
1. 检测需求文档存在的问题（缺失信息、模糊描述、矛盾冲突等）
2. 解析需求文档为结构化数据
3. 提供改进建议
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from modules.models import (
    StructuredRequirement, FunctionPoint, BusinessRule, ExceptionHandling,
    ChangeHistory, RequirementStatus, Priority,
    RequirementAnalysisResult, RequirementIssue, IssueType, IssueSeverity
)
from modules.requirement_parser import RequirementParser


class RequirementAnalyzer:
    """需求分析器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化需求分析器
        
        Args:
            output_dir: 结构化需求输出目录
        """
        self.parser = RequirementParser(output_dir)
        self.issue_counter = 0
    
    def _generate_issue_id(self) -> str:
        """生成问题ID"""
        self.issue_counter += 1
        return f"ISSUE-{self.issue_counter:03d}"
    
    def analyze_requirement_document(self, content: str, source_name: str = "未知来源") -> RequirementAnalysisResult:
        """
        分析需求文档
        
        Args:
            content: 需求文档内容
            source_name: 来源名称
        
        Returns:
            需求分析结果（包含问题列表和结构化需求）
        """
        self.issue_counter = 0
        
        issues = []
        
        issues.extend(self._detect_missing_info(content))
        issues.extend(self._detect_vague_descriptions(content))
        issues.extend(self._detect_incomplete_content(content))
        issues.extend(self._detect_missing_preconditions(content))
        issues.extend(self._detect_missing_exception_handling(content))
        issues.extend(self._detect_unclear_scope(content))
        
        parse_result = self.parser.parse_prd_text(content, source_name)
        
        for req in parse_result.parsed_requirements:
            issues.extend(self._analyze_structured_requirement(req))
        
        critical_count = sum(1 for issue in issues if issue.severity == IssueSeverity.CRITICAL)
        major_count = sum(1 for issue in issues if issue.severity == IssueSeverity.MAJOR)
        minor_count = sum(1 for issue in issues if issue.severity == IssueSeverity.MINOR)
        
        analysis_summary = self._generate_analysis_summary(
            len(issues), critical_count, major_count, minor_count,
            len(parse_result.parsed_requirements), parse_result.total_modules
        )
        
        return RequirementAnalysisResult(
            original_content=content[:200] + "..." if len(content) > 200 else content,
            issues=issues,
            parsed_requirements=parse_result.parsed_requirements,
            analysis_summary=analysis_summary,
            total_issues=len(issues),
            critical_issues=critical_count,
            major_issues=major_count,
            minor_issues=minor_count,
            total_modules=parse_result.total_modules,
            total_function_points=parse_result.total_function_points
        )
    
    def _detect_missing_info(self, content: str) -> List[RequirementIssue]:
        """检测缺失信息"""
        issues = []
        
        required_sections = {
            "需求描述": ["需求描述", "功能描述", "需求说明"],
            "功能点": ["功能点", "功能列表", "功能清单"],
            "前置条件": ["前置条件", "前提条件", "前置要求"],
            "后置条件": ["后置条件", "后续条件", "结果状态"],
            "业务规则": ["业务规则", "业务逻辑", "业务约束"],
        }
        
        for section_name, keywords in required_sections.items():
            found = any(keyword in content for keyword in keywords)
            if not found:
                issues.append(RequirementIssue(
                    requirement_issue_id=self._generate_issue_id(),
                    issue_type=IssueType.MISSING_INFO,
                    severity=IssueSeverity.MAJOR,
                    field_name=section_name,
                    description=f"文档中缺少 '{section_name}' 相关内容",
                    suggestion=f"建议添加 '{section_name}' 章节，详细说明相关内容"
                ))
        
        return issues
    
    def _detect_vague_descriptions(self, content: str) -> List[RequirementIssue]:
        """检测模糊描述"""
        issues = []
        
        vague_patterns = [
            (r"等\s*等", "使用了'等等'等模糊表述"),
            (r"之类", "使用了'之类'等模糊表述"),
            (r"可能", "使用了'可能'等不确定表述"),
            (r"大概", "使用了'大概'等不确定表述"),
            (r"差不多", "使用了'差不多'等模糊表述"),
            (r"一些\s*功能", "使用了'一些功能'等模糊表述"),
            (r"相关\s*功能", "使用了'相关功能'等模糊表述"),
            (r"若干", "使用了'若干'等模糊数量词"),
        ]
        
        for pattern, description in vague_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                context_start = max(0, match.start() - 20)
                context_end = min(len(content), match.end() + 20)
                context = content[context_start:context_end]
                
                issues.append(RequirementIssue(
                    requirement_issue_id=self._generate_issue_id(),
                    issue_type=IssueType.VAGUE_DESCRIPTION,
                    severity=IssueSeverity.MINOR,
                    field_name="需求描述",
                    description=description,
                    suggestion="建议使用更精确、具体的描述，避免模糊表述",
                    location=context
                ))
        
        return issues
    
    def _detect_incomplete_content(self, content: str) -> List[RequirementIssue]:
        """检测不完整内容"""
        issues = []
        
        if len(content.strip()) < 100:
            issues.append(RequirementIssue(
                requirement_issue_id=self._generate_issue_id(),
                issue_type=IssueType.INCOMPLETE,
                severity=IssueSeverity.CRITICAL,
                field_name="整体内容",
                description="需求文档内容过短，可能不完整",
                suggestion="建议补充完整的需求说明，包括功能描述、业务规则、约束条件等"
            ))
        
        incomplete_markers = [
            "待补充", "待完善", "TODO", "TBD", "暂未确定", "后续补充"
        ]
        
        for marker in incomplete_markers:
            if marker in content:
                issues.append(RequirementIssue(
                    requirement_issue_id=self._generate_issue_id(),
                    issue_type=IssueType.INCOMPLETE,
                    severity=IssueSeverity.MAJOR,
                    field_name="整体内容",
                    description=f"发现未完成标记: '{marker}'",
                    suggestion="建议完善所有标记为待补充的内容"
                ))
        
        return issues
    
    def _detect_missing_preconditions(self, content: str) -> List[RequirementIssue]:
        """检测缺少前置条件"""
        issues = []
        
        precondition_keywords = ["前置条件", "前提条件", "前置要求", "前置依赖"]
        has_preconditions = any(keyword in content for keyword in precondition_keywords)
        
        if not has_preconditions:
            if "登录" in content or "注册" in content or "下单" in content or "支付" in content:
                issues.append(RequirementIssue(
                    requirement_issue_id=self._generate_issue_id(),
                    issue_type=IssueType.MISSING_PRECONDITIONS,
                    severity=IssueSeverity.MAJOR,
                    field_name="前置条件",
                    description="文档中缺少前置条件说明",
                    suggestion="建议添加前置条件章节，说明使用该功能前需要满足的条件"
                ))
        
        return issues
    
    def _detect_missing_exception_handling(self, content: str) -> List[RequirementIssue]:
        """检测缺少异常处理"""
        issues = []
        
        exception_keywords = ["异常处理", "异常情况", "错误处理", "失败处理", "异常场景"]
        has_exception = any(keyword in content for keyword in exception_keywords)
        
        if not has_exception:
            if "登录" in content or "支付" in content or "订单" in content:
                issues.append(RequirementIssue(
                    requirement_issue_id=self._generate_issue_id(),
                    issue_type=IssueType.MISSING_EXCEPTION_HANDLING,
                    severity=IssueSeverity.MAJOR,
                    field_name="异常处理",
                    description="文档中缺少异常处理说明",
                    suggestion="建议添加异常处理章节，说明可能出现的异常情况及处理方式"
                ))
        
        return issues
    
    def _detect_unclear_scope(self, content: str) -> List[RequirementIssue]:
        """检测范围不清晰"""
        issues = []
        
        if "模块" not in content and "功能模块" not in content:
            issues.append(RequirementIssue(
                requirement_issue_id=self._generate_issue_id(),
                issue_type=IssueType.UNCLEAR_SCOPE,
                severity=IssueSeverity.MINOR,
                field_name="模块划分",
                description="文档中缺少模块划分说明",
                suggestion="建议明确功能模块划分，说明各模块的职责和边界"
            ))
        
        return issues
    
    def _analyze_structured_requirement(self, req: StructuredRequirement) -> List[RequirementIssue]:
        """分析结构化需求"""
        issues = []
        
        if not req.description or len(req.description.strip()) < 20:
            issues.append(RequirementIssue(
                requirement_issue_id=self._generate_issue_id(),
                issue_type=IssueType.MISSING_INFO,
                severity=IssueSeverity.MAJOR,
                field_name="需求描述",
                description=f"需求 {req.id} 的描述过于简短或缺失",
                suggestion="建议补充详细的需求描述，说明功能的目的、作用和预期效果",
                location=f"需求ID: {req.id}"
            ))
        
        if not req.function_points or len(req.function_points) == 0:
            issues.append(RequirementIssue(
                requirement_issue_id=self._generate_issue_id(),
                issue_type=IssueType.MISSING_INFO,
                severity=IssueSeverity.MAJOR,
                field_name="功能点",
                description=f"需求 {req.id} 缺少功能点说明",
                suggestion="建议添加功能点列表，详细说明该需求包含的具体功能",
                location=f"需求ID: {req.id}"
            ))
        
        if not req.preconditions or len(req.preconditions) == 0:
            issues.append(RequirementIssue(
                requirement_issue_id=self._generate_issue_id(),
                issue_type=IssueType.MISSING_PRECONDITIONS,
                severity=IssueSeverity.MINOR,
                field_name="前置条件",
                description=f"需求 {req.id} 缺少前置条件",
                suggestion="建议添加前置条件，说明使用该功能前需要满足的条件",
                location=f"需求ID: {req.id}"
            ))
        
        if not req.exception_handling or len(req.exception_handling) == 0:
            issues.append(RequirementIssue(
                requirement_issue_id=self._generate_issue_id(),
                issue_type=IssueType.MISSING_EXCEPTION_HANDLING,
                severity=IssueSeverity.MINOR,
                field_name="异常处理",
                description=f"需求 {req.id} 缺少异常处理说明",
                suggestion="建议添加异常处理，说明可能出现的异常情况及处理方式",
                location=f"需求ID: {req.id}"
            ))
        
        return issues
    
    def _generate_analysis_summary(
        self, 
        total_issues: int, 
        critical: int, 
        major: int, 
        minor: int,
        total_requirements: int,
        total_modules: int
    ) -> str:
        """生成分析总结"""
        summary_parts = []
        
        summary_parts.append(f"共识别 {total_modules} 个模块，{total_requirements} 个需求。")
        
        if total_issues > 0:
            summary_parts.append(f"检测到 {total_issues} 个问题：")
            if critical > 0:
                summary_parts.append(f"严重问题 {critical} 个")
            if major > 0:
                summary_parts.append(f"一般问题 {major} 个")
            if minor > 0:
                summary_parts.append(f"轻微问题 {minor} 个")
            
            if critical > 0:
                summary_parts.append("建议优先解决严重问题，确保需求文档的完整性。")
            elif major > 0:
                summary_parts.append("建议解决一般问题，提高需求文档质量。")
            else:
                summary_parts.append("需求文档整体质量良好，建议优化轻微问题。")
        else:
            summary_parts.append("未检测到明显问题，需求文档质量良好。")
        
        return " ".join(summary_parts)


def analyze_requirement(content: str, source_name: str = "未知来源", output_dir: str = None) -> RequirementAnalysisResult:
    """
    分析需求文档的便捷函数
    
    Args:
        content: 需求文档内容
        source_name: 来源名称
        output_dir: 输出目录
    
    Returns:
        需求分析结果
    """
    analyzer = RequirementAnalyzer(output_dir)
    return analyzer.analyze_requirement_document(content, source_name)
