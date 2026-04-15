#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
需求拆解流程测试脚本
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from modules.requirement_parser import RequirementParser

# 测试目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "requirements")

def test_parse_simple_text():
    """测试简单文本解析"""
    
    # 示例需求文本
    test_text = """
# 用户管理系统需求

## 1. 用户登录功能

用户可以通过手机号+验证码或账号密码登录系统。

### 功能要求：
1. 支持手机号+短信验证码登录
   - 验证码6位数字，有效期5分钟
   - 同一手机号60秒内只能发送一次验证码
2. 支持账号密码登录
   - 密码长度8-20位，必须包含字母和数字
   - 连续5次密码错误锁定账号30分钟
3. 登录成功后返回用户信息和Token
   - Token有效期30天
   - 支持Token刷新

### 异常处理：
- 手机号格式错误：提示"请输入正确的手机号"
- 验证码错误：提示"验证码错误，请重新输入"
- 账号被锁定：提示"账号已被锁定，请30分钟后再试"

## 2. 用户注册功能

用户可以通过手机号注册新账号。

### 功能要求：
1. 手机号验证
   - 必须是大陆手机号（1开头，11位）
   - 不能是已注册的手机号
2. 密码设置
   - 长度8-20位
   - 必须包含字母和数字
3. 注册成功后自动登录

### 前置条件：
- 短信服务正常运行
- 用户未注册过账号

### 后置条件：
- 创建用户记录
- 发送欢迎消息
"""
    
    print("=" * 60)
    print("测试 1：从文本解析需求")
    print("=" * 60)
    
    parser = RequirementParser(OUTPUT_DIR)
    result = parser.parse_prd_text(test_text, "用户管理系统需求")
    
    print(f"\n✅ 解析完成！")
    print(f"📊 识别模块数: {result.total_modules}")
    print(f"📋 识别功能点数: {result.total_function_points}")
    print(f"📝 生成需求数: {len(result.parsed_requirements)}")
    print(f"\n📄 解析总结: {result.parse_summary}")
    
    if result.warnings:
        print(f"\n⚠️  警告:")
        for w in result.warnings:
            print(f"   - {w}")
    
    print(f"\n📦 生成的需求列表:")
    for req in result.parsed_requirements:
        print(f"   - {req.id}: {req.title} ({req.module})")
        print(f"     优先级: {req.priority.value}")
        print(f"     功能点: {len(req.function_points)} 个")
        for fp in req.function_points:
            print(f"       • {fp.id}: {fp.description}")
    
    # 保存文件
    if result.parsed_requirements:
        print(f"\n💾 保存文件...")
        saved_files = parser.save_structured_requirements(result)
        print(f"✅ 成功保存 {len(saved_files)} 个文件:")
        for f in saved_files:
            print(f"   - {f}")
    
    return result


def test_existing_prd_file():
    """测试从现有 PRD 文件解析"""
    
    # 检查是否有可用的 PRD 文件
    prd_file = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "skills", 
        "prd-to-xmind-testcases", 
        "requirements",
        "企业级B2C电商项目-测试用例.md"
    )
    
    if not os.path.exists(prd_file):
        print(f"\n⚠️  未找到 PRD 文件: {prd_file}")
        return None
    
    print("\n" + "=" * 60)
    print("测试 2：从文件解析需求")
    print("=" * 60)
    print(f"📂 文件: {prd_file}")
    
    try:
        parser = RequirementParser(OUTPUT_DIR)
        result = parser.parse_prd_file(prd_file)
        
        print(f"\n✅ 解析完成！")
        print(f"📊 识别模块数: {result.total_modules}")
        print(f"📋 识别功能点数: {result.total_function_points}")
        print(f"📝 生成需求数: {len(result.parsed_requirements)}")
        
        if result.warnings:
            print(f"\n⚠️  警告:")
            for w in result.warnings:
                print(f"   - {w}")
        
        # 保存文件
        if result.parsed_requirements:
            saved_files = parser.save_structured_requirements(result)
            print(f"\n✅ 成功保存 {len(saved_files)} 个文件")
        
        return result
    except Exception as e:
        print(f"\n❌ 解析失败: {str(e)}")
        return None


if __name__ == "__main__":
    print("\n🚀 开始测试需求拆解流程\n")
    
    # 测试 1：简单文本
    result1 = test_parse_simple_text()
    
    # 测试 2：从文件
    result2 = test_existing_prd_file()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n📁 输出目录:")
    print(f"   {OUTPUT_DIR}")
    print("\n📖 下一步:")
    print("   1. 查看生成的需求文件")
    print("   2. 人工审核和调整")
    print("   3. 进入阶段2：根据结构化需求生成测试用例")
