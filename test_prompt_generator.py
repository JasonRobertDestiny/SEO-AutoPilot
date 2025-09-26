#!/usr/bin/env python3
"""
测试prompt生成器API端点
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_prompt_generation():
    """测试基本prompt生成功能"""
    print("🧪 测试基本prompt生成功能...")
    
    url = f"{BASE_URL}/api/prompt/generate"
    data = {
        "url": "https://example.com",
        "optimization_type": "content_quality",
        "page_type": "homepage",
        "current_score": 75.0,
        "target_score": 90.0,
        "industry": "Technology",
        "primary_keywords": ["SEO优化", "网站分析"],
        "secondary_keywords": ["搜索引擎", "网站优化"],
        "custom_requirements": ["提高用户体验", "增加转化率"]
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ 基本prompt生成成功")
            print(f"生成的prompt长度: {len(result['prompt'])} 字符")
            print(f"Prompt预览: {result['prompt'][:200]}...")
            return True
        else:
            print(f"❌ 基本prompt生成失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_batch_generation():
    """测试批量prompt生成功能"""
    print("\n🧪 测试批量prompt生成功能...")
    
    url = f"{BASE_URL}/api/prompt/batch"
    data = {
        "url": "https://shop.example.com/products",
        "optimization_types": ["content_quality", "technical_seo", "performance"],
        "page_type": "product",
        "current_score": 65.0,
        "target_score": 85.0,
        "primary_keywords": ["电商SEO", "产品优化"],
        "secondary_keywords": ["在线购物", "产品页面"],
        "industry": "E-commerce"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            prompts = result.get('prompts', {})
            print(f"✅ 批量prompt生成成功，共生成 {len(prompts)} 个prompt")
            for opt_type, prompt in prompts.items():
                print(f"   - {opt_type}: {len(prompt)} 字符")
            return True
        else:
            print(f"❌ 批量prompt生成失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_templates():
    """测试模板获取功能"""
    print("\n🧪 测试模板获取功能...")
    
    url = f"{BASE_URL}/api/prompt/templates"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('success'):
            templates = result['templates']
            print(f"✅ 模板获取成功，共有 {len(templates)} 个模板")
            for template_type in templates.keys():
                print(f"  - {template_type}")
            return True
        else:
            print(f"❌ 模板获取失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_from_analysis():
    """测试基于分析结果生成prompt功能"""
    print("\n🧪 测试基于分析结果生成prompt功能...")
    
    # 模拟完整的分析结果
    mock_analysis = {
        "url": "https://example.com",
        "seo_score": 72,
        "seo_analysis": {
            "issues": {
                "technical": [
                    {"title": "标题长度不当", "description": "页面标题过短", "priority": "high"},
                    {"title": "缺少Meta描述", "description": "页面缺少Meta描述标签", "priority": "high"}
                ],
                "content": [
                    {"title": "关键词密度低", "description": "主要关键词密度不足", "priority": "medium"}
                ]
            }
        },
        "keywords": {
            "primary": ["SEO", "网站优化"],
            "secondary": ["搜索引擎", "网站分析"]
        },
        "performance": {
            "overall_score": 72,
            "load_time": 3.2
        }
    }
    
    url = f"{BASE_URL}/api/prompt/from-analysis"
    data = {
        "analysis_result": mock_analysis,
        "optimization_type": "technical_seo"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ 基于分析结果的prompt生成成功")
            print(f"生成的prompt长度: {len(result['prompt'])} 字符")
            print(f"Prompt预览: {result['prompt'][:200]}...")
            return True
        else:
            print(f"❌ 基于分析结果的prompt生成失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试SEO Prompt生成器...")
    print("=" * 50)
    
    tests = [
        test_prompt_generation,
        test_batch_generation,
        test_templates,
        test_from_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！Prompt生成器功能正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()