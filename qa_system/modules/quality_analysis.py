"""
质量分析与预测模块
- 缺陷密度分析
- 需求覆盖率分析
- 高风险模块识别
- BUG趋势预测
"""
from data.file_provider import get_data_provider
from modules.models import (
    QualityAnalysisResult, ModuleQualityMetrics,
    BugTrendPrediction, ModuleBugPrediction
)
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression


_data_provider = get_data_provider()


def calculate_defect_density_by_module() -> Dict[str, float]:
    """
    计算各模块的缺陷密度
    缺陷密度 = BUG数量 / 测试用例数量
    """
    test_cases = _data_provider.get_all_test_cases()
    bugs = _data_provider.get_all_bugs()
    
    # 按模块统计
    module_tc_count = defaultdict(int)
    module_bug_count = defaultdict(int)
    
    for tc in test_cases:
        module_tc_count[tc.module] += 1
    
    for bug in bugs:
        module_bug_count[bug.module] += 1
    
    # 计算缺陷密度
    defect_density = {}
    for module in module_tc_count:
        tc_count = module_tc_count[module]
        bug_count = module_bug_count.get(module, 0)
        defect_density[module] = round(bug_count / tc_count, 3) if tc_count > 0 else 0
    
    return defect_density


def calculate_requirement_coverage() -> Dict[str, float]:
    """
    计算各模块的需求覆盖率
    需求覆盖率 = 有测试用例的需求数 / 总需求数
    """
    requirements = _data_provider.get_all_requirements()
    test_cases = _data_provider.get_all_test_cases()
    
    # 按模块统计
    module_reqs = defaultdict(set)
    module_covered_reqs = defaultdict(set)
    
    for req in requirements:
        module_reqs[req.module].add(req.id)
    
    for tc in test_cases:
        module_covered_reqs[tc.module].add(tc.requirement_id)
    
    # 计算覆盖率
    coverage = {}
    for module in module_reqs:
        total = len(module_reqs[module])
        covered = len(module_covered_reqs.get(module, set()))
        coverage[module] = round(covered / total, 3) if total > 0 else 0
    
    return coverage


def identify_high_risk_modules(
    defect_density: Dict[str, float],
    requirement_coverage: Dict[str, float]
) -> List[str]:
    """
    识别高风险模块
    高风险特征：
    - 缺陷密度高 (>0.5)
    - 需求覆盖率低但BUG多
    - 缺陷密度高于平均值
    """
    if not defect_density:
        return []
    
    avg_density = np.mean(list(defect_density.values()))
    
    high_risk = []
    for module, density in defect_density.items():
        coverage = requirement_coverage.get(module, 0)
        
        # 风险评分逻辑
        is_high_risk = (
            density > 0.5 or  # 缺陷密度高
            (density > avg_density and coverage > 0.8) or  # 密度高于平均且覆盖率高
            density > avg_density * 1.5  # 密度远高于平均
        )
        
        if is_high_risk:
            high_risk.append(module)
    
    return high_risk


def find_uncovered_requirements() -> List[str]:
    """找出未被测试用例覆盖的需求ID"""
    requirements = _data_provider.get_all_requirements()
    test_cases = _data_provider.get_all_test_cases()
    
    covered_req_ids = set(tc.requirement_id for tc in test_cases)
    uncovered = [req.id for req in requirements if req.id not in covered_req_ids]
    
    return uncovered


def analyze_quality() -> QualityAnalysisResult:
    """
    综合分析质量
    返回完整的质量分析结果
    """
    requirements = _data_provider.get_all_requirements()
    test_cases = _data_provider.get_all_test_cases()
    bugs = _data_provider.get_all_bugs()
    
    # 计算基础指标
    defect_density = calculate_defect_density_by_module()
    requirement_coverage = calculate_requirement_coverage()
    high_risk_modules = identify_high_risk_modules(defect_density, requirement_coverage)
    uncovered_reqs = find_uncovered_requirements()
    
    # 按模块计算详细指标
    modules = _data_provider.get_modules()
    module_metrics = []
    
    for module in modules:
        module_reqs = _data_provider.get_requirements_by_module(module)
        module_tcs = _data_provider.get_test_cases_by_module(module)
        module_bugs = _data_provider.get_bugs_by_module(module)
        
        covered_reqs = len(set(tc.requirement_id for tc in module_tcs))
        executed_tcs = len([tc for tc in module_tcs if tc.status.value in ["已执行", "执行中"]])
        fixed_bugs = len([bug for bug in module_bugs if bug.status.value == "已修复"])
        
        total_tcs = len(module_tcs)
        total_bugs = len(module_bugs)
        
        module_metrics.append(
            ModuleQualityMetrics(
                module=module,
                total_requirements=len(module_reqs),
                covered_requirements=covered_reqs,
                requirement_coverage_rate=requirement_coverage.get(module, 0),
                total_test_cases=total_tcs,
                executed_test_cases=executed_tcs,
                execution_rate=round(executed_tcs / total_tcs, 3) if total_tcs > 0 else 0,
                total_bugs=total_bugs,
                fixed_bugs=fixed_bugs,
                bug_fix_rate=round(fixed_bugs / total_bugs, 3) if total_bugs > 0 else 0,
                defect_density=defect_density.get(module, 0),
                risk_level="高" if module in high_risk_modules else "中" if defect_density.get(module, 0) > 0.3 else "低"
            )
        )
    
    # 生成建议
    recommendations = []
    if high_risk_modules:
        recommendations.append(f"重点关注高风险模块: {', '.join(high_risk_modules)}")
    
    avg_coverage = np.mean(list(requirement_coverage.values()))
    if avg_coverage < 0.8:
        recommendations.append("整体需求覆盖率偏低，建议增加测试用例覆盖")
    
    avg_density = np.mean(list(defect_density.values()))
    if avg_density > 0.5:
        recommendations.append("缺陷密度偏高，建议进行代码质量审查")
    
    if uncovered_reqs:
        recommendations.append(f"发现 {len(uncovered_reqs)} 个未被测试的需求，建议补充测试用例")
    
    # 整体统计
    total_tcs = len(test_cases)
    total_bugs = len(bugs)
    overall_density = total_bugs / total_tcs if total_tcs > 0 else 0
    
    covered_reqs = len(set(tc.requirement_id for tc in test_cases))
    overall_coverage = covered_reqs / len(requirements) if requirements else 0
    
    return QualityAnalysisResult(
        analysis_time=datetime.now(),
        module_metrics=module_metrics,
        overall_defect_density=round(overall_density, 3),
        overall_requirement_coverage=round(overall_coverage, 3),
        high_risk_modules=high_risk_modules,
        uncovered_requirements=uncovered_reqs,
        recommendations=recommendations
    )


