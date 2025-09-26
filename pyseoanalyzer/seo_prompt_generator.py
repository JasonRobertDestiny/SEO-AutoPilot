#!/usr/bin/env python3
"""
🚀 SEO内容优化Prompt规范生成器
为MGX AI提供标准化、精准的SEO优化提示词生成

Author: SEO AutoPilot Team
Version: 1.0.0
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import datetime


class OptimizationType(Enum):
    """SEO优化类型枚举"""
    TECHNICAL_SEO = "technical_seo"
    CONTENT_QUALITY = "content_quality"
    USER_EXPERIENCE = "user_experience"
    PERFORMANCE = "performance"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    STRATEGIC_PLANNING = "strategic_planning"


class PriorityLevel(Enum):
    """优先级级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContentType(Enum):
    """内容类型"""
    HOMEPAGE = "homepage"
    PRODUCT_PAGE = "product_page"
    BLOG_POST = "blog_post"
    CATEGORY_PAGE = "category_page"
    LANDING_PAGE = "landing_page"
    ABOUT_PAGE = "about_page"
    CONTACT_PAGE = "contact_page"


@dataclass
class SEOContext:
    """SEO优化上下文信息"""
    url: str
    domain: str
    page_type: ContentType
    current_score: float
    target_score: float
    industry: str
    competitors: List[str]
    primary_keywords: List[str]
    secondary_keywords: List[str]
    content_length: int
    issues_detected: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    user_intent: str  # informational, commercial, navigational, transactional


@dataclass
class PromptTemplate:
    """Prompt模板结构"""
    template_id: str
    optimization_type: OptimizationType
    priority: PriorityLevel
    title: str
    context_requirements: List[str]
    prompt_structure: Dict[str, str]
    expected_output_format: str
    success_metrics: List[str]
    examples: List[str]


