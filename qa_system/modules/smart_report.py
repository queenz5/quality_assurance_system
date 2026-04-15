"""
智能报告模块
- 项目质量报告（自动生成）
- 模块报告
"""
from data.file_provider import get_data_provider
from modules.models import (
    ProjectQualityReport, ModuleReport, BugTrendPrediction
)
from modules.quality_analysis import (
    analyze_quality, predict_bug_trend, calculate_defect_density_by_module,
    calculate_requirement_coverage, identify_high_risk_modules
)
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np


_data_provider = get_data_provider()


def generate_module_report(module: str) -> Optional[ModuleReport]:
    """
    生成模块质量报告
    
    Args:
        module: 模块名称
    """
    modules = _data_provider.get_modules()
    if module not in modules:
        return None
    
    module_reqs = _data_provider.get_requirements_by_module(module)
    module_tcs = _data_provider.get_test_cases_by_module(module)
    module_bugs = _data_provider.get_bugs_by_module(module)
    
    # 计算模块质量指标
    total_tcs = len(module_tcs)
    total_bugs = len(module_bugs)
    
    # 需求覆盖率
    covered_reqs = len(set(tc.requirement_id for tc in module_tcs))
    requirement_coverage = covered_reqs / len(module_reqs) if module_reqs else 0
    
    # 缺陷密度
    defect_density = total_bugs / total_tcs if total_tcs > 0 else 0
    
    # BUG修复率
    fixed_bugs = len([bug for bug in module_bugs if bug.status.value == "已修复"])
    bug_fix_rate = fixed_bugs / total_bugs if total_bugs > 0 else 0
    
    # 计算质量得分 (0-100)
    # 覆盖率得分 (0-30分)
    coverage_score = min(30, requirement_coverage * 30)
    
    # 缺陷密度得分 (0-30分，密度越低分越高)
    density_score = max(0, 30 - defect_density * 20)
    
    # BUG修复率得分 (0-25分)
    fix_rate_score = bug_fix_rate * 25
    
    # 测试执行率得分 (0-15分)
    executed_tcs = len([tc for tc in module_tcs if tc.status.value in ["已执行", "执行中"]])
    execution_rate = executed_tcs / total_tcs if total_tcs > 0 else 0
    execution_score = execution_rate * 15
    
    quality_score = round(coverage_score + density_score + fix_rate_score + execution_score, 2)
    
    # 风险评估
    if quality_score >= 80:
        risk_assessment = "低风险 - 模块质量优秀"
    elif quality_score >= 60:
        risk_assessment = "中低风险 - 模块质量良好"
    elif quality_score >= 40:
        risk_assessment = "中风险 - 模块质量一般，需关注改进"
    else:
        risk_assessment = "高风险 - 模块质量较差，需重点关注"
    
    # 生成建议
    recommendations = []
    
    if requirement_coverage < 0.8:
        recommendations.append(f"需求覆盖率较低({requirement_coverage:.0%})，建议增加测试用例")
    
    if defect_density > 0.5:
        recommendations.append(f"缺陷密度较高({defect_density:.2f})，建议进行代码质量审查")
    
    if bug_fix_rate < 0.7 and total_bugs > 0:
        recommendations.append(f"BUG修复率较低({bug_fix_rate:.0%})，建议加快修复进度")
    
    if execution_rate < 0.7:
        recommendations.append(f"测试执行率较低({execution_rate:.0%})，建议加快测试进度")
    
    # 检查严重BUG
    critical_bugs = [b for b in module_bugs if b.severity.value == "严重" and b.status.value != "已修复"]
    if critical_bugs:
        recommendations.append(f"存在 {len(critical_bugs)} 个未修复的严重BUG，需优先处理")
    
    return ModuleReport(
        module=module,
        quality_score=quality_score,
        requirement_coverage=round(requirement_coverage, 3),
        defect_density=round(defect_density, 3),
        bug_fix_rate=round(bug_fix_rate, 3),
        total_requirements=len(module_reqs),
        total_test_cases=total_tcs,
        total_bugs=total_bugs,
        fixed_bugs=fixed_bugs,
        risk_assessment=risk_assessment,
        recommendations=recommendations
    )


def generate_all_module_reports() -> List[ModuleReport]:
    """生成所有模块的报告"""
    modules = _data_provider.get_modules()
    reports = []
    
    for module in modules:
        report = generate_module_report(module)
        if report:
            reports.append(report)
    
    # 按质量得分排序
    reports.sort(key=lambda r: r.quality_score)
    
    return reports