def predict_bug_trend(days: int = 7) -> List[BugTrendPrediction]:
    """
    预测未来N天的BUG趋势
    使用线性回归模型基于历史数据预测
    """
    bugs = _data_provider.get_all_bugs()
    
    if len(bugs) < 3:
        return []
    
    # 按日期统计BUG数量
    bug_by_date = defaultdict(int)
    for bug in bugs:
        date_str = bug.created_at.strftime('%Y-%m-%d')
        bug_by_date[date_str] += 1
    
    # 准备训练数据
    dates = sorted(bug_by_date.keys())
    base_date = datetime.strptime(dates[0], '%Y-%m-%d')
    
    X = np.array([[(datetime.strptime(d, '%Y-%m-%d') - base_date).days for d in dates]]).T
    y = np.array([bug_by_date[d] for d in dates])
    
    # 训练模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 预测未来
    predictions = []
    last_date = datetime.strptime(dates[-1], '%Y-%m-%d')
    
    for i in range(1, days + 1):
        future_date = last_date + timedelta(days=i)
        future_day = (future_date - base_date).days
        
        predicted = max(0, int(model.predict([[future_day]])[0]))
        
        # 计算置信区间（简化版）
        std = np.std(y)
        confidence_interval = {
            "lower": max(0, predicted - int(std)),
            "upper": predicted + int(std)
        }
        
        predictions.append(
            BugTrendPrediction(
                date=future_date.strftime('%Y-%m-%d'),
                predicted_bugs=predicted,
                confidence_interval=confidence_interval
            )
        )
    
    return predictions


def predict_bugs_by_module(new_test_cases_per_module: Dict[str, int] = None) -> List[ModuleBugPrediction]:
    """
    按模块预测未来可能出现的BUG数量
    
    Args:
        new_test_cases_per_module: 每个模块新增的测试用例数
    """
    if new_test_cases_per_module is None:
        # 默认假设每个模块新增5个测试用例
        modules = _data_provider.get_modules()
        new_test_cases_per_module = {module: 5 for module in modules}
    
    bugs = _data_provider.get_all_bugs()
    test_cases = _data_provider.get_all_test_cases()
    
    # 统计历史数据
    module_bug_count = defaultdict(int)
    module_tc_count = defaultdict(int)
    
    for bug in bugs:
        module_bug_count[bug.module] += 1
    
    for tc in test_cases:
        module_tc_count[tc.module] += 1
    
    predictions = []
    for module, new_tc_count in new_test_cases_per_module.items():
        historical_bugs = module_bug_count.get(module, 0)
        historical_tcs = module_tc_count.get(module, 1)
        
        # 计算历史BUG率
        bug_rate = historical_bugs / historical_tcs if historical_tcs > 0 else 0
        
        # 预测新BUG数
        predicted_bugs = int(bug_rate * new_tc_count)
        
        # 计算置信度（基于历史数据量）
        confidence = min(1.0, historical_tcs / 20)
        
        # 识别风险因素
        risk_factors = []
        if bug_rate > 0.5:
            risk_factors.append("历史BUG率高")
        if historical_bugs > 10:
            risk_factors.append("历史BUG总数多")
        
        # 检查该模块的严重程度分布
        module_bugs = [b for b in bugs if b.module == module]
        critical_bugs = [b for b in module_bugs if b.severity.value == "严重"]
        if len(critical_bugs) > 2:
            risk_factors.append("存在多个严重BUG")
        
        predictions.append(
            ModuleBugPrediction(
                module=module,
                historical_bug_rate=round(bug_rate, 3),
                predicted_new_bugs=predicted_bugs,
                confidence=round(confidence, 2),
                risk_factors=risk_factors
            )
        )
    
    return predictions
