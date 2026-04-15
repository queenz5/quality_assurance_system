"""
AI 辅助测试模块
- 智能用例生成（根据需求自动生成测试用例）
- BUG 根因分析（比对历史，推荐可能原因）
- 用例推荐（输入修改的代码文件，推荐需要回归的用例）
- 新需求影响分析（RAG 检索 + LLM 分析）
"""
from data.file_provider import get_data_provider
from modules.rag_retriever import get_retriever
from config.llm_config import get_llm
from modules.models import (
    AIAssistedTestResult, GeneratedTestCase, BugRootCauseAnalysis,
    TestCaseRecommendation, Priority, TestCase, Bug
)
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
import os
import json


_data_provider = get_data_provider()


def analyze_bug_root_cause(bug_id: str) -> Optional[BugRootCauseAnalysis]:
    """
    分析 BUG 根因
    通过比对历史 BUG，推荐可能的根因和修复方案
    """
    bugs = _data_provider.get_all_bugs()
    target_bug = next((bug for bug in bugs if bug.id == bug_id), None)
    
    if not target_bug:
        return None
    
    # 获取同模块的历史 BUG
    historical_bugs = [
        bug for bug in bugs 
        if bug.module == target_bug.module and bug.id != bug_id
    ]
    
    # 统计根因分布
    root_cause_stats = defaultdict(int)
    root_cause_solutions = defaultdict(list)
    
    for bug in historical_bugs:
        if bug.root_cause:
            root_cause_stats[bug.root_cause] += 1
            if bug.fix_solution:
                root_cause_solutions[bug.root_cause].append(bug.fix_solution)
    
    # 推荐根因（按频率排序）
    recommended_causes = []
    for cause, count in sorted(root_cause_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        solutions = root_cause_solutions.get(cause, [])
        recommended_causes.append({
            "root_cause": cause,
            "occurrence_count": count,
            "confidence": round(count / len(historical_bugs), 2) if historical_bugs else 0,
            "typical_solutions": solutions[:2]
        })
    
    # 查找相似 BUG（标题或描述相似度）
    similar_bugs = []
    target_words = set(target_bug.title.lower().split())
    
    for bug in historical_bugs[:20]:  # 只检查前20个提高性能
        bug_words = set(bug.title.lower().split())
        similarity = len(target_words & bug_words) / len(target_words | bug_words) if (target_words | bug_words) else 0
        
        if similarity > 0.3:  # 相似度阈值
            similar_bugs.append({
                "id": bug.id,
                "title": bug.title,
                "root_cause": bug.root_cause,
                "fix_solution": bug.fix_solution,
                "similarity": round(similarity, 2)
            })
    
    similar_bugs.sort(key=lambda x: x["similarity"], reverse=True)
    
    # 生成修复建议
    if target_bug.fix_solution:
        suggested_fix = target_bug.fix_solution
    elif root_cause_solutions:
        # 使用最常见的修复方案
        most_common_cause = max(root_cause_stats.items(), key=lambda x: x[1])
        solutions = root_cause_solutions.get(most_common_cause[0], [])
        suggested_fix = solutions[0] if solutions else "建议参考历史相似BUG的修复方案"
    else:
        suggested_fix = "建议先进行代码审查，定位问题后再修复"
    
    # 计算置信度
    confidence = min(1.0, len(historical_bugs) / 10) if historical_bugs else 0.3
    
    return BugRootCauseAnalysis(
        bug_id=bug_id,
        bug_info={
            "id": target_bug.id,
            "title": target_bug.title,
            "module": target_bug.module,
            "severity": target_bug.severity.value,
            "status": target_bug.status.value,
            "description": target_bug.description
        },
        recommended_root_causes=recommended_causes,
        similar_bugs=similar_bugs[:3],
        suggested_fix=suggested_fix,
        confidence=round(confidence, 2)
    )


def recommend_test_cases_for_code_change(
    code_files: List[str],
    module: Optional[str] = None
) -> List[TestCaseRecommendation]:
    """
    根据代码文件修改推荐需要回归测试的用例
    
    Args:
        code_files: 修改的代码文件路径列表
        module: 模块名称（可选，如果提供会更准确）
    """
    # 代码文件到模块的映射
    file_to_module_mapping = {
        "user": "用户管理",
        "order": "订单管理",
        "product": "商品管理",
        "statistics": "数据统计",
        "settings": "系统设置",
        "auth": "用户管理",
        "payment": "订单管理",
        "inventory": "商品管理"
    }
    
    # 确定影响的模块
    affected_modules = set()
    if module:
        affected_modules.add(module)
    
    for file_path in code_files:
        file_lower = file_path.lower()
        for key, mod in file_to_module_mapping.items():
            if key in file_lower:
                affected_modules.add(mod)
    
    # 如果没有映射到模块，使用默认
    if not affected_modules:
        affected_modules = set(_data_provider.get_modules()[:1])
    
    # 获取相关测试用例
    all_test_cases = _data_provider.get_all_test_cases()
    all_bugs = _data_provider.get_all_bugs()
    
    # 统计每个测试用例的历史 BUG 数
    tc_bug_count = defaultdict(int)
    for bug in all_bugs:
        if bug.test_case_id:
            tc_bug_count[bug.test_case_id] += 1
    
    # 筛选受影响模块的测试用例
    affected_tcs = [tc for tc in all_test_cases if tc.module in affected_modules]
    
    # 计算推荐分数
    recommendations = []
    for tc in affected_tcs:
        # 分数计算逻辑：
        # 1. 历史发现 BUG 数 * 3（权重最高）
        # 2. 优先级权重
        # 3. 执行状态（未执行的优先）
        # 4. 最后执行时间（久未执行的优先）
        
        bug_count = tc_bug_count.get(tc.id, 0)
        priority_weight = {"高": 5, "中": 3, "低": 1}.get(tc.priority.value, 1)
        
        status_weight = 0
        if tc.status.value == "未执行":
            status_weight = 4
        elif tc.status.value == "执行中":
            status_weight = 2
        else:
            status_weight = 1
        
        # 执行时间衰减
        time_weight = 1
        if tc.last_executed_at:
            days_since_execution = (datetime.now() - tc.last_executed_at).days
            time_weight = min(3, 1 + days_since_execution / 10)
        
        score = bug_count * 3 + priority_weight + status_weight + time_weight
        
        # 生成推荐理由
        reasons = []
        if bug_count > 0:
            reasons.append(f"历史发现 {bug_count} 个BUG")
        if tc.priority.value == "高":
            reasons.append("高优先级用例")
        if tc.status.value == "未执行":
            reasons.append("尚未执行")
        elif tc.last_executed_at and (datetime.now() - tc.last_executed_at).days > 7:
            reasons.append("超过7天未执行")
        
        recommendations.append(
            TestCaseRecommendation(
                test_case_id=tc.id,
                test_case_title=tc.title,
                module=tc.module,
                relevance_score=round(score, 2),
                recommendation_reason="; ".join(reasons) if reasons else "受影响的测试用例",
                historical_bugs_found=bug_count
            )
        )
    
    # 按分数排序，返回前10个
    recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
    return recommendations[:10]


def ai_assisted_test(
    requirement_id: Optional[str] = None,
    bug_id: Optional[str] = None,
    code_files: Optional[List[str]] = None,
    module: Optional[str] = None
) -> AIAssistedTestResult:
    """
    AI 辅助测试统一接口
    
    Args:
        requirement_id: 需求ID，用于生成测试用例
        bug_id: BUG ID，用于根因分析
        code_files: 代码文件列表，用于推荐测试用例
        module: 模块名称
    """
    generated_cases = []
    bug_analysis = None
    recommended_cases = []
    
    # 生成测试用例
    if requirement_id:
        generated_cases = generate_test_cases_from_requirement(requirement_id)
    
    # BUG 根因分析
    if bug_id:
        bug_analysis = analyze_bug_root_cause(bug_id)
    
    # 推荐测试用例
    if code_files:
        recommended_cases = recommend_test_cases_for_code_change(code_files, module)
    
    return AIAssistedTestResult(
        generated_test_cases=generated_cases,
        bug_analysis=bug_analysis,
        recommended_test_cases=recommended_cases
    )


# ============== 新需求影响分析 ==============

class ImpactAnalysisResult:
    """新需求影响分析结果"""
    def __init__(self):
        self.affected_requirements: List[Dict] = []  # 受影响的历史需求
        regressed_test_cases: List[Dict] = []  # 推荐回归的测试用例
        impact_summary: str = ""  # 影响分析总结
        suggestions: List[str] = []  # 建议


def analyze_new_requirement_impact(
    new_requirement_content: str,
    module: Optional[str] = None
) -> Dict:
    """
    分析新需求的影响并生成测试建议
    
    Args:
        new_requirement_content: 新需求的完整内容（Markdown 格式）
        module: 模块名称（可选，用于过滤检索范围）
        
    Returns:
        影响分析结果字典
    """
    # 1. 使用 RAG 检索相关的历史数据
    retriever = get_retriever()
    context = retriever.get_context_for_llm(
        query=new_requirement_content,
        top_k=8
    )
    
    # 2. 构建 Prompt
    prompt = f"""你是一个高级测试架构师。请分析以下新需求的影响，并给出建议。

【新需求文档】
{new_requirement_content}

【相关的历史数据和用例】
{context}

请以 JSON 格式输出分析结果，包含以下字段：
1. affected_requirements: 受影响的历史需求列表，每项包含 {{id, title, module, impact_reason}}
2. regression_test_cases: 需要回归测试的历史用例列表，每项包含 {{id, title, module, reason}}
3. impact_summary: 影响分析总结（2-3句话）
4. suggestions: 测试建议列表（3-5条）
5. risk_level: 风险等级（低/中/高）

注意：
- 只输出 JSON，不要输出其他文字
- 如果没有受影响的需求或用例，返回空列表
- 确保影响原因是具体的，不要泛泛而谈
"""

    # 3. 调用 LLM
    try:
        llm = get_llm()
        
        # 使用 LangChain 调用
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="你是一个专业的测试分析专家，擅长需求影响分析和测试用例设计。"),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # 尝试解析 JSON
        try:
            # 清理可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
            return result
        except json.JSONDecodeError:
            return {
                "affected_requirements": [],
                "regression_test_cases": [],
                "impact_summary": "LLM 返回格式解析失败",
                "suggestions": ["请检查 LLM 返回格式"],
                "risk_level": "中"
            }
    except Exception as e:
        return {
            "affected_requirements": [],
            "regression_test_cases": [],
            "impact_summary": f"LLM 调用失败: {str(e)}",
            "suggestions": ["检查 LLM 配置"],
            "risk_level": "中"
        }


