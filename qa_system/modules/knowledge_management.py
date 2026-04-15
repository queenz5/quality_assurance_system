"""
知识管理模块
- 新人培训（整合文档，AI问答）
- 经验沉淀（历史BUG + 修复方案）
- 智能搜索（自然语言搜索，返回全链路信息）
"""
from data.file_provider import get_data_provider
from modules.models import (
    KnowledgeManagementResult, TrainingMaterial,
    HistoricalBugCase, KnowledgeSearchResult, BugSeverity
)
from typing import List, Dict, Optional
from collections import defaultdict
import re


_data_provider = get_data_provider()


def generate_training_materials() -> List[TrainingMaterial]:
    """
    生成新人培训材料
    按模块组织需求、测试用例、BUG的综合培训材料
    """
    modules = _data_provider.get_modules()
    training_materials = []
    
    for module in modules:
        module_reqs = _data_provider.get_requirements_by_module(module)
        module_tcs = _data_provider.get_test_cases_by_module(module)
        module_bugs = _data_provider.get_bugs_by_module(module)
        
        # 模块概述
        overview = (
            f"{module}模块包含 {len(module_reqs)} 个需求，"
            f"{len(module_tcs)} 个测试用例，"
            f"共发现 {len(module_bugs)} 个BUG。"
        )
        
        # 需求摘要
        req_summary = []
        for req in module_reqs[:5]:  # 最多展示5个
            req_summary.append({
                "id": req.id,
                "title": req.title,
                "priority": req.priority.value,
                "status": req.status.value,
                "tags": req.tags
            })
        
        # 测试用例摘要
        tc_summary = []
        for tc in module_tcs[:5]:
            tc_summary.append({
                "id": tc.id,
                "title": tc.title,
                "priority": tc.priority.value,
                "status": tc.status.value,
                "bugs_found": len(tc.bugs_found)
            })
        
        # 常见BUG
        common_bugs = []
        # 按根因统计
        bug_cause_stats = defaultdict(int)
        for bug in module_bugs:
            if bug.root_cause:
                bug_cause_stats[bug.root_cause] += 1
        
        # 展示最常见的BUG
        sorted_bugs = sorted(module_bugs, key=lambda b: bug_cause_stats.get(b.root_cause or "", 0), reverse=True)
        for bug in sorted_bugs[:5]:
            common_bugs.append({
                "id": bug.id,
                "title": bug.title,
                "severity": bug.severity.value,
                "root_cause": bug.root_cause or "未知",
                "fix_solution": bug.fix_solution or "待补充"
            })
        
        # 最佳实践（基于历史数据生成）
        best_practices = []
        
        if module_bugs:
            # 统计最常见的BUG类型
            top_causes = sorted(bug_cause_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_causes:
                best_practices.append(f"重点关注: {', '.join([cause for cause, _ in top_causes])}")
            
            # 检查是否有严重BUG
            critical_bugs = [b for b in module_bugs if b.severity.value == "严重"]
            if critical_bugs:
                best_practices.append(f"历史出现 {len(critical_bugs)} 个严重BUG，测试时需特别注意")
        
        # 高优先级需求
        high_priority_reqs = [r for r in module_reqs if r.priority.value == "高"]
        if high_priority_reqs:
            best_practices.append(f"模块包含 {len(high_priority_reqs)} 个高优先级需求，需优先保障质量")
        
        # 测试覆盖情况
        if module_tcs:
            executed_rate = len([tc for tc in module_tcs if tc.status.value in ["已执行", "执行中"]]) / len(module_tcs)
            if executed_rate < 0.7:
                best_practices.append(f"测试执行率较低({executed_rate:.0%})，建议加快测试进度")
        
        training_materials.append(
            TrainingMaterial(
                module=module,
                overview=overview,
                requirements_summary=req_summary,
                test_cases_summary=tc_summary,
                common_bugs=common_bugs,
                best_practices=best_practices
            )
        )
    
    return training_materials


def collect_historical_bugs(limit: int = 20) -> List[HistoricalBugCase]:
    """
    收集历史BUG案例，用于经验沉淀
    """
    bugs = _data_provider.get_all_bugs()
    
    # 筛选有修复方案的BUG
    bugs_with_solutions = [bug for bug in bugs if bug.fix_solution]
    
    # 按严重程度和修复方案质量排序
    severity_weight = {"严重": 3, "一般": 2, "轻微": 1}
    bugs_with_solutions.sort(
        key=lambda b: severity_weight.get(b.severity.value, 0),
        reverse=True
    )
    
    # 生成经验教训
    historical_cases = []
    for bug in bugs_with_solutions[:limit]:
        lessons = []
        
        # 根据根因生成教训
        if bug.root_cause:
            if "空指针" in bug.root_cause:
                lessons.append("加强空值检查，增加防御性编程")
            elif "边界" in bug.root_cause:
                lessons.append("重视边界条件测试，增加边界值验证")
            elif "并发" in bug.root_cause or "并发" in bug.root_cause:
                lessons.append("加强并发场景测试，使用并发测试工具")
            elif "性能" in bug.root_cause:
                lessons.append("定期进行性能测试和代码审查")
            else:
                lessons.append(f"注意{bug.root_cause}类问题")
        
        # 根据严重程度补充教训
        if bug.severity.value == "严重":
            lessons.append("严重BUG需在代码审查中重点检查")
        
        # 如果有相似根因的BUG，补充说明
        similar_bugs = [b for b in bugs if b.root_cause == bug.root_cause and b.id != bug.id]
        if len(similar_bugs) > 2:
            lessons.append(f"同类问题已出现 {len(similar_bugs)} 次，建议建立检查清单")
        
        historical_cases.append(
            HistoricalBugCase(
                bug_id=bug.id,
                title=bug.title,
                module=bug.module,
                severity=bug.severity,
                root_cause=bug.root_cause,
                fix_solution=bug.fix_solution,
                lessons_learned=lessons
            )
        )
    
    return historical_cases


def search_knowledge(query: str, limit: int = 10) -> List[KnowledgeSearchResult]:
    """
    智能搜索
    支持自然语言搜索，返回需求、测试用例、BUG的全链路信息
    """
    requirements = _data_provider.get_all_requirements()
    test_cases = _data_provider.get_all_test_cases()
    bugs = _data_provider.get_all_bugs()
    
    # 分词（简单实现，可按空格和常见分隔符分割）
    keywords = re.split(r'[\s,，、]+', query.lower())
    keywords = [kw for kw in keywords if kw]  # 过滤空字符串
    
    if not keywords:
        return []
    
    search_results = []
    
    # 搜索需求
    for req in requirements:
        req_text = f"{req.id} {req.title} {req.description} {' '.join(req.tags)}".lower()
        
        # 计算匹配分数
        match_count = sum(1 for kw in keywords if kw in req_text)
        if match_count > 0:
            score = match_count / len(keywords)
            
            search_results.append(
                KnowledgeSearchResult(
                    result_type="requirement",
                    id=req.id,
                    title=req.title,
                    description=req.description,
                    module=req.module,
                    relevance_score=round(score, 2),
                    full_data=req.model_dump(mode='json')
                )
            )
    
    # 搜索测试用例
    for tc in test_cases:
        tc_text = f"{tc.id} {tc.title} {tc.description}".lower()
        
        match_count = sum(1 for kw in keywords if kw in tc_text)
        if match_count > 0:
            score = match_count / len(keywords)
            
            search_results.append(
                KnowledgeSearchResult(
                    result_type="test_case",
                    id=tc.id,
                    title=tc.title,
                    description=tc.description,
                    module=tc.module,
                    relevance_score=round(score, 2),
                    full_data=tc.model_dump(mode='json')
                )
            )
    
    # 搜索BUG
    for bug in bugs:
        bug_text = f"{bug.id} {bug.title} {bug.description} {bug.root_cause or ''} {bug.fix_solution or ''}".lower()
        
        match_count = sum(1 for kw in keywords if kw in bug_text)
        if match_count > 0:
            score = match_count / len(keywords)
            
            search_results.append(
                KnowledgeSearchResult(
                    result_type="bug",
                    id=bug.id,
                    title=bug.title,
                    description=bug.description,
                    module=bug.module,
                    relevance_score=round(score, 2),
                    full_data=bug.model_dump(mode='json')
                )
            )
    
    # 按相关性分数排序
    search_results.sort(key=lambda r: r.relevance_score, reverse=True)
    
    return search_results[:limit]


def generate_qa_pairs() -> List[Dict[str, str]]:
    """
    生成常见问答对，用于新人培训和AI问答
    """
    qa_pairs = []
    
    # 基于模块统计生成问答
    modules = _data_provider.get_modules()
    stats = _data_provider.get_statistics()
    
    qa_pairs.append({
        "question": "系统包含哪些模块？",
        "answer": f"系统包含以下模块: {', '.join(modules)}"
    })
    
    qa_pairs.append({
        "question": "系统有多少需求、测试用例和BUG？",
        "answer": f"系统共有 {stats['total_requirements']} 个需求，{stats['total_test_cases']} 个测试用例，{stats['total_bugs']} 个BUG"
    })
    
    # 按模块生成问答
    for module in modules[:3]:  # 只取前3个模块
        module_bugs = _data_provider.get_bugs_by_module(module)
        module_tcs = _data_provider.get_test_cases_by_module(module)
        
        qa_pairs.append({
            "question": f"{module}模块的质量如何？",
            "answer": (
                f"{module}模块共有 {len(module_tcs)} 个测试用例，"
                f"发现 {len(module_bugs)} 个BUG。"
                f"BUG修复率为 {len([b for b in module_bugs if b.status.value == '已修复']) / len(module_bugs) * 100:.0f}%"
                if module_bugs else f"{module}模块暂无BUG记录"
            )
        })
    
    # 常见BUG根因问答
    all_bugs = _data_provider.get_all_bugs()
    root_cause_stats = defaultdict(int)
    for bug in all_bugs:
        if bug.root_cause:
            root_cause_stats[bug.root_cause] += 1
    
    top_causes = sorted(root_cause_stats.items(), key=lambda x: x[1], reverse=True)[:3]
    if top_causes:
        cause_text = ", ".join([f"{cause}({count}次)" for cause, count in top_causes])
        qa_pairs.append({
            "question": "系统中最常见的BUG类型是什么？",
            "answer": f"最常见的BUG类型包括: {cause_text}"
        })
    
    return qa_pairs


def manage_knowledge(query: Optional[str] = None) -> KnowledgeManagementResult:
    """
    知识管理统一接口
    
    Args:
        query: 搜索查询（可选）
    """
    # 生成培训材料
    training_materials = generate_training_materials()
    
    # 收集历史BUG案例
    historical_bugs = collect_historical_bugs(limit=15)
    
    # 搜索结果（如果提供了查询）
    search_results = []
    if query:
        search_results = search_knowledge(query)
    
    # 生成问答对
    qa_pairs = generate_qa_pairs()
    
    return KnowledgeManagementResult(
        training_materials=training_materials,
        historical_bugs=historical_bugs,
        search_results=search_results,
        qa_pairs=qa_pairs
    )