class SEOPromptGenerator:
    """🧠 SEO内容优化Prompt生成器"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.context_analyzers = self._initialize_context_analyzers()
        
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """初始化prompt模板库"""
        templates = {}
        
        # 技术SEO优化模板
        templates["technical_seo_meta"] = PromptTemplate(
            template_id="technical_seo_meta",
            optimization_type=OptimizationType.TECHNICAL_SEO,
            priority=PriorityLevel.HIGH,
            title="Meta标签优化",
            context_requirements=["current_title", "current_description", "target_keywords", "page_content"],
            prompt_structure={
                "role": "你是一位专业的SEO技术专家，专门负责Meta标签优化",
                "context": "基于网站分析结果和目标关键词",
                "task": "优化页面的Title和Meta Description",
                "constraints": "Title长度50-60字符，Description长度150-160字符，包含主要关键词",
                "output_format": "提供优化后的Title和Description，并说明优化理由"
            },
            expected_output_format="JSON格式：{title: '', description: '', reasoning: ''}",
            success_metrics=["关键词密度", "字符长度", "点击率预期提升"],
            examples=["电商产品页面Meta优化", "博客文章Meta优化"]
        )
        
        # 内容质量优化模板
        templates["content_structure"] = PromptTemplate(
            template_id="content_structure",
            optimization_type=OptimizationType.CONTENT_QUALITY,
            priority=PriorityLevel.HIGH,
            title="内容结构优化",
            context_requirements=["current_content", "target_keywords", "user_intent", "content_length"],
            prompt_structure={
                "role": "你是一位资深的内容策略专家和SEO文案师",
                "context": "基于当前页面内容和用户搜索意图",
                "task": "重构内容层次结构，优化标题层级和段落组织",
                "constraints": "保持原有信息完整性，提升可读性和SEO友好度",
                "output_format": "提供优化后的内容大纲和具体改进建议"
            },
            expected_output_format="Markdown格式的内容结构 + 优化说明",
            success_metrics=["可读性评分", "关键词分布", "用户停留时间"],
            examples=["长篇博客文章结构优化", "产品详情页内容重组"]
        )
        
        # 关键词优化模板
        templates["keyword_optimization"] = PromptTemplate(
            template_id="keyword_optimization",
            optimization_type=OptimizationType.KEYWORD_OPTIMIZATION,
            priority=PriorityLevel.MEDIUM,
            title="关键词策略优化",
            context_requirements=["current_keywords", "competitor_keywords", "search_trends", "content_gaps"],
            prompt_structure={
                "role": "你是一位关键词研究专家和竞争分析师",
                "context": "基于竞争对手分析和搜索趋势数据",
                "task": "制定精准的关键词策略和内容优化方案",
                "constraints": "平衡搜索量、竞争度和相关性",
                "output_format": "提供关键词映射表和内容优化建议"
            },
            expected_output_format="关键词策略表格 + 实施计划",
            success_metrics=["关键词排名提升", "搜索流量增长", "转化率"],
            examples=["电商类目页关键词优化", "服务页面关键词布局"]
        )
        
        # 性能优化模板
        templates["performance_optimization"] = PromptTemplate(
            template_id="performance_optimization",
            optimization_type=OptimizationType.PERFORMANCE,
            priority=PriorityLevel.CRITICAL,
            title="页面性能优化",
            context_requirements=["core_web_vitals", "pagespeed_score", "performance_issues"],
            prompt_structure={
                "role": "你是一位Web性能优化专家和技术SEO顾问",
                "context": "基于Core Web Vitals和PageSpeed分析结果",
                "task": "制定全面的性能优化方案",
                "constraints": "优先解决影响SEO排名的关键性能指标",
                "output_format": "提供分阶段的性能优化实施计划"
            },
            expected_output_format="优化清单 + 预期性能提升数据",
            success_metrics=["LCP改善", "FID优化", "CLS减少", "整体评分提升"],
            examples=["移动端性能优化", "图片加载优化"]
        )
        
        # 用户体验优化模板
        templates["ux_optimization"] = PromptTemplate(
            template_id="ux_optimization",
            optimization_type=OptimizationType.USER_EXPERIENCE,
            priority=PriorityLevel.MEDIUM,
            title="用户体验优化",
            context_requirements=["user_behavior_data", "navigation_structure", "mobile_usability"],
            prompt_structure={
                "role": "你是一位UX设计师和用户体验优化专家",
                "context": "基于用户行为数据和可用性分析",
                "task": "优化页面用户体验和交互设计",
                "constraints": "提升用户满意度的同时保持SEO友好性",
                "output_format": "提供UX优化建议和实施指南"
            },
            expected_output_format="UX改进方案 + 用户旅程优化",
            success_metrics=["跳出率降低", "页面停留时间", "转化率提升"],
            examples=["移动端导航优化", "表单用户体验改善"]
        )
        
        # 竞争分析模板
        templates["competitive_analysis"] = PromptTemplate(
            template_id="competitive_analysis",
            optimization_type=OptimizationType.COMPETITIVE_ANALYSIS,
            priority=PriorityLevel.MEDIUM,
            title="竞争对手分析优化",
            context_requirements=["competitor_data", "market_position", "content_gaps", "backlink_analysis"],
            prompt_structure={
                "role": "你是一位市场竞争分析专家和SEO策略师",
                "context": "基于竞争对手SEO表现和市场定位分析",
                "task": "制定差异化的SEO竞争策略",
                "constraints": "发挥自身优势，弥补竞争劣势",
                "output_format": "提供竞争策略和实施路线图"
            },
            expected_output_format="竞争分析报告 + 策略建议",
            success_metrics=["市场份额提升", "关键词排名超越", "品牌知名度"],
            examples=["行业领导者分析", "细分市场竞争策略"]
        )
        
        # 战略规划模板
        templates["strategic_planning"] = PromptTemplate(
            template_id="strategic_planning",
            optimization_type=OptimizationType.STRATEGIC_PLANNING,
            priority=PriorityLevel.HIGH,
            title="SEO战略规划",
            context_requirements=["business_goals", "current_performance", "resource_constraints", "timeline"],
            prompt_structure={
                "role": "你是一位SEO战略顾问和数字营销专家",
                "context": "基于业务目标和当前SEO表现",
                "task": "制定长期SEO发展战略和实施计划",
                "constraints": "考虑资源限制和时间安排",
                "output_format": "提供战略规划文档和里程碑计划"
            },
            expected_output_format="战略规划书 + 执行时间表",
            success_metrics=["流量增长目标", "排名提升计划", "ROI预期"],
            examples=["年度SEO规划", "产品上线SEO策略"]
        )
        
        return templates
    
    def _initialize_context_analyzers(self) -> Dict[str, callable]:
        """初始化上下文分析器"""
        return {
            "content_analyzer": self._analyze_content_context,
            "technical_analyzer": self._analyze_technical_context,
            "competitive_analyzer": self._analyze_competitive_context,
            "performance_analyzer": self._analyze_performance_context
        }
    
    def generate_optimization_prompt(
        self, 
        seo_context: SEOContext, 
        optimization_type: OptimizationType,
        custom_requirements: Optional[List[str]] = None
    ) -> str:
        """
        🎯 生成针对性的SEO优化prompt
        
        Args:
            seo_context: SEO上下文信息
            optimization_type: 优化类型
            custom_requirements: 自定义需求
            
        Returns:
            格式化的prompt字符串
        """
        # 选择合适的模板
        template = self._select_template(optimization_type, seo_context)
        
        # 分析上下文
        context_analysis = self._analyze_context(seo_context, template)
        
        # 生成prompt
        prompt = self._build_prompt(template, seo_context, context_analysis, custom_requirements)
        
        return prompt
    
    def _select_template(self, optimization_type: OptimizationType, context: SEOContext) -> PromptTemplate:
        """选择最适合的模板"""
        # 基于优化类型选择主模板
        template_mapping = {
            OptimizationType.TECHNICAL_SEO: "technical_seo_meta",
            OptimizationType.CONTENT_QUALITY: "content_structure",
            OptimizationType.KEYWORD_OPTIMIZATION: "keyword_optimization",
            OptimizationType.PERFORMANCE: "performance_optimization",
            OptimizationType.USER_EXPERIENCE: "ux_optimization",
            OptimizationType.COMPETITIVE_ANALYSIS: "competitive_analysis",
            OptimizationType.STRATEGIC_PLANNING: "strategic_planning"
        }
        
        template_id = template_mapping.get(optimization_type, "content_structure")
        return self.templates[template_id]
    
    def _analyze_context(self, seo_context: SEOContext, template: PromptTemplate) -> Dict[str, Any]:
        """分析SEO上下文"""
        analysis = {
            "priority_issues": self._identify_priority_issues(seo_context),
            "optimization_opportunities": self._identify_opportunities(seo_context),
            "resource_requirements": self._estimate_resources(seo_context, template),
            "expected_impact": self._estimate_impact(seo_context, template)
        }
        return analysis
    
    def _build_prompt(
        self, 
        template: PromptTemplate, 
        context: SEOContext, 
        analysis: Dict[str, Any],
        custom_requirements: Optional[List[str]] = None
    ) -> str:
        """构建最终的prompt"""
        
        prompt_sections = []
        
        # 1. 角色定义
        prompt_sections.append(f"## 🎯 角色定义\n{template.prompt_structure['role']}")
        
        # 2. 任务背景
        background = f"""
