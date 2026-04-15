"""
功能演示脚本
展示智能质量保证系统的所有核心功能
"""
from data.file_provider import get_data_provider
from modules.quality_analysis import analyze_quality, predict_bug_trend, predict_bugs_by_module
from modules.ai_assisted_testing import generate_test_cases_from_requirement, analyze_bug_root_cause, recommend_test_cases_for_code_change
from modules.knowledge_management import search_knowledge, generate_training_materials, collect_historical_bugs
from modules.smart_report import generate_smart_report, generate_module_report
import json


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data, indent=2):
    """格式化打印 JSON 数据"""
    print(json.dumps(data, indent=indent, ensure_ascii=False, default=str))


def main():
    print("\n" + "🚀" * 30)
    print("  智能质量保证系统 v2.0.0 - 功能演示")
    print("🚀" * 30)
    
    # 0. 数据统计
    print_section("📊 数据统计概览")
    dp = get_data_provider()
    stats = dp.get_statistics()
    print(f"模块列表: {', '.join(stats['modules'])}")
    print(f"需求总数: {stats['total_requirements']}")
    print(f"测试用例总数: {stats['total_test_cases']}")
    print(f"BUG总数: {stats['total_bugs']}")
    
    # 1. 质量分析
    print_section("🔍 1. 质量分析与预测")
    
    print("\n1.1 综合质量分析:")
    quality_result = analyze_quality()
    print(f"  - 整体缺陷密度: {quality_result.overall_defect_density}")
    print(f"  - 整体需求覆盖率: {quality_result.overall_requirement_coverage:.0%}")
    print(f"  - 高风险模块: {', '.join(quality_result.high_risk_modules) if quality_result.high_risk_modules else '无'}")
    print(f"  - 未覆盖需求: {len(quality_result.uncovered_requirements)} 个")
    print(f"  - 建议:")
    for rec in quality_result.recommendations[:3]:
        print(f"    • {rec}")
    
    print("\n1.2 BUG趋势预测（未来7天）:")
    trend = predict_bug_trend(days=7)
    for pred in trend[:3]:
        ci = pred.confidence_interval
        print(f"  - {pred.date}: 预测 {pred.predicted_bugs} 个BUG (置信区间: {ci['lower']}-{ci['upper']})")
    
    print("\n1.3 模块BUG预测:")
    bug_preds = predict_bugs_by_module()
    for pred in bug_preds[:3]:
        print(f"  - {pred.module}: 预测 {pred.predicted_new_bugs} 个新BUG (置信度: {pred.confidence:.0%})")
        if pred.risk_factors:
            print(f"    风险因素: {', '.join(pred.risk_factors)}")
    
    # 2. AI辅助测试
    print_section("🤖 2. AI 辅助测试")
    
    print("\n2.1 智能用例生成（基于需求 REQ-001）:")
    generated_cases = generate_test_cases_from_requirement("REQ-001")
    print(f"  生成 {len(generated_cases)} 个测试用例:")
    for case in generated_cases[:3]:
        print(f"  • {case.title}")
        print(f"    优先级: {case.priority.value}")
        print(f"    生成原因: {case.generation_reason}")
    
    print("\n2.2 BUG根因分析（BUG-001）:")
    bug_analysis = analyze_bug_root_cause("BUG-001")
    if bug_analysis:
        print(f"  BUG信息: {bug_analysis.bug_info['title']}")
        print(f"  推荐根因:")
        for cause in bug_analysis.recommended_root_causes[:2]:
            print(f"    • {cause['root_cause']} (出现{cause['occurrence_count']}次, 置信度{cause['confidence']:.0%})")
        print(f"  建议修复方案: {bug_analysis.suggested_fix}")
        print(f"  分析置信度: {bug_analysis.confidence:.0%}")
    
    print("\n2.3 用例推荐（代码变更）:")
    recommendations = recommend_test_cases_for_code_change(["user.py", "auth.py"])
    print(f"  推荐 {len(recommendations)} 个测试用例:")
    for rec in recommendations[:3]:
        print(f"  • {rec.test_case_title} (分数: {rec.relevance_score})")
        print(f"    理由: {rec.recommendation_reason}")
    
    # 4. 知识管理
    print_section("📚 4. 知识管理")
    
    print("\n4.1 智能搜索（关键词: '用户'）:")
    search_results = search_knowledge("用户")
    print(f"  找到 {len(search_results)} 个结果:")
    for result in search_results[:3]:
        print(f"  • [{result.result_type}] {result.title}")
        print(f"    模块: {result.module}, 相关性: {result.relevance_score:.0%}")
    
    print("\n4.2 培训材料生成:")
    materials = generate_training_materials()
    print(f"  生成 {len(materials)} 个模块的培训材料")
    if materials:
        first = materials[0]
        print(f"\n  示例 - {first.module}模块:")
        print(f"  {first.overview}")
        if first.best_practices:
            print(f"  最佳实践:")
            for practice in first.best_practices[:2]:
                print(f"    • {practice}")
    
    print("\n4.3 历史BUG案例:")
    historical_bugs = collect_historical_bugs(limit=3)
    print(f"  收集 {len(historical_bugs)} 个历史BUG案例")
    for bug in historical_bugs[:2]:
        print(f"  • {bug.title}")
        print(f"    根因: {bug.root_cause}")
        print(f"    经验教训:")
        for lesson in bug.lessons_learned[:2]:
            print(f"      - {lesson}")
    
    # 5. 智能报告
    print_section("📈 5. 智能报告")
    
    print("\n5.1 项目质量报告:")
    report = generate_smart_report()
    print(f"  项目质量得分: {report.project_quality_score:.1f}/100")
    print(f"  整体缺陷密度: {report.overall_defect_density}")
    print(f"  整体需求覆盖率: {report.overall_requirement_coverage:.0%}")
    print(f"\n  执行摘要:")
    print(f"  {report.executive_summary[:150]}...")
    print(f"\n  建议:")
    for rec in report.recommendations[:3]:
        print(f"    • {rec}")
    
    print("\n5.2 模块质量报告（用户管理）:")
    module_report = generate_module_report("用户管理")
    if module_report:
        print(f"  模块: {module_report.module}")
        print(f"  质量得分: {module_report.quality_score:.1f}/100")
        print(f"  需求覆盖率: {module_report.requirement_coverage:.0%}")
        print(f"  缺陷密度: {module_report.defect_density}")
        print(f"  BUG修复率: {module_report.bug_fix_rate:.0%}")
        print(f"  风险评估: {module_report.risk_assessment}")
    
    # 总结
    print_section("✨ 总结")
    print("✅ 所有核心功能演示完成!")
    print("\n系统特性:")
    print("  • 模块化架构，易于扩展和维护")
    print("  • 基于数据驱动的质量分析")
    print("  • AI辅助测试，提升测试效率")
    print("  • 智能知识管理，沉淀团队经验")
    print("  • 自动化报告，减少人工工作量")
    print("\n访问 http://localhost:8000/docs 查看完整 API 文档")
    print()


if __name__ == "__main__":
    main()