def generate_smart_report() -> ProjectQualityReport:
    """
    生成项目质量报告
    整合各模块数据，生成综合质量报告
    """
    # 获取基础数据
    requirements = _data_provider.get_all_requirements()
    test_cases = _data_provider.get_all_test_cases()
    bugs = _data_provider.get_all_bugs()
    
    # 质量分析
    quality_analysis_result = analyze_quality()
    
    # BUG趋势预测
    bug_trend = predict_bug_trend(days=7)
    
    # 模块报告
    module_reports = generate_all_module_reports()
    
    # 高风险模块报告
    high_risk_modules = [
        report for report in module_reports 
        if report.module in quality_analysis_result.high_risk_modules
    ]
    
    # BUG统计
    total_bugs = len(bugs)
    fixed_bugs = len([b for b in bugs if b.status.value == "已修复"])
    open_bugs = len([b for b in bugs if b.status.value in ["未修复", "修复中"]])
    
    severity_dist = {
        "严重": len([b for b in bugs if b.severity.value == "严重"]),
        "一般": len([b for b in bugs if b.severity.value == "一般"]),
        "轻微": len([b for b in bugs if b.severity.value == "轻微"])
    }
    
    status_dist = {
        "已修复": fixed_bugs,
        "修复中": len([b for b in bugs if b.status.value == "修复中"]),
        "未修复": len([b for b in bugs if b.status.value == "未修复"]),
        "其他": len([b for b in bugs if b.status.value not in ["已修复", "修复中", "未修复"]])
    }
    
    bug_statistics = {
        "total_bugs": total_bugs,
        "fixed_bugs": fixed_bugs,
        "open_bugs": open_bugs,
        "fix_rate": round(fixed_bugs / total_bugs, 3) if total_bugs > 0 else 0,
        "severity_distribution": severity_dist,
        "status_distribution": status_dist
    }
    
    # 测试执行摘要
    total_tcs = len(test_cases)
    executed_tcs = len([tc for tc in test_cases if tc.status.value == "已执行"])
    not_executed_tcs = len([tc for tc in test_cases if tc.status.value == "未执行"])
    
    test_execution_summary = {
        "total_test_cases": total_tcs,
        "executed": executed_tcs,
        "not_executed": not_executed_tcs,
        "execution_rate": round(executed_tcs / total_tcs, 3) if total_tcs > 0 else 0,
        "total_bugs_found": total_bugs,
        "bug_discovery_rate": round(total_bugs / total_tcs, 3) if total_tcs > 0 else 0
    }
    
    # 计算项目质量得分
    # 基于多个维度综合评分
    overall_coverage = quality_analysis_result.overall_requirement_coverage
    overall_density = quality_analysis_result.overall_defect_density
    
    # 覆盖率得分 (0-25分)
    coverage_score = min(25, overall_coverage * 25)
    
    # 缺陷密度得分 (0-25分)
    density_score = max(0, 25 - overall_density * 15)
    
    # 高风险模块扣分 (0-20分)
    risk_score = max(0, 20 - len(quality_analysis_result.high_risk_modules) * 5)
    
    # BUG修复率得分 (0-15分)
    fix_rate = bug_statistics["fix_rate"]
    fix_score = fix_rate * 15
    
    # 测试执行率得分 (0-15分)
    execution_rate = test_execution_summary["execution_rate"]
    execution_score = execution_rate * 15
    
    project_quality_score = round(
        coverage_score + density_score + risk_score + fix_score + execution_score,
        2
    )
    
    # 生成建议
    recommendations = []
    
    if quality_analysis_result.high_risk_modules:
        recommendations.append(
            f"重点关注高风险模块: {', '.join(quality_analysis_result.high_risk_modules)}"
        )
    
    if overall_coverage < 0.8:
        recommendations.append(
            f"整体需求覆盖率为 {overall_coverage:.0%}，建议提升至80%以上"
        )
    
    if overall_density > 0.5:
        recommendations.append(
            f"整体缺陷密度为 {overall_density:.2f}，建议进行代码质量改进"
        )
    
    if fix_rate < 0.8:
        recommendations.append(
            f"BUG修复率为 {fix_rate:.0%}，建议加快修复进度"
        )
    
    if execution_rate < 0.8:
        recommendations.append(
            f"测试执行率为 {execution_rate:.0%}，建议加快测试执行进度"
        )
    
    if quality_analysis_result.uncovered_requirements:
        recommendations.append(
            f"有 {len(quality_analysis_result.uncovered_requirements)} 个需求未被测试覆盖"
        )
    
    # 生成执行摘要
    executive_summary = (
        f"项目质量评估报告 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        f"项目整体质量得分为 {project_quality_score:.1f}/100 分。"
        f"需求覆盖率为 {overall_coverage:.0%}，"
        f"缺陷密度为 {overall_density:.2f}，"
        f"BUG修复率为 {fix_rate:.0%}。\n\n"
    )
    
    if project_quality_score >= 80:
        executive_summary += "项目质量状况良好，建议继续保持当前的质量管理实践。"
    elif project_quality_score >= 60:
        executive_summary += "项目质量状况一般，存在部分需要改进的方面，建议重点关注高风险模块。"
    elif project_quality_score >= 40:
        executive_summary += "项目质量状况需要关注，建议增加测试投入，加快BUG修复进度。"
    else:
        executive_summary += "项目质量状况较差，需要立即采取措施改进质量。"
    
    if quality_analysis_result.high_risk_modules:
        executive_summary += (
            f"\n\n需要重点关注的风险模块: {', '.join(quality_analysis_result.high_risk_modules)}"
        )
    
    return ProjectQualityReport(
        report_time=datetime.now(),
        project_quality_score=project_quality_score,
        overall_defect_density=round(overall_density, 3),
        overall_requirement_coverage=round(overall_coverage, 3),
        bug_statistics=bug_statistics,
        high_risk_modules=high_risk_modules,
        bug_trend=bug_trend,
        test_execution_summary=test_execution_summary,
        recommendations=recommendations,
        executive_summary=executive_summary
    )
