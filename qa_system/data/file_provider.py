"""
文件数据提供者
从 Markdown 需求文档、YAML 测试用例和 BUG 文件中加载数据
"""
import os
import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from modules.models import (
    Requirement, TestCase, Bug,
    Priority, RequirementStatus, TestCaseStatus,
    BugSeverity, BugStatus
)


class FileDataProvider:
    """基于文件的数据提供者"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self._requirements: List[Requirement] = []
        self._test_cases: List[TestCase] = []
        self._bugs: List[Bug] = []
        self._tc_index: Dict[str, Dict[str, Any]] = {}  # 模块 -> 测试用例索引
        self._bug_index: Dict[str, Dict[str, Any]] = {}  # 模块 -> BUG索引
        self._load_all_data()

    def _load_all_data(self):
        """加载所有数据"""
        self._requirements = self._load_requirements()
        self._tc_index = self._load_all_tc_index()
        self._bug_index = self._load_all_bug_index()
        self._test_cases = self._load_all_test_cases()
        self._bugs = self._load_all_bugs()

    # ============== 需求加载 ==============

    def _load_requirements(self) -> List[Requirement]:
        """加载所有需求文档"""
        requirements = []
        req_dir = self.data_dir / "requirements"

        if not req_dir.exists():
            return requirements

        for module_dir in req_dir.iterdir():
            if module_dir.is_dir():
                for md_file in module_dir.glob("REQ-*.md"):
                    req = self._parse_requirement_doc(md_file)
                    if req:
                        requirements.append(req)

        return requirements

    def _parse_requirement_doc(self, file_path: Path) -> Optional[Requirement]:
        """解析单个需求 Markdown 文档"""
        content = file_path.read_text(encoding='utf-8')

        # 提取需求ID和标题
        header_match = re.match(r'# (REQ-\d+):\s*(.+)', content)
        if not header_match:
            return None

        req_id = header_match.group(1)
        title = header_match.group(2).strip()

        # 提取字段
        module = self._extract_field(content, r'\*\*模块\*\*:\s*(.+)')
        sub_module = self._extract_field(content, r'\*\*子模块\*\*:\s*(.+)')
        priority_str = self._extract_field(content, r'\*\*优先级\*\*:\s*(.+)')
        status_str = self._extract_field(content, r'\*\*状态\*\*:\s*(.+)')
        created_at_str = self._extract_field(content, r'\*\*创建时间\*\*:\s*(.+)')
        updated_at_str = self._extract_field(content, r'\*\*更新时间\*\*:\s*(.+)')
        description = self._extract_section(content, '## 需求描述', '##')
        tags_str = self._extract_section(content, '## 标签', '##')
        change_history = self._extract_change_history(content)

        # 转换枚举值
        priority_map = {
            "高": Priority.HIGH,
            "中": Priority.MEDIUM,
            "低": Priority.LOW
        }
        status_map = {
            "已完成": RequirementStatus.COMPLETED,
            "进行中": RequirementStatus.IN_PROGRESS,
            "未开始": RequirementStatus.NOT_STARTED,
            "已变更": RequirementStatus.CHANGED
        }

        # 解析标签
        tags = [t.strip() for t in tags_str.split(',')] if tags_str else []

        # 解析时间
        try:
            created_at = datetime.fromisoformat(created_at_str)
            updated_at = datetime.fromisoformat(updated_at_str)
        except (ValueError, TypeError):
            created_at = datetime.now()
            updated_at = datetime.now()

        return Requirement(
            id=req_id,
            title=title,
            description=description,
            module=module,
            sub_module=sub_module if sub_module else None,
            priority=priority_map.get(priority_str, Priority.MEDIUM),
            status=status_map.get(status_str, RequirementStatus.NOT_STARTED),
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
            change_history=change_history
        )

    def _extract_field(self, content: str, pattern: str) -> str:
        """提取单个字段"""
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    def _extract_section(self, content: str, section_name: str, next_section_prefix: str) -> str:
        """提取章节内容"""
        pattern = rf'{re.escape(section_name)}\s*\n(.*?)(?=\n{re.escape(next_section_prefix)}\s|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_change_history(self, content: str) -> List[Dict[str, Any]]:
        """提取变更历史"""
        changes = []
        table_match = re.search(r'## 变更历史\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not table_match:
            return changes

        for line in table_match.group(1).strip().split('\n'):
            if '|' not in line or line.startswith('|---') or line.startswith('| 日期'):
                continue
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(cells) >= 3:
                changes.append({
                    "date": cells[0],
                    "action": cells[1],
                    "description": cells[2]
                })

        return changes

    # ============== 索引加载 ==============

    def _load_all_tc_index(self) -> Dict[str, Dict[str, Any]]:
        """加载所有测试用例索引"""
        index = {}
        tc_dir = self.data_dir / "testcases"

        if not tc_dir.exists():
            return index

        for module_dir in tc_dir.iterdir():
            if module_dir.is_dir():
                index_file = module_dir / "testcase_index.json"
                if index_file.exists():
                    with open(index_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        index[data["module"]] = data

        return index

    def _load_all_bug_index(self) -> Dict[str, Dict[str, Any]]:
        """加载所有BUG索引"""
        index = {}
        bug_dir = self.data_dir / "bugs"

        if not bug_dir.exists():
            return index

        for module_dir in bug_dir.iterdir():
            if module_dir.is_dir():
                index_file = module_dir / "bug_index.json"
                if index_file.exists():
                    with open(index_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        index[data["module"]] = data

        return index

    # ============== 测试用例加载 ==============

    def _load_all_test_cases(self) -> List[TestCase]:
        """加载所有测试用例"""
        test_cases = []
        tc_dir = self.data_dir / "testcases"

        if not tc_dir.exists():
            return test_cases

        for module_dir in tc_dir.iterdir():
            if module_dir.is_dir():
                for yaml_file in module_dir.rglob("TC-*.yaml"):
                    tc = self._parse_test_case_yaml(yaml_file)
                    if tc:
                        test_cases.append(tc)

        return test_cases

    def _parse_test_case_yaml(self, file_path: Path) -> Optional[TestCase]:
        """解析单个测试用例 YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception:
            return None

        priority_map = {"高": Priority.HIGH, "中": Priority.MEDIUM, "低": Priority.LOW}
        status_map = {
            "已执行": TestCaseStatus.EXECUTED,
            "未执行": TestCaseStatus.NOT_EXECUTED,
            "执行中": TestCaseStatus.EXECUTING,
            "阻塞": TestCaseStatus.BLOCKED
        }

        def parse_datetime(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(str(val))
            except (ValueError, TypeError):
                return None

        return TestCase(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            requirement_id=data.get("requirement_id", ""),
            module=data.get("module", ""),
            priority=priority_map.get(data.get("priority", "中"), Priority.MEDIUM),
            status=status_map.get(data.get("status", "未执行"), TestCaseStatus.NOT_EXECUTED),
            steps=data.get("steps", []),
            expected_result=data.get("expected_result", ""),
            actual_result=data.get("actual_result"),
            bugs_found=data.get("bugs_found", []),
            execution_count=data.get("execution_count", 0),
            last_executed_at=parse_datetime(data.get("last_executed_at")),
            created_at=parse_datetime(data.get("created_at")) or datetime.now(),
            updated_at=parse_datetime(data.get("updated_at")) or datetime.now()
        )

    # ============== BUG加载 ==============

    def _load_all_bugs(self) -> List[Bug]:
        """加载所有BUG"""
        bugs = []
        bug_dir = self.data_dir / "bugs"

        if not bug_dir.exists():
            return bugs

        for module_dir in bug_dir.iterdir():
            if module_dir.is_dir():
                for yaml_file in module_dir.rglob("BUG-*.yaml"):
                    bug = self._parse_bug_yaml(yaml_file)
                    if bug:
                        bugs.append(bug)

        return bugs

    def _parse_bug_yaml(self, file_path: Path) -> Optional[Bug]:
        """解析单个 BUG YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception:
            return None

        severity_map = {"严重": BugSeverity.CRITICAL, "一般": BugSeverity.MAJOR, "轻微": BugSeverity.MINOR}
        status_map = {
            "已修复": BugStatus.FIXED,
            "修复中": BugStatus.FIXING,
            "未修复": BugStatus.OPEN,
            "已拒绝": BugStatus.REJECTED,
            "重新打开": BugStatus.REOPENED
        }

        def parse_datetime(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(str(val))
            except (ValueError, TypeError):
                return None

        return Bug(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            test_case_id=data.get("test_case_id"),
            requirement_id=data.get("requirement_id"),
            module=data.get("module", ""),
            severity=severity_map.get(data.get("severity", "一般"), BugSeverity.MAJOR),
            status=status_map.get(data.get("status", "未修复"), BugStatus.OPEN),
            root_cause=data.get("root_cause"),
            root_cause_category=data.get("root_cause_category"),
            fix_solution=data.get("fix_solution"),
            fixed_in_version=data.get("fixed_in_version"),
            assignee=data.get("assignee"),
            reporter=data.get("reporter"),
            created_at=parse_datetime(data.get("created_at")) or datetime.now(),
            updated_at=parse_datetime(data.get("updated_at")) or datetime.now(),
            fixed_at=parse_datetime(data.get("fixed_at"))
        )

    # ============== 数据访问方法 ==============

    def get_modules(self) -> List[str]:
        """获取所有模块列表"""
        return list(set(req.module for req in self._requirements))

    def get_all_requirements(self) -> List[Requirement]:
        """获取所有需求"""
        return self._requirements.copy()

    def get_all_test_cases(self) -> List[TestCase]:
        """获取所有测试用例"""
        return self._test_cases.copy()

    def get_all_bugs(self) -> List[Bug]:
        """获取所有BUG"""
        return self._bugs.copy()

    def get_requirements_by_module(self, module: str) -> List[Requirement]:
        """根据模块获取需求"""
        return [req for req in self._requirements if req.module == module]

    def get_test_cases_by_module(self, module: str) -> List[TestCase]:
        """根据模块获取测试用例"""
        return [tc for tc in self._test_cases if tc.module == module]

    def get_bugs_by_module(self, module: str) -> List[Bug]:
        """根据模块获取BUG"""
        return [bug for bug in self._bugs if bug.module == module]

    def get_test_cases_by_requirement(self, requirement_id: str) -> List[TestCase]:
        """根据需求ID获取测试用例"""
        return [tc for tc in self._test_cases if tc.requirement_id == requirement_id]

    def get_bugs_by_test_case(self, test_case_id: str) -> List[Bug]:
        """根据测试用例ID获取BUG"""
        return [bug for bug in self._bugs if bug.test_case_id == test_case_id]

    def get_bugs_by_requirement(self, requirement_id: str) -> List[Bug]:
        """根据需求ID获取BUG"""
        return [bug for bug in self._bugs if bug.requirement_id == requirement_id]

    def get_module_overview(self, module: str) -> Dict[str, Any]:
        """获取模块完整概览（按需求组织关联数据）"""
        requirements = self.get_requirements_by_module(module)
        test_cases = self.get_test_cases_by_module(module)
        bugs = self.get_bugs_by_module(module)

        executed_count = sum(1 for tc in test_cases if tc.status == TestCaseStatus.EXECUTED)
        fixed_count = sum(1 for b in bugs if b.status == BugStatus.FIXED)

        result = {
            "module": module,
            "summary": {
                "total_requirements": len(requirements),
                "total_test_cases": len(test_cases),
                "executed_test_cases": executed_count,
                "execution_rate": round(executed_count / len(test_cases) * 100, 1) if test_cases else 0,
                "total_bugs": len(bugs),
                "fixed_bugs": fixed_count,
                "bug_fix_rate": round(fixed_count / len(bugs) * 100, 1) if bugs else 0
            },
            "requirements": []
        }

        for req in requirements:
            req_test_cases = [tc for tc in test_cases if tc.requirement_id == req.id]
            req_bugs = [b for b in bugs if b.requirement_id == req.id]

            result["requirements"].append({
                "requirement": req.model_dump(mode='json'),
                "test_cases": [tc.model_dump(mode='json') for tc in req_test_cases],
                "bugs": [b.model_dump(mode='json') for b in req_bugs]
            })

        return result

    def get_statistics(self) -> dict:
        """获取数据统计信息"""
        return {
            "total_requirements": len(self._requirements),
            "total_test_cases": len(self._test_cases),
            "total_bugs": len(self._bugs),
            "modules": self.get_modules()
        }


# 全局数据提供者实例
_data_provider: Optional[FileDataProvider] = None


def init_data_provider(data_dir: str) -> FileDataProvider:
    """初始化数据提供者"""
    global _data_provider
    _data_provider = FileDataProvider(data_dir)
    return _data_provider


def get_data_provider() -> FileDataProvider:
    """获取数据提供者实例"""
    global _data_provider
    if _data_provider is None:
        # 默认使用项目 data 目录
        default_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        _data_provider = FileDataProvider(default_dir)
    return _data_provider
