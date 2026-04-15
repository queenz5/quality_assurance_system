"""
MCP QA Tools - 质量保证系统工具服务
为 LLM 提供访问质量保障系统数据的能力
"""
from mcp.server.fastmcp import FastMCP
from data.file_provider import get_data_provider
from typing import List, Dict, Any, Optional
import os

# 创建 MCP Server 实例
server = FastMCP(
    name="quality-assurance-system"
)

_data_provider = get_data_provider()


@server.tool()
async def list_modules() -> List[str]:
    """获取所有模块列表"""
    return _data_provider.get_modules()


@server.tool()
async def get_data_statistics() -> Dict[str, Any]:
    """获取数据统计信息，包括需求、测试用例、BUG的总数和模块列表"""
    stats = _data_provider.get_statistics()
    return stats


@server.tool()
async def get_all_requirements() -> List[Dict[str, Any]]:
    """获取所有需求数据，返回结构化的需求列表"""
    requirements = _data_provider.get_all_requirements()
    return [req.model_dump(mode='json') for req in requirements]


@server.tool()
async def get_all_test_cases() -> List[Dict[str, Any]]:
    """获取所有测试用例数据，返回结构化的测试用例列表"""
    test_cases = _data_provider.get_all_test_cases()
    return [tc.model_dump(mode='json') for tc in test_cases]


@server.tool()
async def get_all_bugs() -> List[Dict[str, Any]]:
    """获取所有BUG数据，返回结构化的BUG列表"""
    bugs = _data_provider.get_all_bugs()
    return [bug.model_dump(mode='json') for bug in bugs]


@server.tool()
async def get_requirements_by_module(module: str) -> List[Dict[str, Any]]:
    """
    根据模块名称获取相关需求

    Args:
        module: 模块名称，如"用户管理"、"订单管理"等
    """
    requirements = _data_provider.get_requirements_by_module(module)
    return [req.model_dump(mode='json') for req in requirements]


@server.tool()
async def get_test_cases_by_module(module: str) -> List[Dict[str, Any]]:
    """
    根据模块名称获取相关测试用例

    Args:
        module: 模块名称
    """
    test_cases = _data_provider.get_test_cases_by_module(module)
    return [tc.model_dump(mode='json') for tc in test_cases]


@server.tool()
async def get_bugs_by_module(module: str) -> List[Dict[str, Any]]:
    """
    根据模块名称获取相关BUG

    Args:
        module: 模块名称
    """
    bugs = _data_provider.get_bugs_by_module(module)
    return [bug.model_dump(mode='json') for bug in bugs]


@server.tool()
async def get_test_cases_by_requirement(requirement_id: str) -> List[Dict[str, Any]]:
    """
    根据需求ID获取相关测试用例

    Args:
        requirement_id: 需求ID，如"REQ-001"
    """
    test_cases = _data_provider.get_test_cases_by_requirement(requirement_id)
    return [tc.model_dump(mode='json') for tc in test_cases]


@server.tool()
async def get_bugs_by_test_case(test_case_id: str) -> List[Dict[str, Any]]:
    """
    根据测试用例ID获取相关BUG

    Args:
        test_case_id: 测试用例ID，如"TC-001"
    """
    bugs = _data_provider.get_bugs_by_test_case(test_case_id)
    return [bug.model_dump(mode='json') for bug in bugs]


@server.tool()
async def get_bugs_by_requirement(requirement_id: str) -> List[Dict[str, Any]]:
    """
    根据需求ID获取相关BUG

    Args:
        requirement_id: 需求ID
    """
    bugs = _data_provider.get_bugs_by_requirement(requirement_id)
    return [bug.model_dump(mode='json') for bug in bugs]


@server.tool()
async def get_module_overview(module: str) -> Dict[str, Any]:
    """
    获取模块完整概览（管理后台展示用）
    按需求组织，包含每个需求关联的测试用例和BUG

    Args:
        module: 模块名称
    """
    return _data_provider.get_module_overview(module)
