"""
索引管理模块
自动更新需求、测试用例、BUG的索引文件

功能：
1. 当数据有变动时，自动更新对应模块的索引
2. 支持单个模块更新或全局更新
3. 保持索引与实际文件同步
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class IndexManager:
    """索引管理器"""
    
    def __init__(self, data_dir: str):
        """
        初始化索引管理器
        
        Args:
            data_dir: 数据根目录（qa_system/data/）
        """
        self.data_dir = Path(data_dir)
    
    # ==================== 需求索引管理 ====================
    
    def update_requirements_index(self, module: str = None):
        """
        更新需求索引
        
        Args:
            module: 模块名称（可选，如果不指定则更新所有模块）
        """
        req_dir = self.data_dir / "requirements"
        if not req_dir.exists():
            return
        
        index_file = req_dir / "_index.json"
        
        # 加载现有索引
        existing_index = {"requirements": [], "modules": [], "last_updated": ""}
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            except:
                pass
        
        # 确定要更新的模块
        modules_to_update = []
        if module:
            modules_to_update = [module]
        else:
            # 获取所有模块
            for module_dir in req_dir.iterdir():
                if module_dir.is_dir():
                    modules_to_update.append(module_dir.name)
        
        # 重新扫描需求文件
        all_requirements = []
        modules_set = set(existing_index.get("modules", []))
        
        for mod in modules_to_update:
            module_dir = req_dir / mod
            if not module_dir.exists():
                continue
            
            # 移除该模块的旧索引
            all_requirements = [
                req for req in all_requirements 
                if req.get("module") != mod
            ]
            all_requirements = [
                req for req in existing_index.get("requirements", [])
                if req.get("module") != mod
            ]
            
            # 扫描新需求
            for req_file in module_dir.glob("REQ-*.md"):
                req_info = self._parse_requirement_filename(req_file, mod)
                if req_info:
                    all_requirements.append(req_info)
            
            modules_set.add(mod)
        
        # 合并旧索引（未更新的模块保持不变）
        if not module:
            # 全局更新：重新扫描所有模块
            all_requirements = []
            modules_set = set()
            for module_dir in req_dir.iterdir():
                if module_dir.is_dir():
                    modules_set.add(module_dir.name)
                    for req_file in module_dir.glob("REQ-*.md"):
                        req_info = self._parse_requirement_filename(req_file, module_dir.name)
                        if req_info:
                            all_requirements.append(req_info)
        else:
            # 单模块更新：保留其他模块的索引
            existing_reqs = existing_index.get("requirements", [])
            other_module_reqs = [
                req for req in existing_reqs
                if req.get("module") != module
            ]
            all_requirements = other_module_reqs + all_requirements
        
        # 更新索引
        existing_index["requirements"] = all_requirements
        existing_index["modules"] = sorted(list(modules_set))
        existing_index["last_updated"] = datetime.now().isoformat()
        
        # 写入文件
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(existing_index, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 需求索引已更新: {module or '所有模块'} ({len(all_requirements)} 个需求)")
    
    def _parse_requirement_filename(self, file_path: Path, module: str) -> Optional[Dict]:
        """解析需求文件名，提取索引信息"""
        # 文件名格式：REQ-XXX_标题.md
        stem = file_path.stem
        parts = stem.split("_", 1)
        
        if len(parts) < 2:
            return None
        
        req_id = parts[0]
        title = parts[1]
        
        return {
            "id": req_id,
            "file": file_path.name,
            "module": module,
            "title": title,
            "priority": "中",  # 默认值，实际应从文件内容读取
            "status": "待开发",
            "function_points_count": 0,  # 默认值
            "tags": []
        }
    
    # ==================== 测试用例索引管理 ====================
    
    def update_testcases_index(self, module: str = None):
        """
        更新测试用例索引
        
        Args:
            module: 模块名称（可选，如果不指定则更新所有模块）
        """
        tc_dir = self.data_dir / "testcases"
        if not tc_dir.exists():
            return
        
        # 确定要更新的模块
        modules_to_update = []
        if module:
            modules_to_update = [module]
        else:
            # 获取所有模块
            for module_dir in tc_dir.iterdir():
                if module_dir.is_dir() and (module_dir / "testcase_index.json").exists():
                    modules_to_update.append(module_dir.name)
        
        for mod in modules_to_update:
            self._update_single_module_tc_index(mod)
    
    def _update_single_module_tc_index(self, module: str):
        """更新单个模块的测试用例索引"""
        module_dir = self.data_dir / "testcases" / module
        if not module_dir.exists():
            return
        
        index_file = module_dir / "testcase_index.json"
        
        # 加载现有索引
        existing_index = {"module": module, "test_cases": []}
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            except:
                pass
        
        # 重新扫描用例文件
        all_test_cases = []
        for tc_file in module_dir.glob("TC-*.yaml"):
            tc_info = self._parse_testcase_filename(tc_file)
            if tc_info:
                all_test_cases.append(tc_info)
        
        # 更新索引
        existing_index["test_cases"] = all_test_cases
        
        # 写入文件
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(existing_index, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ {module} 模块测试用例索引已更新 ({len(all_test_cases)} 条用例)")
    
    def _parse_testcase_filename(self, file_path: Path) -> Optional[Dict]:
        """解析测试用例文件名，提取索引信息"""
        # 文件名格式：TC-XXX_标题.yaml
        stem = file_path.stem
        parts = stem.split("_", 1)
        
        if len(parts) < 2:
            return None
        
        tc_id = parts[0]
        title = parts[1]
        
        return {
            "id": tc_id,
            "file": file_path.name,
            "requirement_id": "",  # 需要从文件内容读取
            "title": title,
            "status": "未执行",
            "priority": "中",
            "case_type": "基本功能",
            "bugs_found": []
        }
    
    # ==================== BUG索引管理 ====================
    
    def update_bugs_index(self, module: str = None):
        """
        更新BUG索引
        
        Args:
            module: 模块名称（可选，如果不指定则更新所有模块）
        """
        bug_dir = self.data_dir / "bugs"
        if not bug_dir.exists():
            return
        
        # 确定要更新的模块
        modules_to_update = []
        if module:
            modules_to_update = [module]
        else:
            # 获取所有模块
            for module_dir in bug_dir.iterdir():
                if module_dir.is_dir() and (module_dir / "bug_index.json").exists():
                    modules_to_update.append(module_dir.name)
        
        for mod in modules_to_update:
            self._update_single_module_bug_index(mod)
    
    def _update_single_module_bug_index(self, module: str):
        """更新单个模块的BUG索引"""
        module_dir = self.data_dir / "bugs" / module
        if not module_dir.exists():
            return
        
        index_file = module_dir / "bug_index.json"
        
        # 加载现有索引
        existing_index = {"module": module, "bugs": []}
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            except:
                pass
        
        # 重新扫描BUG文件
        all_bugs = []
        for bug_file in module_dir.glob("BUG-*.yaml"):
            bug_info = self._parse_bug_filename(bug_file)
            if bug_info:
                all_bugs.append(bug_info)
        
        # 更新索引
        existing_index["bugs"] = all_bugs
        
        # 写入文件
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(existing_index, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ {module} 模块BUG索引已更新 ({len(all_bugs)} 个BUG)")
    
    def _parse_bug_filename(self, file_path: Path) -> Optional[Dict]:
        """解析BUG文件名，提取索引信息"""
        # 文件名格式：BUG-XXX_标题.yaml
        stem = file_path.stem
        parts = stem.split("_", 1)
        
        if len(parts) < 2:
            return None
        
        bug_id = parts[0]
        title = parts[1]
        
        return {
            "id": bug_id,
            "file": file_path.name,
            "title": title,
            "severity": "一般",
            "status": "未修复",
            "test_case_id": "",
            "requirement_id": ""
        }
    
    # ==================== 全局索引更新 ====================
    
    def update_all_indexes(self):
        """更新所有索引（需求、测试用例、BUG）"""
        print("🔄 开始更新所有索引...")
        
        self.update_requirements_index()
        self.update_testcases_index()
        self.update_bugs_index()
        
        print("✅ 所有索引更新完成")


# ==================== 便捷函数 ====================

def get_index_manager(data_dir: str = None):
    """获取索引管理器实例"""
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    return IndexManager(data_dir)


def update_requirements_index(module: str = None, data_dir: str = None):
    """更新需求索引"""
    manager = get_index_manager(data_dir)
    manager.update_requirements_index(module)


def update_testcases_index(module: str = None, data_dir: str = None):
    """更新测试用例索引"""
    manager = get_index_manager(data_dir)
    manager.update_testcases_index(module)


def update_bugs_index(module: str = None, data_dir: str = None):
    """更新BUG索引"""
    manager = get_index_manager(data_dir)
    manager.update_bugs_index(module)
