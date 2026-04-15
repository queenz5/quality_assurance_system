"""
质量保证系统 - FastAPI 主入口
提供完整的 REST API 接口
"""
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# 加载环境变量
load_dotenv()

# 导入模块
from modules.requirement_parser import parse_requirement_from_file, parse_requirement_from_text, RequirementParser
from modules.requirement_analyzer import analyze_requirement, RequirementAnalyzer
from modules.requirement_analysis_service import RequirementAnalysisService
from modules.markdown_analysis_service import MarkdownAnalysisService
from modules.test_case_generator import generate_test_cases_from_requirements, TestCaseGenerator
from modules.test_case_generation_service import TestCaseGenerationService
from modules.index_manager import get_index_manager
from modules.quality_analysis import (
    analyze_quality, predict_bug_trend, predict_bugs_by_module
)
from modules.ai_assisted_testing import ai_assisted_test
from modules.knowledge_management import manage_knowledge
from modules.smart_report import generate_smart_report, generate_module_report
from data.file_provider import get_data_provider
from modules.models import RequirementStatus


# 创建 FastAPI 应用
app = FastAPI(
    title="智能质量保证系统",
    description="整合需求、测试用例、BUG的智能质量保证系统，提供质量分析、AI辅助测试、流程优化、知识管理和智能报告等功能",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取数据提供者
_data_provider = get_data_provider()


# ============== 基础信息接口 ==============

@app.get("/")
async def root():
    """根路径，返回系统信息"""
    return {
        "message": "智能质量保证系统 API",
        "version": "2.0.0",
        "features": [
            "质量分析与预测",
            "AI 辅助测试",
            "流程优化",
            "知识管理",
            "智能报告"
        ]
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


# ============== 数据获取接口 ==============

@app.get("/api/data/requirements", summary="获取所有需求")
async def get_all_requirements(module: Optional[str] = Query(None, description="按模块筛选")):
    """获取需求列表，支持按模块筛选"""
    if module:
        data = _data_provider.get_requirements_by_module(module)
    else:
        data = _data_provider.get_all_requirements()
    
    return {"total": len(data), "data": [req.model_dump(mode='json') for req in data]}


@app.get("/api/data/test-cases", summary="获取所有测试用例")
async def get_all_test_cases(
    module: Optional[str] = Query(None, description="按模块筛选"),
    requirement_id: Optional[str] = Query(None, description="按需求ID筛选")
):
    """获取测试用例列表"""
    if module:
        data = _data_provider.get_test_cases_by_module(module)
    elif requirement_id:
        data = _data_provider.get_test_cases_by_requirement(requirement_id)
    else:
        data = _data_provider.get_all_test_cases()
    
    return {"total": len(data), "data": [tc.model_dump(mode='json') for tc in data]}


@app.get("/api/data/bugs", summary="获取所有BUG")
async def get_all_bugs(
    module: Optional[str] = Query(None, description="按模块筛选"),
    status: Optional[str] = Query(None, description="按状态筛选")
):
    """获取BUG列表"""
    data = _data_provider.get_all_bugs()
    
    if module:
        data = [bug for bug in data if bug.module == module]
    
    if status:
        data = [bug for bug in data if bug.status.value == status]
    
    return {"total": len(data), "data": [bug.model_dump(mode='json') for bug in data]}


@app.get("/api/data/modules", summary="获取模块列表")
async def get_modules():
    """获取所有模块列表"""
    return {"modules": _data_provider.get_modules()}


@app.get("/api/data/statistics", summary="获取数据统计信息")
async def get_statistics():
    """获取数据统计摘要"""
    return _data_provider.get_statistics()


# ============== Markdown结构化接口 ==============

@app.post("/api/requirements/analyze-to-markdown", summary="分析需求并输出结构化Markdown")
async def analyze_to_markdown(request: dict):
    """
    分析需求文档，输出带标注的结构化Markdown
    
    请求体示例:
    ```json
    {
      "content": "# 用户需求...",
      "source_name": "用户需求文档"
    }
    ```
    """
    content = request.get("content", "")
    source_name = request.get("source_name", "未知来源")
    
    if not content:
        raise HTTPException(status_code=400, detail="content 不能为空")
    
    try:
        print(f"🔍 开始分析并生成Markdown: {source_name}")
        
        service = MarkdownAnalysisService(data_dir=str(_data_provider.data_dir))
        result = service.analyze_to_markdown(content, source_name)
        
        print(f"✅ Markdown生成成功: {result['draft_id']}")
        
        return {
            "success": True,
            "draft_id": result["draft_id"],
            "markdown": result["markdown"],
            "summary": result["summary"],
            "total_issues": result["total_issues"],
            "critical_issues": result["critical_issues"],
            "major_issues": result["major_issues"],
            "minor_issues": result["minor_issues"],
            "issues": result["issues"]
        }
    except Exception as e:
        import traceback
        error_detail = f"分析失败: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/requirements/draft/{draft_id}/markdown", summary="获取草稿的Markdown内容")
async def get_draft_markdown(draft_id: str):
    """获取草稿的Markdown内容"""
    try:
        service = MarkdownAnalysisService(data_dir=str(_data_provider.data_dir))
        markdown = service.get_draft_markdown(draft_id)
        
        if markdown is None:
            raise HTTPException(status_code=404, detail=f"草稿不存在: {draft_id}")
        
        return {
            "success": True,
            "draft_id": draft_id,
            "markdown": markdown
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@app.put("/api/requirements/draft/{draft_id}/markdown", summary="保存编辑后的Markdown")
async def save_draft_markdown(draft_id: str, request: dict):
    """
    保存编辑后的Markdown草稿
    
    请求体示例:
    ```json
    {
      "markdown": "# 结构化需求..."
    }
    ```
    """
    markdown = request.get("markdown", "")
    
    if not markdown:
        raise HTTPException(status_code=400, detail="markdown 不能为空")
    
    try:
        service = MarkdownAnalysisService(data_dir=str(_data_provider.data_dir))
        success = service.save_draft_markdown(draft_id, markdown)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"草稿不存在: {draft_id}")
        
        return {
            "success": True,
            "message": "草稿保存成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@app.post("/api/requirements/draft/{draft_id}/publish", summary="发布Markdown草稿为正式文档")
async def publish_markdown_draft(draft_id: str, request: dict = None):
    """
    发布Markdown草稿为正式文档
    按标准格式保存: {模块名}/REQ-XXX_标题.md
    """
    try:
        # 读取Markdown文件
        drafts_dir = _data_provider.data_dir / "drafts"
        md_file = drafts_dir / f"{draft_id}.md"

        if not md_file.exists():
            raise HTTPException(status_code=404, detail=f"草稿不存在: {draft_id}")

        markdown_content = md_file.read_text(encoding='utf-8')
        
        # 解析出各个需求
        import re
        requirements = []
        
        # 匹配 # REQ-XXX: 标题
        pattern = r'^#\s+(REQ-\d+):\s+(.+)$'
        matches = list(re.finditer(pattern, markdown_content, re.MULTILINE))
        
        for i, match in enumerate(matches):
            req_id = match.group(1)
            req_title = match.group(2).strip()
            
            # 获取该需求的内容
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_content)
            req_content = markdown_content[start:end].strip()
            
            # 提取模块
            module_match = re.search(r'-\s*\*\*模块\*\*:\s*(.+)', req_content)
            module = module_match.group(1).strip() if module_match else "未分类"
            
            requirements.append({
                "id": req_id,
                "title": req_title,
                "module": module,
                "content": req_content
            })
        
        if not requirements:
            raise HTTPException(status_code=400, detail="未能解析到任何需求")

        # 确定目标目录
        target_dir = None
        if request:
            target_dir = request.get("target_dir")

        if target_dir is None:
            target_dir = _data_provider.data_dir / "requirements"
        else:
            target_dir = Path(target_dir)

        target_dir.mkdir(parents=True, exist_ok=True)

        # 按模块保存每个需求
        saved_files = []
        saved_requirements = []
        for req in requirements:
            # 创建模块目录
            module_dir = target_dir / req["module"]
            module_dir.mkdir(parents=True, exist_ok=True)

            # 清理文件名中的非法字符
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', req["title"])
            file_name = f"{req['id']}_{safe_title}.md"
            file_path = module_dir / file_name

            # 添加发布标记
            content_with_marker = req["content"] + f"\n\n---\n**状态**: 正式文档\n**发布时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            file_path.write_text(content_with_marker, encoding='utf-8')
            saved_files.append(str(file_path))

            # 收集需求信息用于更新索引
            from modules.models import StructuredRequirement, RequirementStatus, Priority
            saved_requirements.append(StructuredRequirement(
                id=req["id"],
                title=req["title"],
                module=req["module"],
                status=RequirementStatus.FORMAL,
                priority=Priority.MEDIUM,
                description=req["content"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ))

            print(f"✅ 保存需求: {file_path}")

        # 更新需求索引
        if saved_requirements:
            from modules.requirement_parser import RequirementParser
            parser = RequirementParser(output_dir=str(target_dir))
            parser._update_requirements_index(saved_requirements)

        # 删除草稿
        meta_file = drafts_dir / f"{draft_id}.json"
        if meta_file.exists():
            meta_file.unlink()

        if md_file.exists():
            md_file.unlink()

        print(f"✅ 草稿已发布: {len(saved_files)} 个需求")

        return {
            "success": True,
            "message": f"草稿已发布为正式文档，共保存 {len(saved_files)} 个需求",
            "saved_files": saved_files
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"发布失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


# ============== 草稿管理接口 ==============

# ============== 正式需求管理接口 ==============

@app.get("/api/requirements/formal", summary="获取正式需求列表")
async def get_formal_requirements(module: Optional[str] = Query(None, description="按模块筛选")):
    """获取正式需求列表（已发布的文档）"""
    try:
        requirements_dir = _data_provider.data_dir / "requirements"
        
        if not requirements_dir.exists():
            return {
                "success": True,
                "total": 0,
                "modules": [],
                "requirements": []
            }
        
        requirements = []
        modules = set()
        
        # 遍历所有模块目录
        for module_dir in requirements_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            module_name = module_dir.name
            
            # 如果指定了module，筛选
            if module and module_name != module:
                continue
            
            modules.add(module_name)
            
            # 遍历目录下的.md文件
            for md_file in module_dir.glob("*.md"):
                # 跳过索引文件
                if md_file.name.startswith("_"):
                    continue
                
                # 读取文件内容提取信息
                content = md_file.read_text(encoding='utf-8')
                
                # 提取标题（# REQ-XXX: 标题）
                import re
                title_match = re.search(r'^#\s+(REQ-\d+):\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    req_id = title_match.group(1)
                    title = title_match.group(2).strip()
                else:
                    # 兼容旧格式
                    title_match = content.split('\n')[0] if content else ""
                    if title_match.startswith("# "):
                        title = title_match[2:].strip()
                    else:
                        title = md_file.stem
                
                # 提取模块（从内容中）
                module_match = re.search(r'-\s*\*\*模块\*\*:\s*(.+)', content)
                req_module = module_match.group(1).strip() if module_match else module_name
                
                requirements.append({
                    "file_name": md_file.name,
                    "title": title,
                    "module": module_name,
                    "path": str(md_file),
                    "updated_at": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                    "size_kb": round(md_file.stat().st_size / 1024, 2)
                })
        
        # 按更新时间倒序
        requirements.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return {
            "success": True,
            "total": len(requirements),
            "modules": sorted(list(modules)),
            "requirements": requirements
        }
    except Exception as e:
        import traceback
        error_detail = f"获取失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/requirements/formal/{module}/{file_name:path}", summary="获取正式需求详情")
async def get_formal_requirement(module: str, file_name: str):
    """获取正式需求的完整Markdown内容"""
    try:
        file_path = _data_provider.data_dir / "requirements" / module / file_name
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="需求文件不存在")
        
        content = file_path.read_text(encoding='utf-8')
        
        return {
            "success": True,
            "file_name": file_name,
            "module": module,
            "content": content,
            "updated_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "size_kb": round(file_path.stat().st_size / 1024, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@app.put("/api/requirements/formal/{module}/{file_name:path}", summary="更新正式需求")
async def update_formal_requirement(module: str, file_name: str, request: dict):
    """更新正式需求的Markdown内容"""
    try:
        file_path = _data_provider.data_dir / "requirements" / module / file_name
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="需求文件不存在")
        
        content = request.get("content", "")
        if not content:
            raise HTTPException(status_code=400, detail="content 不能为空")
        
        file_path.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "message": "需求更新成功",
            "updated_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@app.delete("/api/requirements/formal/{module}/{file_name:path}", summary="删除正式需求")
async def delete_formal_requirement(module: str, file_name: str):
    """删除正式需求文件"""
    try:
        file_path = _data_provider.data_dir / "requirements" / module / file_name
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="需求文件不存在")
        
        file_path.unlink()
        
        return {
            "success": True,
            "message": f"需求已删除: {file_name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@app.post("/api/requirements/formal/{module}/{file_name:path}/publish", summary="发布正式需求")
async def publish_formal_requirement(module: str, file_name: str, request: dict = None):
    """
    发布正式需求（从草稿发布）
    
    请求体示例(可选):
    ```json
    {
      "target_dir": "/path/to/requirements"
    }
    ```
    """
    try:
        # 读取Markdown文件
        drafts_dir = _data_provider.data_dir / "drafts"
        md_file = drafts_dir / f"{file_name}.md"
        
        if not md_file.exists():
            raise HTTPException(status_code=404, detail=f"草稿不存在: {file_name}")
        
        markdown_content = md_file.read_text(encoding='utf-8')
        
        # 确定目标目录
        target_dir = None
        if request:
            target_dir = request.get("target_dir")
        
        if target_dir is None:
            target_dir = _data_provider.data_dir / "requirements"
        else:
            target_dir = Path(target_dir)
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 从Markdown中提取模块名称（第一个REQ的模块）
        import re
        module_match = re.search(r'-\s*模块:\s*(.+)', markdown_content)
        module_name = module_match.group(1).strip() if module_match else "未分类"
        
        # 保存为正式文档
        module_dir = target_dir / module_name
        module_dir.mkdir(parents=True, exist_ok=True)
        
        file_name_out = f"{file_name}_structured_requirements.md"
        file_path = module_dir / file_name_out
        
        # 添加发布标记
        content_with_marker = markdown_content + f"\n\n---\n**状态**: 正式文档\n**发布时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        file_path.write_text(content_with_marker, encoding='utf-8')
        
        # 删除草稿（发布后草稿不再显示在草稿箱）
        drafts_dir = _data_provider.data_dir / "drafts"
        meta_file = drafts_dir / f"{file_name}.json"
        if meta_file.exists():
            meta_file.unlink()
        
        # 删除草稿Markdown文件
        if md_file.exists():
            md_file.unlink()
        
        print(f"✅ 草稿已发布: {file_path}")
        
        return {
            "success": True,
            "message": f"草稿已发布为正式文档",
            "file_path": str(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"发布失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


# ============== 草稿管理接口 ==============

@app.post("/api/requirements/analyze-and-create-draft", summary="分析需求并创建草稿")
async def analyze_and_create_draft(request: dict):
    """
    分析需求文档并创建草稿
    
    请求体示例:
    ```json
    {
      "content": "# 用户需求...",
      "source_name": "用户需求文档"
    }
    ```
    
    返回:
    - draft_id: 草稿ID
    - analysis_result: 分析结果(问题列表+结构化需求)
    """
    content = request.get("content", "")
    source_name = request.get("source_name", "未知来源")
    
    if not content:
        raise HTTPException(status_code=400, detail="content 不能为空")
    
    try:
        print(f"🔍 开始分析并创建草稿: {source_name}")
        
        service = RequirementAnalysisService(data_dir=str(_data_provider.data_dir))
        
        # 分析和解析
        analysis_result = service.analyze_and_parse(content, source_name)
        
        # 创建草稿
        draft_id = service.create_draft(analysis_result, source_name, "AI自动解析生成")
        
        print(f"✅ 草稿创建成功: {draft_id}")
        
        # 构建返回数据
        requirements_detail = []
        for req in analysis_result.parsed_requirements:
            requirements_detail.append({
                "id": req.id,
                "title": req.title,
                "module": req.module,
                "sub_module": req.sub_module,
                "priority": req.priority.value,
                "description": req.description,
                "function_points_count": len(req.function_points),
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
                "tags": req.tags
            })
        
        issues_detail = []
        for issue in analysis_result.issues:
            issues_detail.append({
                "id": issue.requirement_issue_id,
                "type": issue.issue_type.value,
                "severity": issue.severity.value,
                "field_name": issue.field_name,
                "description": issue.description,
                "suggestion": issue.suggestion,
                "location": issue.location
            })
        
        return {
            "success": True,
            "draft_id": draft_id,
            "source_name": source_name,
            "analysis_summary": analysis_result.analysis_summary,
            "total_issues": analysis_result.total_issues,
            "critical_issues": analysis_result.critical_issues,
            "major_issues": analysis_result.major_issues,
            "minor_issues": analysis_result.minor_issues,
            "total_modules": analysis_result.total_modules,
            "total_function_points": analysis_result.total_function_points,
            "total_requirements": len(analysis_result.parsed_requirements),
            "issues": issues_detail,
            "requirements": requirements_detail
        }
    except Exception as e:
        import traceback
        error_detail = f"创建草稿失败: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/requirements/drafts", summary="获取草稿列表")
async def get_drafts(module: Optional[str] = Query(None, description="按模块筛选")):
    """获取草稿列表"""
    try:
        service = RequirementAnalysisService(data_dir=str(_data_provider.data_dir))
        drafts = service.list_drafts(module)
        
        return {
            "success": True,
            "total": len(drafts),
            "drafts": drafts
        }
    except Exception as e:
        import traceback
        error_detail = f"获取草稿列表失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/requirements/draft/{draft_id}", summary="获取草稿详情")
async def get_draft_detail(draft_id: str):
    """获取草稿详情"""
    try:
        service = RequirementAnalysisService(data_dir=str(_data_provider.data_dir))
        draft_data = service.get_draft(draft_id)
        
        if not draft_data:
            raise HTTPException(status_code=404, detail=f"草稿不存在: {draft_id}")
        
        return {
            "success": True,
            "draft": draft_data
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"获取草稿详情失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.put("/api/requirements/draft/{draft_id}", summary="更新草稿")
async def update_draft(draft_id: str, request: dict):
    """
    更新草稿
    
    请求体示例:
    ```json
    {
      "requirements": [...],
      "comment": "手动编辑需求"
    }
    ```
    """
    requirements = request.get("requirements", [])
    comment = request.get("comment", "")
    
    if not requirements:
        raise HTTPException(status_code=400, detail="requirements 不能为空")
    
    try:
        service = RequirementAnalysisService(data_dir=str(_data_provider.data_dir))
        success = service.update_draft(draft_id, requirements, comment)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"草稿不存在: {draft_id}")
        
        return {
            "success": True,
            "message": "草稿更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"更新草稿失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.delete("/api/requirements/draft/{draft_id}", summary="删除草稿")
async def delete_draft(draft_id: str):
    """删除草稿"""
    try:
        service = RequirementAnalysisService(data_dir=str(_data_provider.data_dir))
        success = service.delete_draft(draft_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"草稿不存在: {draft_id}")
        
        return {
            "success": True,
            "message": f"草稿 {draft_id} 已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"删除草稿失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/requirements/draft/{draft_id}/publish", summary="发布草稿为正式文档")
async def publish_draft(draft_id: str, request: dict = None):
    """
    发布草稿为正式文档
    
    请求体示例(可选):
    ```json
    {
      "target_dir": "/path/to/requirements"
    }
    ```
    """
    try:
        target_dir = None
        if request:
            target_dir = request.get("target_dir")
        
        service = RequirementAnalysisService(data_dir=str(_data_provider.data_dir))
        success, saved_files = service.publish_to_formal(draft_id, target_dir)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"发布失败,草稿可能为空或不存在: {draft_id}")
        
        return {
            "success": True,
            "message": f"草稿已发布为正式文档,共保存 {len(saved_files)} 个文件",
            "saved_files": saved_files
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"发布草稿失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


# ============== 测试用例生成接口 ==============

@app.post("/api/testcases/generate", summary="生成测试用例（仅预览，不保存）")
async def generate_test_cases(request: dict):
    """
    根据结构化需求生成测试用例（仅预览，不保存到文件）
    
    请求体示例:
    ```json
    {
      "requirements": [...],
      "module": "用户管理"
    }
    ```
    """
    requirements = request.get("requirements", [])
    module = request.get("module", "")
    
    if not requirements:
        raise HTTPException(status_code=400, detail="requirements 不能为空")
    if not module:
        raise HTTPException(status_code=400, detail="module 不能为空")
    
    try:
        # 统计已有用例数
        output_dir = _data_provider.data_dir / "testcases"
        module_dir = output_dir / module
        existing_tc_count = 0
        if module_dir.exists():
            index_file = module_dir / "testcase_index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    existing_tc_count = len(index_data.get("test_cases", []))
        
        print(f"🔍 开始为模块 {module} 生成测试用例（已有 {existing_tc_count} 条）")
        
        # 生成测试用例（不保存）
        generator = TestCaseGenerator(output_dir)
        result = generator.generate_from_requirements(requirements, module, existing_tc_count)
        
        return {
            "success": True,
            "module": module,
            "generation_summary": result.get('generation_summary', ''),
            "total_test_cases": len(result.get('test_cases', [])),
            "warnings": result.get('warnings', []),
            "test_cases": result.get('test_cases', [])
        }
        
    except Exception as e:
        import traceback
        error_detail = f"生成失败: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/testcases/save", summary="保存测试用例到文件")
async def save_test_cases(request: dict):
    """
    保存测试用例到文件
    
    请求体示例:
    ```json
    {
      "module": "用户管理",
      "test_cases": [...]
    }
    ```
    """
    module = request.get("module", "")
    test_cases = request.get("test_cases", [])
    
    if not module:
        raise HTTPException(status_code=400, detail="module 不能为空")
    if not test_cases:
        raise HTTPException(status_code=400, detail="test_cases 不能为空")
    
    try:
        output_dir = _data_provider.data_dir / "testcases"
        
        # 保存用例
        generator = TestCaseGenerator(output_dir)
        saved_files = generator.save_test_cases(test_cases, module)
        print(f"💾 保存了 {len(saved_files)} 条测试用例")
        
        return {
            "success": True,
            "message": f"成功保存 {len(saved_files)} 条测试用例",
            "saved_files": saved_files
        }
        
    except Exception as e:
        import traceback
        error_detail = f"保存失败: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/testcases/modules", summary="获取已有测试用例模块列表")
async def get_testcase_modules():
    """获取所有已有测试用例的模块列表"""
    tc_dir = _data_provider.data_dir / "testcases"

    if not tc_dir.exists():
        return {"modules": []}

    modules = []
    for module_dir in tc_dir.iterdir():
        if module_dir.is_dir():
            # 修复：查找 _index.json 而不是 testcase_index.json
            index_file = module_dir / "_index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    modules.append({
                        "module": index_data.get("module", module_dir.name),
                        "total_test_cases": len(index_data.get("test_cases", []))
                    })

    return {"modules": modules}


