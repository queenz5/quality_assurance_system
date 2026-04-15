"""
测试用例生成模块
根据结构化需求生成完整的测试用例

功能：
1. 从 Skill 文件加载 Prompt（不再硬编码）
2. 读取结构化需求文件
3. AI 生成多维度测试用例（正向/反向/边界值/场景/状态）
4. 生成结构化测试用例文件（YAML + 索引）
"""
import os
import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from modules.models import Priority, TestCaseStatus
from modules.utils import get_module_prefix
from config.llm_config import get_llm


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, output_dir: str = None, skill_dir: str = None):
        """
        初始化测试用例生成器
        
        Args:
            output_dir: 测试用例输出目录
            skill_dir: Skill 目录路径
        """
        if output_dir is None:
            # 默认输出目录
            self.output_dir = Path(__file__).parent.parent / "data" / "testcases"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置 Skill 目录
        if skill_dir is None:
            self.skill_dir = Path(__file__).parent.parent.parent / "skills" / "requirements-to-testcases"
        else:
            self.skill_dir = Path(skill_dir)
        
        # 加载 Prompt
        self._system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """从 SKILL.md 文件加载系统 Prompt"""
        skill_file = self.skill_dir / "SKILL.md"
        
        if not skill_file.exists():
            print(f"⚠️  警告: Skill 文件不存在: {skill_file}，使用默认 Prompt")
            return self._get_default_system_prompt()
        
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # 跳过 frontmatter
            if content.startswith('---'):
                second_dash = content.find('---', 3)
                if second_dash > 0:
                    content = content[second_dash + 3:].strip()
            
            # 提取关键部分
            sections = []
            current_section = ""
            
            for line in content.split('\n'):
                if line.startswith('# '):
                    current_section = "title"
                    sections.append(line)
                elif line.startswith('## 工作流') or line.startswith('## 测试用例格式') or \
                     line.startswith('## 字段说明') or line.startswith('## 测试用例设计策略') or \
                     line.startswith('## 用例设计原则') or line.startswith('## 输出要求'):
                    current_section = "content"
                    sections.append(line)
                elif line.startswith('## '):
                    if line.startswith('## 示例') or line.startswith('## 常见场景'):
                        break
                    current_section = "content"
                    sections.append(line)
                elif current_section in ["title", "content"]:
                    sections.append(line)
            
            prompt_content = '\n'.join(sections)
            
            if not prompt_content.strip():
                print("⚠️  警告: 无法从 SKILL.md 提取 Prompt，使用整个文件内容")
                return content
            
            print(f"✅ 从 SKILL.md 加载测试用例生成 Prompt 成功")
            return prompt_content
            
        except Exception as e:
            print(f"❌ 加载 SKILL.md 失败: {str(e)}，使用默认 Prompt")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """默认系统 Prompt（备用）"""
        return """你是一个资深测试架构师，拥有 10 年测试设计经验。

你的任务是根据结构化需求文档生成完整的测试用例。

需要覆盖的测试策略：
1. 正向测试：正常流程验证
2. 反向测试：异常流程和错误处理
3. 边界值测试：临界值验证
4. 等价类测试：输入域划分
5. 场景法测试：端到端业务流程
6. 状态流转测试：状态机验证（如适用）

输出必须是严格的 JSON 格式，包含 test_cases 数组。
每个测试用例包含：
- id: TC-XXX（三位数字，从 001 开始递增）
- title: 模块-场景描述
- description: 用例简要说明
- requirement_id: 关联需求ID
- module: 模块名称
- priority: 高/中/低
- case_type: 基本功能/异常情况/边界条件/性能测试/安全测试
- test_method: 正向测试/反向测试/边界值/场景法/状态流转
- preconditions: 前置条件列表
- steps: 测试步骤数组（每项包含 step_no, action, input, expected）
- expected_result: 整体预期结果
- test_data: 测试数据字典
- tags: 标签列表

注意事项：
- 用例 ID 格式：TC-XXX（三位数字）
- 覆盖所有功能点
- 每个功能点至少包含正向、反向、边界值用例
- 步骤清晰具体，5-10步/条
- 测试数据使用具体值"""
    
    def _get_next_testcase_id(self, module: str) -> str:
        """获取下一个可用的测试用例 ID（使用模块拼音首字母）"""
        # 获取模块前缀
        prefix = get_module_prefix(module)

        # 读取全局索引
        global_index_file = self.output_dir / "_global_index.json"
        max_id = 0

        if global_index_file.exists():
            try:
                with open(global_index_file, 'r', encoding='utf-8') as f:
                    global_index = json.load(f)
                module_info = global_index.get("modules", {}).get(module, {})
                max_id = module_info.get("last_tc_id", 0)
            except Exception as e:
                print(f"⚠️ 读取全局索引失败: {e}")

        # 如果索引中没有该模块信息，扫描文件
        if max_id == 0:
            max_id = self._scan_existing_testcase_files(module, prefix)

        # 返回下一个编号
        next_id = max_id + 1
        return f"TC-{prefix}-{next_id:03d}"

    def _scan_existing_testcase_files(self, module: str, prefix: str) -> int:
        """扫描现有测试用例文件，找出最大编号"""
        max_id = 0
        module_dir = self.output_dir / module

        if not module_dir.exists():
            return 0

        # 扫描所有 TC-{prefix}-*.yaml 文件（包括子目录）
        pattern = f"TC-{prefix}-*.yaml"
        for file_path in module_dir.rglob(pattern):
            file_name = file_path.name
            # 提取 TC-{prefix}-XXX 部分
            match = re.match(rf'TC-{re.escape(prefix)}-(\d+)_', file_name)
            if match:
                try:
                    tc_num = int(match.group(1))
                    max_id = max(max_id, tc_num)
                except:
                    pass

        if max_id > 0:
            print(f"📂 扫描到模块 {module} 现有用例文件，最大编号: TC-{prefix}-{max_id:03d}")

        return max_id
    
    def _renumber_test_cases(self, result: Dict[str, Any], module: str) -> Dict[str, Any]:
        """重新编号测试用例，避免与已有用例冲突"""
        test_cases = result.get("test_cases", [])
        if not test_cases:
            return result

        # 获取下一个可用的用例 ID
        next_tc_id = self._get_next_testcase_id(module)
        # 提取序号部分
        match = re.match(r'TC-.+?-(\d+)', next_tc_id)
        if match:
            tc_num = int(match.group(1))
        else:
            tc_num = 1

        # 重新编号每个测试用例
        for tc in test_cases:
            tc["id"] = f"TC-{get_module_prefix(module)}-{tc_num:03d}"
            tc_num += 1

        return result
    
    def generate_from_requirements(
        self,
        requirements: List[Dict[str, Any]],
        module: str,
        existing_tc_count: int = 0
    ) -> Dict[str, Any]:
        """
        根据需求列表生成测试用例
        
        Args:
            requirements: 需求数据列表
            module: 模块名称
            existing_tc_count: 已有用例数（用于编号）
        
        Returns:
            生成结果字典
        """
        # 构建 Prompt
        prompt = self._build_generation_prompt(requirements, module, existing_tc_count)
        
        # 调用 LLM
        try:
            llm = get_llm()
            from langchain_core.messages import SystemMessage, HumanMessage
            
            messages = [
                SystemMessage(content=self._system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = llm.invoke(messages)
            result_text = response.content
            
            # 解析 JSON 结果
            parsed_result = self._parse_json_response(result_text)
            
            # 打印调试信息
            if parsed_result.get("test_cases") and len(parsed_result["test_cases"]) > 0:
                first_tc = parsed_result["test_cases"][0]
                print(f"🔍 第一个用例的字段: module={first_tc.get('module')}, sub_module={first_tc.get('sub_module')}")

            # 重新编号，避免与已有用例冲突
            parsed_result = self._renumber_test_cases(parsed_result, module)

            return parsed_result
            
        except Exception as e:
            import traceback
            return {
                "test_cases": [],
                "generation_summary": f"生成失败: {str(e)}",
                "warnings": [f"LLM 调用失败: {str(e)}\n{traceback.format_exc()}"]
            }
    
    def _build_generation_prompt(
        self,
        requirements: List[Dict[str, Any]],
        module: str,
        existing_tc_count: int
    ) -> str:
        """构建生成 Prompt"""
        
        # 将需求转换为 JSON 字符串
        req_json = json.dumps(requirements, ensure_ascii=False, indent=2)
        
        return f"""请根据以下结构化需求生成测试用例。

【模块】
{module}

【需求列表】
{req_json}

【已有用例数】
{existing_tc_count}（新生成的用例 ID 应从 TC-{existing_tc_count + 1:03d} 开始）

【要求】
1. 为每个功能点设计正向、反向、边界值用例
2. 如果需求包含异常处理，为每个异常场景设计用例
3. 如果需求包含状态流转，设计状态流转用例
4. 步骤清晰具体，5-10步/条
5. 测试数据使用具体值

请严格按照系统提示词中定义的 JSON 格式输出。"""
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """解析 LLM 返回的 JSON"""
        
        # 清理可能的 markdown 代码块标记
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        try:
            data = json.loads(text.strip())
            return data
        except json.JSONDecodeError as e:
            return {
                "test_cases": [],
                "generation_summary": f"JSON 解析失败: {str(e)}",
                "warnings": [f"JSON 解析失败: {str(e)}"]
            }
    
    def save_test_cases(
        self,
        test_cases: List[Dict[str, Any]],
        module: str,
        submodule: str = None
    ) -> List[str]:
        """
        保存测试用例到文件

        Args:
            test_cases: 测试用例列表
            module: 模块名称
            submodule: 子模块名称（可选）

        Returns:
            保存的文件路径列表
        """
        saved_files = []

        # 确定保存目录
        if submodule:
            save_dir = self.output_dir / module / submodule
        else:
            save_dir = self.output_dir / module

        save_dir.mkdir(parents=True, exist_ok=True)

        for tc in test_cases:
            # 更新用例的模块和子模块信息
            tc["module"] = module
            if submodule:
                tc["submodule"] = submodule
            
            # 打印调试信息
            print(f"📝 保存用例: {tc.get('id')} - module={tc.get('module')}, sub_module={tc.get('sub_module')}, submodule={tc.get('submodule')}")

            # 生成文件名
            file_name = f"{tc['id']}_{tc['title']}.yaml"
            file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
            file_path = save_dir / file_name

            # 转换为 YAML 格式
            yaml_content = self._convert_to_yaml_format(tc)

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_content, f, allow_unicode=True, default_flow_style=False)

            saved_files.append(str(file_path))

        # 更新索引
        self._update_tc_index(test_cases, module, submodule)

        return saved_files
    
    def _convert_to_yaml_format(self, tc: Dict[str, Any]) -> Dict[str, Any]:
        """转换为 YAML 格式"""
        now = datetime.now().isoformat()

        yaml_data = {
            'id': tc.get('id', ''),
            'title': tc.get('title', ''),
            'description': tc.get('description', ''),
            'requirement_id': tc.get('requirement_id', ''),
            'module': tc.get('module', ''),
            'priority': tc.get('priority', '中'),
            'status': '未执行',
            'case_type': tc.get('case_type', '基本功能'),
            'preconditions': tc.get('preconditions', []),
            'steps': tc.get('steps', []),
            'expected_result': tc.get('expected_result', ''),
            'test_data': tc.get('test_data', {}),
            'tags': tc.get('tags', []),
            'execution_count': 0,
            'created_at': now,
            'updated_at': now
        }
        
        if tc.get('submodule'):
            yaml_data['sub_module'] = tc['submodule']
        elif tc.get('sub_module'):
            yaml_data['sub_module'] = tc['sub_module']

        return yaml_data
    
    def _update_tc_index(self, test_cases: List[Dict[str, Any]], module: str, submodule: str = None):
        """更新测试用例索引（全局索引 + 模块索引）"""
        prefix = get_module_prefix(module)

        # 1. 更新全局索引
        global_index_file = self.output_dir / "_global_index.json"
        if global_index_file.exists():
            try:
                with open(global_index_file, 'r', encoding='utf-8') as f:
                    global_index = json.load(f)
            except:
                global_index = {"modules": {}}
        else:
            global_index = {"modules": {}}

        # 初始化模块信息
        if module not in global_index["modules"]:
            global_index["modules"][module] = {"prefix": prefix, "last_tc_id": 0}

        # 2. 更新模块索引
        module_index_file = self.output_dir / module / "_index.json"
        if module_index_file.exists():
            try:
                with open(module_index_file, 'r', encoding='utf-8') as f:
                    module_index = json.load(f)
            except:
                module_index = {"module": module, "prefix": prefix, "last_tc_id": 0, "submodules": {}, "test_cases": []}
        else:
            module_index = {"module": module, "prefix": prefix, "last_tc_id": 0, "submodules": {}, "test_cases": []}

        # 确保字段存在
        if "submodules" not in module_index:
            module_index["submodules"] = {}

        # 处理每个用例
        now = datetime.now().isoformat()
        for tc in test_cases:
            tc_id = tc.get('id', '')
            tc_title = tc.get('title', '')
            tc_req_id = tc.get('requirement_id', '')
            tc_priority = tc.get('priority', '中')
            tc_case_type = tc.get('case_type', '基本功能')

            # 提取序号
            try:
                match = re.match(rf'TC-{re.escape(prefix)}-(\d+)', tc_id)
                if match:
                    tc_num = int(match.group(1))
                    if tc_num > global_index["modules"][module]["last_tc_id"]:
                        global_index["modules"][module]["last_tc_id"] = tc_num
                    if tc_num > module_index["last_tc_id"]:
                        module_index["last_tc_id"] = tc_num
            except:
                pass

            # 确定文件路径
            if submodule:
                file_path = f"{submodule}/{tc_id}_{tc_title}.yaml"
                # 更新子模块映射
                if submodule not in module_index["submodules"]:
                    module_index["submodules"][submodule] = []
                if tc_id not in module_index["submodules"][submodule]:
                    module_index["submodules"][submodule].append(tc_id)
            else:
                file_path = f"{tc_id}_{tc_title}.yaml"

            # 检查是否已存在
            existing_tc = next((t for t in module_index["test_cases"] if t.get("id") == tc_id), None)

            if existing_tc:
                existing_tc.update({
                    "file": file_path,
                    "requirement_id": tc_req_id,
                    "title": tc_title,
                    "status": "未执行",
                    "priority": tc_priority,
                    "case_type": tc_case_type,
                    "updated_at": now,
                })
                if submodule:
                    existing_tc["submodule"] = submodule
            else:
                tc_entry = {
                    "id": tc_id,
                    "file": file_path,
                    "requirement_id": tc_req_id,
                    "title": tc_title,
                    "status": "未执行",
                    "priority": tc_priority,
                    "case_type": tc_case_type,
                    "bugs_found": [],
                    "updated_at": now,
                }
                if submodule:
                    tc_entry["submodule"] = submodule
                module_index["test_cases"].append(tc_entry)

        # 写入索引文件
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(global_index_file, 'w', encoding='utf-8') as f:
            json.dump(global_index, f, ensure_ascii=False, indent=2)

        (self.output_dir / module).mkdir(parents=True, exist_ok=True)
        with open(module_index_file, 'w', encoding='utf-8') as f:
            json.dump(module_index, f, ensure_ascii=False, indent=2)

        print(f"✅ 用例索引已更新: {len(test_cases)} 个用例，模块: {module}, 最新 ID: TC-{prefix}-{global_index['modules'][module]['last_tc_id']:03d}")


# ============== 便捷函数 ==============

def generate_test_cases_from_requirements(
    requirements: List[Dict[str, Any]],
    module: str,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    根据需求生成测试用例
    
    Args:
        requirements: 需求数据列表
        module: 模块名称
        output_dir: 输出目录
    
    Returns:
        生成结果字典
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "testcases")
    
    generator = TestCaseGenerator(output_dir)
    result = generator.generate_from_requirements(requirements, module)
    
    # 保存用例
    if result.get('test_cases'):
        saved_files = generator.save_test_cases(result['test_cases'], module)
        print(f"✅ 成功生成 {len(result['test_cases'])} 条测试用例")
        print(f"📁 保存文件: {len(saved_files)} 个")
        for f in saved_files:
            print(f"   - {f}")
    
    return result
