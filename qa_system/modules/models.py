"""
数据模型定义
包含需求、测试用例、BUG以及各模块的分析结果模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# ============== 枚举类型 ==============
class Priority(str, Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class RequirementStatus(str, Enum):
    COMPLETED = "已完成"
    IN_PROGRESS = "进行中"
    NOT_STARTED = "未开始"
    CHANGED = "已变更"
    DRAFT = "草稿"
    FORMAL = "正式文档"


class TestCaseStatus(str, Enum):
    EXECUTED = "已执行"
    NOT_EXECUTED = "未执行"
    EXECUTING = "执行中"
    BLOCKED = "阻塞"


class BugSeverity(str, Enum):
    CRITICAL = "严重"
    MAJOR = "一般"
    MINOR = "轻微"


class BugStatus(str, Enum):
    FIXED = "已修复"
    FIXING = "修复中"
    OPEN = "未修复"
    REJECTED = "已拒绝"
    REOPENED = "重新打开"


# ============== 核心数据模型 ==============
class Requirement(BaseModel):
    """需求模型"""
    id: str = Field(..., description="需求ID")
    title: str = Field(..., description="需求标题")
    description: str = Field(..., description="需求描述")
    module: str = Field(..., description="所属模块")
    sub_module: Optional[str] = Field(None, description="子模块")
    priority: Priority = Field(..., description="优先级")
    status: RequirementStatus = Field(..., description="状态")
    tags: List[str] = Field(default=[], description="标签")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    change_history: List[Dict[str, Any]] = Field(default=[], description="变更历史")


class TestStep(BaseModel):
    """测试步骤模型"""
    step_no: int = Field(default=1, description="步骤序号")
    action: str = Field(default="", description="操作描述")
    input: str = Field(default="", description="输入数据")
    expected: str = Field(default="", description="预期结果")


class TestCase(BaseModel):
    """测试用例模型"""
    id: str = Field(..., description="测试用例ID")
    title: str = Field(..., description="测试用例标题")
    description: str = Field(..., description="测试用例描述")
    requirement_id: str = Field(..., description="关联需求ID")
    module: str = Field(..., description="所属模块")
    priority: Priority = Field(..., description="优先级")
    status: TestCaseStatus = Field(..., description="执行状态")
    steps: List[Union[str, Dict[str, Any], TestStep]] = Field(default=[], description="测试步骤")
    expected_result: str = Field(..., description="期望结果")
    actual_result: Optional[str] = Field(None, description="实际结果")
    bugs_found: List[str] = Field(default=[], description="发现的BUG ID列表")
    execution_count: int = Field(default=0, description="执行次数")
    last_executed_at: Optional[datetime] = Field(None, description="最后执行时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class Bug(BaseModel):
    """BUG模型"""
    id: str = Field(..., description="BUG ID")
    title: str = Field(..., description="BUG标题")
    description: str = Field(..., description="BUG描述")
    test_case_id: Optional[str] = Field(None, description="关联测试用例ID")
    requirement_id: Optional[str] = Field(None, description="关联需求ID")
    module: str = Field(..., description="所属模块")
    severity: BugSeverity = Field(..., description="严重程度")
    status: BugStatus = Field(..., description="状态")
    root_cause: Optional[str] = Field(None, description="根因分析")
    root_cause_category: Optional[str] = Field(None, description="根因分类")
    fix_solution: Optional[str] = Field(None, description="修复方案")
    fixed_in_version: Optional[str] = Field(None, description="修复版本")
    assignee: Optional[str] = Field(None, description="指派人")
    reporter: Optional[str] = Field(None, description="报告人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    fixed_at: Optional[datetime] = Field(None, description="修复时间")


# ============== 需求拆解模块模型 ==============

class FunctionPoint(BaseModel):
    """功能点"""
    id: str = Field(..., description="功能点ID，如 FP-001")
    description: str = Field(..., description="功能点描述")
    business_rules: List[str] = Field(default=[], description="业务规则列表")
    constraints: List[str] = Field(default=[], description="约束条件")
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")


class BusinessRule(BaseModel):
    """业务规则"""
    id: str = Field(..., description="规则ID，如 BR-001")
    description: str = Field(..., description="规则描述")
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")


class ExceptionHandling(BaseModel):
    """异常处理"""
    scenario: str = Field(..., description="异常场景")
    expected_handling: str = Field(..., description="预期处理方式")


class ChangeHistory(BaseModel):
    """变更历史"""
    date: str = Field(..., description="变更日期")
    action: str = Field(..., description="操作（创建/修改/废弃）")
    description: str = Field(..., description="变更说明")
    operator: str = Field(default="", description="操作人")


class StructuredRequirement(BaseModel):
    """结构化需求"""
    id: str = Field(..., description="需求ID，如 REQ-001")
    title: str = Field(..., description="需求标题")
    module: str = Field(..., description="所属模块")
    sub_module: Optional[str] = Field(None, description="子模块")
    priority: Priority = Field(..., description="优先级")
    status: RequirementStatus = Field(..., description="状态")
    
    # 需求内容
    description: str = Field(..., description="需求详细描述")
    function_points: List[FunctionPoint] = Field(default=[], description="功能点列表")
    
    # 条件
    preconditions: List[str] = Field(default=[], description="前置条件")
    postconditions: List[str] = Field(default=[], description="后置条件")
    
    # 业务规则
    business_rules: List[BusinessRule] = Field(default=[], description="业务规则列表")
    
    # 异常处理
    exception_handling: List[ExceptionHandling] = Field(default=[], description="异常处理")
    
    # 依赖关系
    prerequisite_requirements: List[str] = Field(default=[], description="前置需求ID列表")
    dependent_requirements: List[str] = Field(default=[], description="后续需求ID列表")
    
    # 标签
    tags: List[str] = Field(default=[], description="标签")
    
    # 变更历史
    change_history: List[ChangeHistory] = Field(default=[], description="变更历史")
    
    # 审计信息
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class RequirementParseResult(BaseModel):
    """需求解析结果"""
    original_content: str = Field(..., description="原始内容摘要")
    parsed_requirements: List[StructuredRequirement] = Field(..., description="解析后的结构化需求")
    parse_summary: str = Field(..., description="解析总结")
    warnings: List[str] = Field(default=[], description="警告信息")
    total_modules: int = Field(default=0, description="识别的模块数")
    total_function_points: int = Field(default=0, description="识别的功能点数")


# ============== 质量分析模块模型 ==============
class ModuleQualityMetrics(BaseModel):
    """模块质量指标"""
    module: str = Field(..., description="模块名称")
    total_requirements: int = Field(default=0, description="需求总数")
    covered_requirements: int = Field(default=0, description="已覆盖需求数")
    requirement_coverage_rate: float = Field(default=0.0, description="需求覆盖率")
    total_test_cases: int = Field(default=0, description="测试用例总数")
    executed_test_cases: int = Field(default=0, description="已执行测试用例数")
    execution_rate: float = Field(default=0.0, description="执行率")
    total_bugs: int = Field(default=0, description="BUG总数")
    fixed_bugs: int = Field(default=0, description="已修复BUG数")
    bug_fix_rate: float = Field(default=0.0, description="BUG修复率")
    defect_density: float = Field(default=0.0, description="缺陷密度")
    risk_level: str = Field(default="低", description="风险等级")


class QualityAnalysisResult(BaseModel):
    """质量分析结果"""
    analysis_time: datetime = Field(..., description="分析时间")
    module_metrics: List[ModuleQualityMetrics] = Field(..., description="各模块质量指标")
    overall_defect_density: float = Field(..., description="整体缺陷密度")
    overall_requirement_coverage: float = Field(..., description="整体需求覆盖率")
    high_risk_modules: List[str] = Field(..., description="高风险模块列表")
    uncovered_requirements: List[str] = Field(default=[], description="未覆盖的需求ID")
    recommendations: List[str] = Field(default=[], description="建议")


class BugTrendPrediction(BaseModel):
    """BUG趋势预测"""
    date: str = Field(..., description="日期")
    actual_bugs: Optional[int] = Field(None, description="实际BUG数")
    predicted_bugs: int = Field(..., description="预测BUG数")
    confidence_interval: Optional[Dict[str, float]] = Field(None, description="置信区间")


class ModuleBugPrediction(BaseModel):
    """模块BUG预测"""
    module: str = Field(..., description="模块名称")
    historical_bug_rate: float = Field(..., description="历史BUG率")
    predicted_new_bugs: int = Field(..., description="预测新增BUG数")
    confidence: float = Field(..., description="置信度")
    risk_factors: List[str] = Field(default=[], description="风险因素")


# ============== AI辅助测试模块模型 ==============
class GeneratedTestCase(BaseModel):
    """生成的测试用例"""
    title: str = Field(..., description="测试用例标题")
    description: str = Field(..., description="测试用例描述")
    requirement_id: str = Field(..., description="关联需求ID")
    module: str = Field(..., description="所属模块")
    priority: Priority = Field(..., description="优先级")
    steps: List[str] = Field(..., description="测试步骤")
    expected_result: str = Field(..., description="期望结果")
    generation_reason: str = Field(..., description="生成原因")


class BugRootCauseAnalysis(BaseModel):
    """BUG根因分析结果"""
    bug_id: str = Field(..., description="BUG ID")
    bug_info: Dict[str, Any] = Field(..., description="BUG信息")
    recommended_root_causes: List[Dict[str, Any]] = Field(..., description="推荐的根因列表")
    similar_bugs: List[Dict[str, Any]] = Field(default=[], description="相似BUG")
    suggested_fix: str = Field(..., description="建议修复方案")
    confidence: float = Field(..., description="分析置信度")


class TestCaseRecommendation(BaseModel):
    """测试用例推荐"""
    test_case_id: str = Field(..., description="测试用例ID")
    test_case_title: str = Field(..., description="测试用例标题")
    module: str = Field(..., description="所属模块")
    relevance_score: float = Field(..., description="相关性分数")
    recommendation_reason: str = Field(..., description="推荐理由")
    historical_bugs_found: int = Field(default=0, description="历史发现BUG数")


class AIAssistedTestResult(BaseModel):
    """AI辅助测试结果"""
    generated_test_cases: List[GeneratedTestCase] = Field(default=[], description="生成的测试用例")
    bug_analysis: Optional[BugRootCauseAnalysis] = Field(None, description="BUG分析结果")
    recommended_test_cases: List[TestCaseRecommendation] = Field(default=[], description="推荐的测试用例")


# ============== 流程优化模块模型 ==============
class ChangeImpactAnalysis(BaseModel):
    """需求变更影响分析"""
    requirement_id: str = Field(..., description="需求ID")
    requirement_title: str = Field(..., description="需求标题")
    affected_test_cases: List[Dict[str, Any]] = Field(..., description="影响的测试用例")
    affected_bugs: List[Dict[str, Any]] = Field(..., description="影响的BUG")
    impact_level: str = Field(..., description="影响程度")
    recommendations: List[str] = Field(default=[], description="建议")


class PrioritizedTestCase(BaseModel):
    """优先级测试用例"""
    test_case_id: str = Field(..., description="测试用例ID")
    test_case_title: str = Field(..., description="测试用例标题")
    module: str = Field(..., description="所属模块")
    priority_score: float = Field(..., description="优先级分数")
    historical_bugs_found: int = Field(default=0, description="历史发现BUG数")
    last_executed_at: Optional[datetime] = Field(None, description="最后执行时间")
    execution_recommendation: str = Field(..., description="执行建议")


class InefficientTestCase(BaseModel):
    """低效用例"""
    test_case_id: str = Field(..., description="测试用例ID")
    test_case_title: str = Field(..., description="测试用例标题")
    module: str = Field(..., description="所属模块")
    execution_count: int = Field(default=0, description="执行次数")
    bugs_found: int = Field(default=0, description="发现BUG数")
    inefficiency_reason: str = Field(..., description="低效原因")
    suggestion: str = Field(..., description="优化建议")


class ProcessOptimizationResult(BaseModel):
    """流程优化结果"""
    change_impact: Optional[ChangeImpactAnalysis] = Field(None, description="变更影响分析")
    prioritized_test_cases: List[PrioritizedTestCase] = Field(default=[], description="优先级测试用例")
    inefficient_test_cases: List[InefficientTestCase] = Field(default=[], description="低效用例")
    resource_allocation_suggestions: List[str] = Field(default=[], description="资源分配建议")


# ============== 知识管理模块模型 ==============
class TrainingMaterial(BaseModel):
    """培训材料"""
    module: str = Field(..., description="模块名称")
    overview: str = Field(..., description="模块概述")
    requirements_summary: List[Dict[str, Any]] = Field(..., description="需求摘要")
    test_cases_summary: List[Dict[str, Any]] = Field(..., description="测试用例摘要")
    common_bugs: List[Dict[str, Any]] = Field(..., description="常见BUG")
    best_practices: List[str] = Field(default=[], description="最佳实践")


class HistoricalBugCase(BaseModel):
    """历史BUG案例"""
    bug_id: str = Field(..., description="BUG ID")
    title: str = Field(..., description="标题")
    module: str = Field(..., description="模块")
    severity: BugSeverity = Field(..., description="严重程度")
    root_cause: Optional[str] = Field(None, description="根因")
    fix_solution: Optional[str] = Field(None, description="修复方案")
    lessons_learned: List[str] = Field(default=[], description="经验教训")


class KnowledgeSearchResult(BaseModel):
    """知识搜索结果"""
    result_type: str = Field(..., description="结果类型")
    id: str = Field(..., description="ID")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    module: str = Field(..., description="模块")
    relevance_score: float = Field(..., description="相关性分数")
    full_data: Dict[str, Any] = Field(..., description="完整数据")


class KnowledgeManagementResult(BaseModel):
    """知识管理结果"""
    training_materials: List[TrainingMaterial] = Field(default=[], description="培训材料")
    historical_bugs: List[HistoricalBugCase] = Field(default=[], description="历史BUG案例")
    search_results: List[KnowledgeSearchResult] = Field(default=[], description="搜索结果")
    qa_pairs: List[Dict[str, str]] = Field(default=[], description="问答对")


# ============== 智能报告模块模型 ==============
class ModuleReport(BaseModel):
    """模块报告"""
    module: str = Field(..., description="模块名称")
    quality_score: float = Field(..., description="质量得分")
    requirement_coverage: float = Field(..., description="需求覆盖率")
    defect_density: float = Field(..., description="缺陷密度")
    bug_fix_rate: float = Field(..., description="BUG修复率")
    total_requirements: int = Field(..., description="需求总数")
    total_test_cases: int = Field(..., description="测试用例总数")
    total_bugs: int = Field(..., description="BUG总数")
    fixed_bugs: int = Field(..., description="已修复BUG数")
    risk_assessment: str = Field(..., description="风险评估")
    recommendations: List[str] = Field(default=[], description="建议")


class ProjectQualityReport(BaseModel):
    """项目质量报告"""
    report_time: datetime = Field(..., description="报告时间")
    project_quality_score: float = Field(..., description="项目质量得分")
    overall_defect_density: float = Field(..., description="整体缺陷密度")
    overall_requirement_coverage: float = Field(..., description="整体需求覆盖率")
    bug_statistics: Dict[str, Any] = Field(..., description="BUG统计")
    high_risk_modules: List[ModuleReport] = Field(..., description="高风险模块报告")
    bug_trend: List[BugTrendPrediction] = Field(..., description="BUG趋势")
    test_execution_summary: Dict[str, Any] = Field(..., description="测试执行摘要")
    recommendations: List[str] = Field(..., description="建议")
    executive_summary: str = Field(..., description="执行摘要")


class IssueType(str, Enum):
    MISSING_INFO = "缺失信息"
    VAGUE_DESCRIPTION = "模糊描述"
    CONTRADICTION = "矛盾冲突"
    INCOMPLETE = "不完整"
    UNREASONABLE_PRIORITY = "优先级不合理"
    MISSING_PRECONDITIONS = "缺少前置条件"
    MISSING_EXCEPTION_HANDLING = "缺少异常处理"
    UNCLEAR_SCOPE = "范围不清晰"


class IssueSeverity(str, Enum):
    CRITICAL = "严重"
    MAJOR = "一般"
    MINOR = "轻微"


class RequirementIssue(BaseModel):
    requirement_issue_id: str = Field(..., description="问题ID")
    issue_type: IssueType = Field(..., description="问题类型")
    severity: IssueSeverity = Field(..., description="严重程度")
    field_name: str = Field(..., description="问题字段名称")
    description: str = Field(..., description="问题描述")
    suggestion: str = Field(..., description="改进建议")
    location: Optional[str] = Field(None, description="问题位置")


class RequirementAnalysisResult(BaseModel):
    original_content: str = Field(..., description="原始内容摘要")
    issues: List[RequirementIssue] = Field(default=[], description="检测到的问题列表")
    parsed_requirements: List[StructuredRequirement] = Field(default=[], description="解析后的结构化需求")
    analysis_summary: str = Field(..., description="分析总结")
    total_issues: int = Field(default=0, description="问题总数")
    critical_issues: int = Field(default=0, description="严重问题数")
    major_issues: int = Field(default=0, description="一般问题数")
    minor_issues: int = Field(default=0, description="轻微问题数")
    total_modules: int = Field(default=0, description="识别的模块数")
    total_function_points: int = Field(default=0, description="识别的功能点数")


# ============== 草稿版本管理模型 ==============

class DraftVersionInfo(BaseModel):
    """草稿版本信息"""
    version_id: str = Field(..., description="版本ID")
    parent_id: Optional[str] = Field(None, description="父版本ID")
    version_number: int = Field(..., description="版本号")
    is_draft: bool = Field(..., description="是否为草稿")
    content: Dict[str, Any] = Field(default={}, description="版本内容")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    comment: str = Field(default="", description="版本注释")


class DraftMetadata(BaseModel):
    """草稿元数据"""
    draft_id: str = Field(..., description="草稿ID")
    source_name: str = Field(..., description="来源名称")
    status: str = Field(default="draft", description="状态: draft/formal")
    current_version: Optional[DraftVersionInfo] = Field(None, description="当前版本")
    versions: List[DraftVersionInfo] = Field(default=[], description="版本历史")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    formal_files: List[str] = Field(default=[], description="发布的正式文件路径")


class DraftSummary(BaseModel):
    """草稿摘要(用于列表展示)"""
    draft_id: str = Field(..., description="草稿ID")
    source_name: str = Field(..., description="来源名称")
    status: str = Field(..., description="状态")
    version: int = Field(..., description="当前版本号")
    total_requirements: int = Field(..., description="需求总数")
    total_issues: int = Field(..., description="问题总数")
    modules: List[str] = Field(default=[], description="涉及的模块列表")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