# ============== 测试用例草稿管理接口 ==============

@app.post("/api/testcases/generate-and-create-draft", summary="生成用例并创建草稿")
async def generate_and_create_draft(request: dict):
    """
    根据输入文本或选择的需求生成测试用例并创建草稿

    请求体示例:
    ```json
    {
      "source_type": "text",
      "input_text": "需求文本...",
      "module": "用户管理",
      "selected_requirements": []
    }
    ```
    """
    source_type = request.get("source_type", "text")
    input_text = request.get("input_text", "")
    module = request.get("module", "未分类")
    selected_requirements = request.get("selected_requirements", [])

    try:
        service = TestCaseGenerationService()

        result = service.generate_test_cases(
            input_text=input_text if source_type == "text" else None,
            requirements=selected_requirements if source_type == "requirement" else None,
            module=module,
            source_type=source_type
        )

        if not result.get("test_cases"):
            return {
                "success": False,
                "message": "未生成任何测试用例",
                "warnings": result.get("warnings", [])
            }

        draft_id = service.create_draft(
            test_cases=result.get("test_cases", []),
            module=module,
            sub_module=result.get("sub_module"),
            source_type=source_type,
            input_text=input_text,
            selected_requirements=selected_requirements,
            generation_summary=result.get("generation_summary", "")
        )

        return {
            "success": True,
            "draft_id": draft_id,
            "module": module,
            "total_test_cases": len(result.get("test_cases", [])),
            "generation_summary": result.get("generation_summary", ""),
            "warnings": result.get("warnings", [])
        }

    except Exception as e:
        import traceback
        error_detail = f"生成失败: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/testcases/drafts", summary="获取用例草稿列表")
