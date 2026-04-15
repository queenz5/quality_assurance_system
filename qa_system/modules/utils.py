"""
工具函数模块
"""
from pypinyin import pinyin, Style


def get_module_prefix(module_name: str) -> str:
    """
    获取模块名称的拼音首字母（大写）

    Args:
        module_name: 模块名称，如 "基础组件"

    Returns:
        拼音首字母，如 "JCZJ"
    """
    if not module_name:
        return "QT"  # 其他

    # 中文转拼音首字母
    try:
        py = pinyin(module_name, style=Style.FIRST_LETTER)
        prefix = ''.join([p[0].upper() for p in py])
        # 过滤非字母
        prefix = ''.join([c for c in prefix if c.isalpha()])
        return prefix if prefix else "QT"
    except Exception:
        # 降级处理：使用模块名前 2 个大写字母
        return ''.join([c.upper() for c in module_name if c.isalpha()])[:2] or "QT"