def _simulate_impact_analysis(
    content: str,
    retriever,
    module: Optional[str] = None
) -> Dict:
    """
    模拟影响分析（用于没有 LLM API Key 时的演示）
    """
    # 使用 RAG 检索结果生成模拟分析
    results = retriever.search(content, top_k=5, filter_module=module)
    
    affected_reqs = []
    regression_tcs = []
    
    for r in results:
        meta = r["metadata"]
        if meta.get("type") == "requirement":
            affected_reqs.append({
                "id": meta["id"],
                "title": meta["title"],
                "module": meta["module"],
                "impact_reason": f"与新需求在'{meta['title']}'方面存在语义重叠"
            })
        elif meta.get("type") == "test_case":
            regression_tcs.append({
                "id": meta["id"],
                "title": meta["title"],
                "module": meta["module"],
                "reason": f"关联需求 {meta.get('requirement_id', '未知')} 可能受影响"
            })
    
    return {
        "affected_requirements": affected_reqs[:3],
        "regression_test_cases": regression_tcs[:5],
        "impact_summary": f"通过 RAG 检索发现 {len(affected_reqs)} 个相关需求，{len(regression_tcs)} 个相关测试用例。建议进行回归测试。",
        "suggestions": [
            "建议对受影响的测试用例进行回归测试",
            "建议补充边界条件测试用例",
            "建议在测试环境中验证端到端流程",
            "建议关注历史 BUG 中相似的问题"
        ],
        "risk_level": "中" if len(affected_reqs) > 0 else "低"
    }

