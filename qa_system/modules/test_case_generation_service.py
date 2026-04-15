"""
用例生成服务层模块
统一编排测试用例生成和管理流程

功能:
1. 根据输入文本或选择的需求生成测试用例
2. 草稿管理(创建、更新、删除、发布)
"""
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from modules.test_case_generator import TestCaseGenerator


class TestCaseGenerationService:
    """用例生成服务层"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

        self.data_dir = Path(data_dir)
        self.testcase_drafts_dir = self.data_dir / "testcase_drafts"
        self.testcase_drafts_dir.mkdir(parents=True, exist_ok=True)

        self.generator = TestCaseGenerator()

    def generate_test_cases(
        self,
        input_text: str = None,
        requirements: List[Dict] = None,
        module: str = "未分类",
        source_type: str = "text"
    ) -> Dict[str, Any]:
        """
        生成测试用例

        Args:
            input_text: 输入的文本内容
            requirements: 选择的需求列表
            module: 模块名称
            source_type: 来源类型（text 或 requirement）

        Returns:
            生成结果
        """
        try:
            sub_module = None
            if requirements and len(requirements) > 0:
                sub_module = requirements[0].get("sub_module")
            
            if source_type == "requirement" and requirements:
                result = self.generator.generate_from_requirements(requirements, module)
            elif source_type == "text" and input_text:
                requirements_from_text = self._parse_text_to_requirements(input_text, module)
                result = self.generator.generate_from_requirements(requirements_from_text, module)
            else:
                return {
                    "test_cases": [],
                    "generation_summary": "生成失败：缺少输入内容",
                    "warnings": ["请提供输入文本或选择需求"]
                }

            if sub_module:
                result["sub_module"] = sub_module

            return result

        except Exception as e:
            import traceback
            return {
                "test_cases": [],
                "generation_summary": f"生成失败: {str(e)}",
                "warnings": [f"生成失败: {str(e)}\n{traceback.format_exc()}"]
            }

    def create_draft(
        self,
        test_cases: List[Dict],
        module: str = "未分类",
        sub_module: str = None,
        source_type: str = "text",
        input_text: str = None,
        selected_requirements: List[Dict] = None,
        generation_summary: str = ""
    ) -> str:
        """
        创建用例草稿

        Args:
            test_cases: 生成的测试用例列表
            module: 模块名称
            sub_module: 子模块名称
            source_type: 来源类型
            input_text: 原始输入文本
            selected_requirements: 选择的需求列表
            generation_summary: 生成摘要

        Returns:
            草稿ID
        """
        draft_id = f"TC-DRAFT-{uuid.uuid4().hex[:8].upper()}"

        now = datetime.now().isoformat()
        for tc in test_cases:
            if "updated_at" not in tc:
                tc["updated_at"] = now

        draft_data = {
            "draft_id": draft_id,
            "module": module,
            "sub_module": sub_module,
            "source_type": source_type,
            "title": f"{module} - {len(test_cases)}条用例",
            "input_text": input_text or "",
            "selected_requirements": selected_requirements or [],
            "test_cases": test_cases,
            "total_test_cases": len(test_cases),
            "generation_summary": generation_summary,
            "status": "draft",
            "created_at": now,
            "updated_at": now
        }

        draft_file = self.testcase_drafts_dir / f"{draft_id}.yaml"
        with open(draft_file, 'w', encoding='utf-8') as f:
            yaml.dump(draft_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return draft_id

    def get_draft(self, draft_id: str) -> Optional[Dict]:
        """获取草稿详情"""
        draft_file = self.testcase_drafts_dir / f"{draft_id}.yaml"

        if not draft_file.exists():
            return None

        with open(draft_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def list_drafts(self, module: str = None) -> List[Dict]:
        """获取草稿列表"""
        drafts = []

        for draft_file in self.testcase_drafts_dir.glob("TC-DRAFT-*.yaml"):
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    draft_data = yaml.safe_load(f)

                if module and draft_data.get("module") != module:
                    continue

                drafts.append({
                    "draft_id": draft_data.get("draft_id"),
                    "module": draft_data.get("module"),
                    "sub_module": draft_data.get("sub_module"),
                    "source_type": draft_data.get("source_type"),
                    "title": draft_data.get("title"),
                    "status": draft_data.get("status"),
                    "total_test_cases": draft_data.get("total_test_cases", 0),
                    "created_at": draft_data.get("created_at"),
                    "updated_at": draft_data.get("updated_at")
                })
            except Exception as e:
                print(f"⚠️ 读取草稿文件失败 {draft_file}: {e}")

        drafts.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return drafts

    def update_draft(
        self,
        draft_id: str,
        test_cases: List[Dict] = None,
        module: str = None,
        sub_module: str = None
    ) -> bool:
        """更新草稿"""
        draft_data = self.get_draft(draft_id)

        if not draft_data:
            return False

        if test_cases is not None:
            draft_data["test_cases"] = test_cases
            draft_data["total_test_cases"] = len(test_cases)
            draft_data["title"] = f"{draft_data.get('module', '未分类')} - {len(test_cases)}条用例"

        if module is not None:
            draft_data["module"] = module

        if sub_module is not None:
            draft_data["sub_module"] = sub_module

        draft_data["updated_at"] = datetime.now().isoformat()

        draft_file = self.testcase_drafts_dir / f"{draft_id}.yaml"
        with open(draft_file, 'w', encoding='utf-8') as f:
            yaml.dump(draft_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return True

    def delete_draft(self, draft_id: str) -> bool:
        """删除草稿"""
        draft_file = self.testcase_drafts_dir / f"{draft_id}.yaml"

        if not draft_file.exists():
            return False

        try:
            draft_file.unlink()
            return True
        except Exception as e:
            print(f"❌ 删除草稿失败: {e}")
            return False

    def get_draft_test_cases(self, draft_id: str) -> Optional[List[Dict]]:
        """获取草稿的测试用例数据"""
        draft_data = self.get_draft(draft_id)

        if not draft_data:
            return None

        return draft_data.get("test_cases", [])

    def save_draft_test_cases(self, draft_id: str, test_cases: List[Dict]) -> bool:
        """保存草稿的测试用例数据"""
        return self.update_draft(draft_id, test_cases=test_cases)

    def publish_to_formal(
        self,
        draft_id: str,
        module: str = None,
        submodule: str = None
    ) -> Tuple[bool, List[str]]:
        """将草稿发布为正式用例"""
        draft_data = self.get_draft(draft_id)

        if not draft_data:
            return False, []

        test_cases = draft_data.get("test_cases", [])

        if not test_cases:
            return False, []

        target_module = module or draft_data.get("module", "未分类")
        target_submodule = submodule or draft_data.get("sub_module")

        try:
            saved_files = self.generator.save_test_cases(test_cases, target_module, target_submodule)

            if saved_files:
                draft_file = self.testcase_drafts_dir / f"{draft_id}.yaml"
                if draft_file.exists():
                    draft_file.unlink()
                    print(f"✅ 草稿 {draft_id} 已删除（已发布为正式用例）")

            return len(saved_files) > 0, saved_files

        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False, []

    def _parse_text_to_requirements(self, text: str, module: str) -> List[Dict]:
        """将输入文本转换为需求格式"""
        return [
            {
                "id": "REQ-TEXT-001",
                "title": "文本输入需求",
                "description": text,
                "module": module,
                "priority": "中",
                "function_points": [],
                "preconditions": [],
                "postconditions": [],
                "business_rules": [],
                "exception_handling": []
            }
        ]