async def list_testcase_drafts(module: str = Query(None, description="按模块筛选")):
    """获取所有用例草稿列表"""
    try:
        service = TestCaseGenerationService()
        drafts = service.list_drafts(module=module)
        return {"success": True, "drafts": drafts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取草稿列表失败: {str(e)}")


@app.get("/api/testcases/draft/{draft_id}", summary="获取用例草稿详情")
async def get_testcase_draft(draft_id: str):
    """获取用例草稿详情"""
    try:
        service = TestCaseGenerationService()
        draft = service.get_draft(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail=f"草稿 {draft_id} 不存在")
        return {"success": True, "draft": draft}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取草稿失败: {str(e)}")


@app.get("/api/testcases/draft/{draft_id}/testcases", summary="获取用例草稿的测试用例数据")
async def get_testcase_draft_testcases(draft_id: str):
    """获取用例草稿的测试用例数据"""
    try:
        service = TestCaseGenerationService()
        test_cases = service.get_draft_test_cases(draft_id)
        if test_cases is None:
            raise HTTPException(status_code=404, detail=f"草稿 {draft_id} 不存在")
        return {"success": True, "test_cases": test_cases}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试用例失败: {str(e)}")


@app.put("/api/testcases/draft/{draft_id}/testcases", summary="保存用例草稿的测试用例数据")
async def save_testcase_draft_testcases(draft_id: str, request: dict):
    """保存用例草稿的测试用例数据"""
    test_cases = request.get("test_cases", [])

    if not test_cases:
        raise HTTPException(status_code=400, detail="test_cases 不能为空")

    try:
        service = TestCaseGenerationService()
        success = service.save_draft_test_cases(draft_id, test_cases)
        if not success:
            raise HTTPException(status_code=404, detail=f"草稿 {draft_id} 不存在")
        return {"success": True, "message": "保存成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@app.delete("/api/testcases/draft/{draft_id}", summary="删除用例草稿")
async def delete_testcase_draft(draft_id: str):
    """删除用例草稿"""
    try:
        service = TestCaseGenerationService()
        success = service.delete_draft(draft_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"草稿 {draft_id} 不存在")
        return {"success": True, "message": f"草稿 {draft_id} 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除草稿失败: {str(e)}")


@app.post("/api/testcases/draft/{draft_id}/publish", summary="发布用例草稿为正式用例")
async def publish_testcase_draft(draft_id: str, request: dict = None):
    """发布用例草稿为正式用例"""
    module = None
    submodule = None
    if request:
        module = request.get("module")
        submodule = request.get("submodule")

    try:
        service = TestCaseGenerationService()
        success, saved_files = service.publish_to_formal(draft_id, module=module, submodule=submodule)
        if not success:
            raise HTTPException(status_code=400, detail=f"草稿 {draft_id} 发布失败，可能没有测试用例")
        return {
            "success": True,
            "message": f"成功发布 {len(saved_files)} 条测试用例",
            "saved_files": saved_files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")


@app.get("/api/testcases/module-index/{module}", summary="获取模块用例索引")
async def get_testcase_module_index(module: str):
    """获取模块用例索引（包含子模块信息）"""
    try:
        tc_dir = _data_provider.data_dir / "testcases" / module
        index_file = tc_dir / "_index.json"

        if not index_file.exists():
            return {"index": {"module": module, "submodules": {}}}

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        return {"index": index_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取索引失败: {str(e)}")


@app.get("/api/testcases/modules/{module}/submodules", summary="获取模块下的子模块列表")
async def get_submodules(module: str):
    """获取指定模块下的所有子模块列表"""
    try:
        tc_dir = _data_provider.data_dir / "testcases" / module
        index_file = tc_dir / "_index.json"

        if not index_file.exists():
            return {"success": True, "module": module, "submodules": []}

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        submodules = []
        submodules_data = index_data.get("submodules", {})
        
        for sub_name, tc_ids in submodules_data.items():
            submodules.append({
                "name": sub_name,
                "case_count": len(tc_ids)
            })

        return {
            "success": True,
            "module": module,
            "submodules": submodules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取子模块列表失败: {str(e)}")


@app.get("/api/testcases/modules/{module}/submodules/{submodule:path}", summary="获取子模块下的用例列表")
async def get_testcases_by_submodule(module: str, submodule: str):
    """获取指定子模块下的所有测试用例列表"""
    try:
        tc_dir = _data_provider.data_dir / "testcases" / module
        index_file = tc_dir / "_index.json"

        if not index_file.exists():
            return {"success": True, "total": 0, "test_cases": []}

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        test_cases = index_data.get("test_cases", [])
        filtered_cases = [tc for tc in test_cases if tc.get("submodule") == submodule]

        for tc in filtered_cases:
            tc["module"] = module

        return {
            "success": True,
            "module": module,
            "submodule": submodule,
            "total": len(filtered_cases),
            "test_cases": filtered_cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用例列表失败: {str(e)}")


@app.get("/api/testcases/cases/{module}/{submodule:path}/{case_id}", summary="获取测试用例详情")
async def get_testcase_detail(module: str, submodule: str, case_id: str):
    """获取指定测试用例的完整详情"""
    try:
        import yaml
        
        tc_dir = _data_provider.data_dir / "testcases" / module
        index_file = tc_dir / "_index.json"

        if not index_file.exists():
            raise HTTPException(status_code=404, detail=f"模块不存在: {module}")

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        test_cases = index_data.get("test_cases", [])
        case_info = None
        for tc in test_cases:
            if tc.get("id") == case_id and tc.get("submodule") == submodule:
                case_info = tc
                break

        if not case_info:
            raise HTTPException(status_code=404, detail=f"测试用例不存在: {case_id}")

        case_file = tc_dir / case_info.get("file", "")
        if not case_file.exists():
            raise HTTPException(status_code=404, detail=f"测试用例文件不存在: {case_file}")

        with open(case_file, 'r', encoding='utf-8') as f:
            case_data = yaml.safe_load(f)

        case_data["module"] = module
        case_data["file_path"] = str(case_file)

        return {
            "success": True,
            "test_case": case_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用例详情失败: {str(e)}")


@app.put("/api/testcases/cases/{module}/{submodule:path}/{case_id}", summary="更新测试用例")
async def update_testcase(module: str, submodule: str, case_id: str, request: dict):
    """更新测试用例内容"""
    try:
        import yaml
        
        tc_dir = _data_provider.data_dir / "testcases" / module
        index_file = tc_dir / "_index.json"

        if not index_file.exists():
            raise HTTPException(status_code=404, detail=f"模块不存在: {module}")

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        test_cases = index_data.get("test_cases", [])
        case_info = None
        case_index = -1
        for i, tc in enumerate(test_cases):
            if tc.get("id") == case_id and tc.get("submodule") == submodule:
                case_info = tc
                case_index = i
                break

        if not case_info:
            raise HTTPException(status_code=404, detail=f"测试用例不存在: {case_id}")

        case_file = tc_dir / case_info.get("file", "")
        if not case_file.exists():
            raise HTTPException(status_code=404, detail=f"测试用例文件不存在")

        updated_case = request.get("test_case", {})
        if not updated_case:
            raise HTTPException(status_code=400, detail="test_case 不能为空")

        updated_case["updated_at"] = datetime.now().isoformat()

        with open(case_file, 'w', encoding='utf-8') as f:
            yaml.dump(updated_case, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        index_data["test_cases"][case_index]["title"] = updated_case.get("title", case_info.get("title"))
        index_data["test_cases"][case_index]["status"] = updated_case.get("status", case_info.get("status"))
        index_data["test_cases"][case_index]["priority"] = updated_case.get("priority", case_info.get("priority"))
        index_data["test_cases"][case_index]["case_type"] = updated_case.get("case_type", case_info.get("case_type"))

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": "测试用例更新成功",
            "test_case": updated_case
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"更新用例失败: {str(e)}\n{traceback.format_exc()}")


@app.delete("/api/testcases/cases/{module}/{submodule:path}/{case_id}", summary="删除测试用例")
async def delete_testcase(module: str, submodule: str, case_id: str):
    """删除指定的测试用例"""
    try:
        tc_dir = _data_provider.data_dir / "testcases" / module
        index_file = tc_dir / "_index.json"

        if not index_file.exists():
            raise HTTPException(status_code=404, detail=f"模块不存在: {module}")

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        test_cases = index_data.get("test_cases", [])
        case_info = None
        case_index = -1
        for i, tc in enumerate(test_cases):
            if tc.get("id") == case_id and tc.get("submodule") == submodule:
                case_info = tc
                case_index = i
                break

        if not case_info:
            raise HTTPException(status_code=404, detail=f"测试用例不存在: {case_id}")

        case_file = tc_dir / case_info.get("file", "")
        if case_file.exists():
            case_file.unlink()

        index_data["test_cases"].pop(case_index)

        if case_id in index_data.get("submodules", {}).get(submodule, []):
            index_data["submodules"][submodule].remove(case_id)

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": f"测试用例 {case_id} 已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用例失败: {str(e)}")


# ============== 质量分析与预测接口 ==============

@app.get("/api/quality/analysis", summary="质量分析")
async def get_quality_analysis():
    """
    综合分析质量
    返回各模块质量指标、缺陷密度、需求覆盖率等
    """
    result = analyze_quality()
    return result.model_dump(mode='json')


@app.get("/api/quality/bug-trend", summary="BUG趋势预测")
async def get_bug_trend(days: int = Query(7, ge=1, le=30, description="预测天数")):
    """预测未来N天的BUG趋势"""
    result = predict_bug_trend(days=days)
    return {"predictions": [p.model_dump(mode='json') for p in result]}


@app.get("/api/quality/bug-prediction", summary="模块BUG预测")
async def get_bug_prediction():
    """按模块预测未来可能出现的BUG数量"""
    result = predict_bugs_by_module()
    return {"predictions": [p.model_dump(mode='json') for p in result]}


# ============== AI 辅助测试接口 ==============


@app.get("/api/ai/bug-analysis", summary="BUG根因分析")
async def analyze_bug(bug_id: str = Query(..., description="BUG ID")):
    """分析BUG根因，推荐可能的原因和修复方案"""
    from modules.ai_assisted_testing import analyze_bug_root_cause
    
    result = analyze_bug_root_cause(bug_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"未找到BUG: {bug_id}")
    
    return result.model_dump(mode='json')


@app.get("/api/ai/recommend-test-cases", summary="推荐测试用例")
async def recommend_test_cases(
    code_files: str = Query(..., description="修改的代码文件路径，多个用逗号分隔"),
    module: Optional[str] = Query(None, description="模块名称")
):
    """根据代码修改推荐需要回归的测试用例"""
    from modules.ai_assisted_testing import recommend_test_cases_for_code_change
    
    files = [f.strip() for f in code_files.split(",")]
    result = recommend_test_cases_for_code_change(files, module)
    
    return {"recommended_count": len(result), "test_cases": [tc.model_dump(mode='json') for tc in result]}


@app.post("/api/ai/requirement-impact-analysis", summary="🆕 新需求影响分析", tags=["AI 辅助测试"])
async def analyze_requirement_impact(
    request: dict
):
    """
    **新需求影响分析功能**
    
    输入新需求的完整内容（Markdown 格式），系统将：
    1. 使用 RAG 检索受影响的历史需求
    2. 推荐需要回归的测试用例
    3. 生成测试建议
    
    请求体示例:
    ```json
    {
      "requirement_content": "# REQ-010: 用户单点登录功能\\n\\n## 需求描述\\n实现单点登录...",
      "module": "用户管理"
    }
    ```
    """
    from modules.ai_assisted_testing import analyze_new_requirement_impact

    requirement_content = request.get("requirement_content", "")
    module = request.get("module")

    if not requirement_content:
        raise HTTPException(status_code=400, detail="requirement_content 不能为空")

    result = analyze_new_requirement_impact(requirement_content, module)
    return result


@app.post("/api/ai/assisted-test", summary="AI辅助测试（综合接口）")
async def ai_assisted_test(
    requirement_id: Optional[str] = None,
    bug_id: Optional[str] = None,
    code_files: Optional[str] = None,
    module: Optional[str] = None
):
    """
    AI辅助测试统一接口
    - requirement_id: 生成测试用例
    - bug_id: BUG根因分析
    - code_files: 推荐测试用例（逗号分隔的文件路径）
    """
    files = [f.strip() for f in code_files.split(",")] if code_files else None
    result = ai_assisted_test(requirement_id, bug_id, files, module)
    return result.model_dump(mode='json')


# ============== 知识管理接口 ==============

@app.get("/api/knowledge/training", summary="培训材料")
async def get_training_materials():
    """生成新人培训材料"""
    from modules.knowledge_management import generate_training_materials
    
    result = generate_training_materials()
    return {"total": len(result), "materials": [tm.model_dump(mode='json') for tm in result]}


@app.get("/api/knowledge/historical-bugs", summary="历史BUG案例")
async def get_historical_bugs(limit: int = Query(20, ge=1, le=50, description="返回数量")):
    """收集历史BUG案例，用于经验沉淀"""
    from modules.knowledge_management import collect_historical_bugs
    
    result = collect_historical_bugs(limit=limit)
    return {"total": len(result), "bugs": [bug.model_dump(mode='json') for bug in result]}


@app.get("/api/knowledge/search", summary="智能搜索")
async def search_knowledge(query: str = Query(..., description="搜索关键词")):
    """智能搜索，返回需求+用例+BUG全链路信息"""
    result = manage_knowledge(query)
    return {"total": len(result.search_results), "results": [r.model_dump(mode='json') for r in result.search_results]}


@app.get("/api/knowledge/qa", summary="常见问答")
async def get_qa_pairs():
    """获取常见问答对，用于新人培训"""
    from modules.knowledge_management import generate_qa_pairs
    
    result = generate_qa_pairs()
    return {"total": len(result), "qa_pairs": result}


# ============== 智能报告接口 ==============

@app.get("/api/report/project", summary="项目质量报告")
async def get_project_quality_report():
    """生成完整的项目质量报告"""
    result = generate_smart_report()
    return result.model_dump(mode='json')


@app.get("/api/report/module", summary="模块质量报告")
async def get_module_quality_report(module: str = Query(..., description="模块名称")):
    """生成指定模块的质量报告"""
    result = generate_module_report(module)
    if not result:
        raise HTTPException(status_code=404, detail=f"未找到模块: {module}")
    
    return result.model_dump(mode='json')


@app.get("/api/report/all-modules", summary="所有模块报告")
async def get_all_module_reports():
    """生成所有模块的质量报告"""
    from modules.smart_report import generate_all_module_reports

    result = generate_all_module_reports()
    return {"total": len(result), "reports": [r.model_dump(mode='json') for r in result]}


# ============== 索引管理接口 ==============

@app.post("/api/index/update", summary="更新索引")
async def update_index(request: dict = None):
    """
    更新索引（需求、测试用例、BUG）
    
    请求体示例:
    ```json
    {
      "type": "requirements",  // requirements/testcases/bugs/all
      "module": "用户管理"      // 可选，不指定则更新所有模块
    }
    ```
    """
    if request is None:
        request = {}
    
    index_type = request.get("type", "all")
    module = request.get("module")
    
    try:
        index_manager = get_index_manager(str(_data_provider.data_dir))
        
        if index_type == "requirements":
            index_manager.update_requirements_index(module)
            message = f"需求索引已更新: {module or '所有模块'}"
        elif index_type == "testcases":
            index_manager.update_testcases_index(module)
            message = f"测试用例索引已更新: {module or '所有模块'}"
        elif index_type == "bugs":
            index_manager.update_bugs_index(module)
            message = f"BUG索引已更新: {module or '所有模块'}"
        elif index_type == "all":
            index_manager.update_all_indexes()
            message = "所有索引已更新"
        else:
            raise ValueError(f"不支持的索引类型: {index_type}")
        
        return {
            "success": True,
            "message": message,
            "type": index_type,
            "module": module
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引更新失败: {str(e)}")


@app.get("/api/index/status", summary="获取索引状态")
async def get_index_status():
    """获取各索引的状态和最后更新时间"""
    data_dir = _data_provider.data_dir
    status = {}
    
    # 需求索引
    req_index = data_dir / "requirements" / "_index.json"
    if req_index.exists():
        with open(req_index, 'r', encoding='utf-8') as f:
            req_data = json.load(f)
            status["requirements"] = {
                "total": len(req_data.get("requirements", [])),
                "modules": req_data.get("modules", []),
                "last_updated": req_data.get("last_updated", "")
            }
    else:
        status["requirements"] = {"total": 0, "modules": [], "last_updated": ""}
    
    # 测试用例索引
    tc_dir = data_dir / "testcases"
    tc_modules = []
    tc_total = 0
    if tc_dir.exists():
        for module_dir in tc_dir.iterdir():
            if module_dir.is_dir():
                index_file = module_dir / "testcase_index.json"
                if index_file.exists():
                    with open(index_file, 'r', encoding='utf-8') as f:
                        tc_data = json.load(f)
                        tc_count = len(tc_data.get("test_cases", []))
                        tc_modules.append(module_dir.name)
                        tc_total += tc_count
    status["testcases"] = {
        "total": tc_total,
        "modules": sorted(tc_modules),
        "last_updated": ""
    }
    
    # BUG索引
    bug_dir = data_dir / "bugs"
    bug_modules = []
    bug_total = 0
    if bug_dir.exists():
        for module_dir in bug_dir.iterdir():
            if module_dir.is_dir():
                index_file = module_dir / "bug_index.json"
                if index_file.exists():
                    with open(index_file, 'r', encoding='utf-8') as f:
                        bug_data = json.load(f)
                        bug_count = len(bug_data.get("bugs", []))
                        bug_modules.append(module_dir.name)
                        bug_total += bug_count
    status["bugs"] = {
        "total": bug_total,
        "modules": sorted(bug_modules),
        "last_updated": ""
    }
    
    return status


# ============== 启动入口 ==============

if __name__ == "__main__":
    print("=" * 60)
    print("智能质量保证系统 v2.0.0")
    print("=" * 60)
    print("启动服务器...")
    print("访问 API 文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