## 📊 任务背景
- **网站URL**: {context.url}
- **页面类型**: {context.page_type.value}
- **当前SEO评分**: {context.current_score:.1f}/100
- **目标评分**: {context.target_score:.1f}/100
- **行业领域**: {context.industry}
- **主要关键词**: {', '.join(context.primary_keywords)}
- **用户搜索意图**: {context.user_intent}
"""
        prompt_sections.append(background)
        
        # 3. 具体任务
        task_section = f"""
## 🎯 具体任务
{template.prompt_structure['task']}

### 优先处理的问题：
"""
        for issue in analysis["priority_issues"][:3]:  # 显示前3个优先问题
            task_section += f"- {issue}\n"
        
        prompt_sections.append(task_section)
        
        # 4. 约束条件
        constraints = f"""
## ⚠️ 约束条件
{template.prompt_structure['constraints']}

### 技术约束：
- 内容长度：{context.content_length} 字符
- 性能要求：Core Web Vitals优化
- 移动端友好：响应式设计必须
"""
        prompt_sections.append(constraints)
        
        # 5. 输出要求
        output_requirements = f"""
## 📋 输出要求
{template.prompt_structure['output_format']}

### 期望格式：
{template.expected_output_format}

### 成功指标：
"""
        for metric in template.success_metrics:
            output_requirements += f"- {metric}\n"
        
        prompt_sections.append(output_requirements)
        
        # 6. 自定义需求
        if custom_requirements:
            custom_section = "## 🔧 自定义需求\n"
            for req in custom_requirements:
                custom_section += f"- {req}\n"
            prompt_sections.append(custom_section)
        
        # 7. 示例参考
        if template.examples:
            examples_section = "## 💡 参考示例\n"
            for example in template.examples:
                examples_section += f"- {example}\n"
            prompt_sections.append(examples_section)
        
        return "\n\n".join(prompt_sections)
    
    def _identify_priority_issues(self, context: SEOContext) -> List[str]:
        """识别优先问题"""
        issues = []
        for issue in context.issues_detected:
            if issue.get('priority') in ['critical', 'high']:
                issues.append(f"{issue.get('title', '')}: {issue.get('description', '')}")
        return issues[:5]  # 返回前5个优先问题
    
    def _identify_opportunities(self, context: SEOContext) -> List[str]:
        """识别优化机会"""
        opportunities = []
        
        # 基于评分差距识别机会
        score_gap = context.target_score - context.current_score
        if score_gap > 20:
            opportunities.append("大幅度SEO提升机会")
        elif score_gap > 10:
            opportunities.append("中等程度优化空间")
        
        # 基于关键词识别机会
        if len(context.primary_keywords) < 3:
            opportunities.append("关键词策略扩展机会")
        
        return opportunities
    
    def _estimate_resources(self, context: SEOContext, template: PromptTemplate) -> Dict[str, str]:
        """估算资源需求"""
        return {
            "时间投入": "2-4小时" if template.priority == PriorityLevel.HIGH else "1-2小时",
            "技术难度": "中等" if template.optimization_type == OptimizationType.TECHNICAL_SEO else "简单",
            "预期周期": "1-2周"
        }
    
    def _estimate_impact(self, context: SEOContext, template: PromptTemplate) -> Dict[str, float]:
        """估算优化影响"""
        base_impact = {
            OptimizationType.TECHNICAL_SEO: 15.0,
            OptimizationType.CONTENT_QUALITY: 12.0,
            OptimizationType.PERFORMANCE: 18.0,
            OptimizationType.KEYWORD_OPTIMIZATION: 10.0,
            OptimizationType.USER_EXPERIENCE: 8.0,
            OptimizationType.COMPETITIVE_ANALYSIS: 6.0,
            OptimizationType.STRATEGIC_PLANNING: 20.0
        }
        
        impact = base_impact.get(template.optimization_type, 10.0)
        
        return {
            "SEO评分提升": impact,
            "流量增长预期": impact * 0.8,
            "排名提升预期": impact * 0.6
        }
    
    def _analyze_content_context(self, context: SEOContext) -> Dict[str, Any]:
        """分析内容上下文"""
        return {
            "content_quality": "good" if context.content_length > 500 else "needs_improvement",
            "keyword_density": "optimal" if context.primary_keywords else "low"
        }
    
    def _analyze_technical_context(self, context: SEOContext) -> Dict[str, Any]:
        """分析技术上下文"""
        return {
            "technical_health": "good" if context.current_score > 70 else "needs_work"
        }
    
    def _analyze_competitive_context(self, context: SEOContext) -> Dict[str, Any]:
        """分析竞争上下文"""
        return {
            "competitive_position": "strong" if len(context.competitors) < 3 else "challenging"
        }
    
    def _analyze_performance_context(self, context: SEOContext) -> Dict[str, Any]:
        """分析性能上下文"""
        return {
            "performance_status": "good" if context.performance_metrics.get('overall_score', 0) > 80 else "needs_optimization"
        }
    
    def generate_batch_prompts(
        self, 
        seo_context: SEOContext, 
        optimization_types: List[OptimizationType]
    ) -> Dict[str, str]:
        """批量生成多种类型的优化prompt"""
        prompts = {}
        for opt_type in optimization_types:
            prompts[opt_type.value] = self.generate_optimization_prompt(seo_context, opt_type)
        return prompts
    
    def export_prompt_library(self, filepath: str) -> None:
        """导出prompt模板库"""
        library = {
            "templates": {k: asdict(v) for k, v in self.templates.items()},
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.datetime.now().isoformat(),
                "total_templates": len(self.templates)
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(library, f, ensure_ascii=False, indent=2)


# 使用示例
if __name__ == "__main__":
    # 创建prompt生成器
    generator = SEOPromptGenerator()
    
    # 示例SEO上下文
    context = SEOContext(
        url="https://mgx.dev/",
        domain="mgx.dev",
        page_type=ContentType.HOMEPAGE,
        current_score=83.2,
        target_score=95.0,
        industry="AI/Technology",
        competitors=["openai.com", "anthropic.com"],
        primary_keywords=["AI platform", "multi-agent AI", "MetaGPT"],
        secondary_keywords=["automation", "natural language", "software development"],
        content_length=1200,
        issues_detected=[
            {"title": "Meta描述缺失", "description": "页面缺少Meta描述标签", "priority": "high"},
            {"title": "图片Alt属性", "description": "部分图片缺少Alt属性", "priority": "medium"}
        ],
        performance_metrics={"overall_score": 95.0, "mobile_score": 95, "desktop_score": 95},
        user_intent="commercial"
    )
    
    # 生成技术SEO优化prompt
    technical_prompt = generator.generate_optimization_prompt(
        context, 
        OptimizationType.TECHNICAL_SEO
    )
    
    print("🚀 生成的SEO技术优化Prompt:")
    print("=" * 50)
    print(technical_prompt)
    
    # 批量生成多种优化prompt
    batch_prompts = generator.generate_batch_prompts(
        context,
        [OptimizationType.CONTENT_QUALITY, OptimizationType.PERFORMANCE, OptimizationType.KEYWORD_OPTIMIZATION]
    )
    
    print(f"\n📦 批量生成了 {len(batch_prompts)} 个优化prompt")