from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

import asyncio
import json
import os
import logging
from .siliconflow_llm import SiliconFlowLLM

load_dotenv()
logger = logging.getLogger(__name__)


# Pydantic models for structured output
class EntityAnalysis(BaseModel):
    entity_assessment: str = Field(
        description="Detailed analysis of entity optimization"
    )
    knowledge_panel_readiness: int = Field(description="Score from 0-100")
    key_improvements: List[str] = Field(description="Top 3 improvements needed")


class CredibilityAnalysis(BaseModel):
    credibility_assessment: str = Field(description="Overall credibility analysis")
    neeat_scores: Dict[str, int] = Field(
        description="Individual N-E-E-A-T-T component scores"
    )
    trust_signals: List[str] = Field(description="Identified trust signals")


class ConversationAnalysis(BaseModel):
    conversation_readiness: str = Field(description="Overall assessment")
    query_patterns: List[str] = Field(description="Identified query patterns")
    engagement_score: int = Field(description="Score from 0-100")
    gaps: List[str] = Field(description="Identified conversational gaps")


class PlatformPresence(BaseModel):
    platform_coverage: Dict[str, str] = Field(
        description="Coverage analysis per platform"
    )
    visibility_scores: Dict[str, int] = Field(description="Scores per platform type")
    optimization_opportunities: List[str] = Field(description="List of opportunities")


class EnhancedProfessionalSEOAnalysis(BaseModel):
    """🎯 Enhanced Professional SEO Analysis with Diagnostic Integration
    
    This model combines AI intelligence with professional diagnostic data
    to provide analysis comparable to industry-leading SEO tools.
    """
    strategic_assessment: str = Field(description="High-level strategic analysis combining diagnostic insights")
    diagnostic_synthesis: Dict[str, str] = Field(description="Synthesis of 150+ diagnostic checkpoints")
    professional_priorities: List[str] = Field(description="Professional-grade optimization priorities ranked by impact")
    competitive_intelligence: str = Field(description="Competitive positioning analysis with actionable insights")
    technical_audit_summary: str = Field(description="Technical SEO audit summary with specific fixes")
    content_optimization_roadmap: Dict[str, List[str]] = Field(description="Detailed content optimization plan")
    implementation_timeline: Dict[str, Dict[str, str]] = Field(description="Phased implementation timeline with expected outcomes")
    roi_projections: Dict[str, float] = Field(description="Expected ROI for each optimization category")
    risk_mitigation_plan: List[str] = Field(description="Risk factors and mitigation strategies")
    professional_score_analysis: str = Field(description="Deep analysis of professional diagnostic scores")
    industry_benchmarking: Dict[str, str] = Field(description="Industry benchmark comparison and positioning")
    advanced_recommendations: List[Dict[str, str]] = Field(description="Advanced recommendations with implementation details")


class DiagnosticDataProcessor(BaseModel):
    """🔬 Diagnostic Data Processing Engine for AI Integration"""
    category_analysis: Dict[str, Dict[str, Any]] = Field(description="Processed category analysis data")
    critical_issues_synthesis: List[Dict[str, Any]] = Field(description="Synthesized critical issues with context")
    performance_correlation: Dict[str, float] = Field(description="Performance correlation analysis")
    optimization_impact_matrix: Dict[str, Dict[str, float]] = Field(description="Impact matrix for optimizations")
    diagnostic_insights: List[str] = Field(description="Key insights from diagnostic analysis")


class ProfessionalSEOAnalysis(BaseModel):
    """Enhanced SEO analysis using professional diagnostic data"""
    strategic_assessment: str = Field(description="High-level strategic analysis")
    technical_priorities: List[str] = Field(description="Top 5 technical optimization priorities")
    content_recommendations: List[str] = Field(description="Content optimization recommendations")
    competitive_insights: str = Field(description="Competitive positioning analysis")
    implementation_roadmap: Dict[str, str] = Field(description="Phased implementation recommendations")
    roi_estimation: str = Field(description="Expected ROI and impact analysis")
    risk_assessment: str = Field(description="Risk factors and mitigation strategies")


class TrendsAnalysis(BaseModel):
    """Trends-based strategic analysis for SEO optimization"""
    trending_opportunities: List[str] = Field(description="Top trending keyword opportunities")
    seasonal_strategy: str = Field(description="Seasonal content strategy recommendations")
    search_intent_alignment: str = Field(description="Analysis of search intent coverage")
    content_gap_analysis: List[str] = Field(description="Identified content gaps based on trends")
    competitive_keyword_strategy: str = Field(description="Competitive keyword positioning strategy")
    trend_momentum_score: int = Field(description="Overall trend momentum score 0-100")
    rising_topic_recommendations: List[str] = Field(description="Recommendations for rising topics")


class PerformanceAnalysis(BaseModel):
    """Performance-focused SEO analysis using PageSpeed data"""
    core_web_vitals_strategy: str = Field(description="Core Web Vitals optimization strategy")
    performance_impact_assessment: str = Field(description="SEO impact of current performance")
    mobile_first_recommendations: List[str] = Field(description="Mobile-first optimization priorities")
    user_experience_insights: str = Field(description="UX impact on SEO performance")
    technical_performance_priorities: List[str] = Field(description="Technical performance optimization priorities")
    page_speed_seo_score: int = Field(description="Performance impact on SEO score 0-100")
    lighthouse_optimization_roadmap: Dict[str, str] = Field(description="Lighthouse-based optimization roadmap")


class SEORecommendations(BaseModel):
    strategic_recommendations: List[str] = Field(
        description="Major strategic recommendations"
    )
    quick_wins: List[str] = Field(description="Immediate action items")
    long_term_strategy: List[str] = Field(description="Long-term strategic goals")
    priority_matrix: Dict[str, str] = Field(
        description="Priority matrix by impact/effort"
    )


class LLMSEOEnhancer:
    """
    Enhanced SEO analysis using Silicon Flow LLM.
    
    This class provides AI-powered SEO insights focusing on:
    1. Entity optimization
    2. N-E-E-A-T-T credibility signals  
    3. Conversational search readiness
    4. Cross-platform presence optimization
    5. Professional diagnostic integration
    """

    def __init__(self, siliconflow_api_key: str = None, siliconflow_model: str = None):
        """
        Initialize LLM SEO Enhancer with Silicon Flow provider.
        
        Args:
            siliconflow_api_key: Silicon Flow API key (defaults to SILICONFLOW_API_KEY env var)
            siliconflow_model: Silicon Flow model to use (defaults to SILICONFLOW_MODEL env var or Qwen/Qwen2.5-VL-72B-Instruct)
        """
        # Get model from parameter, env var, or default
        model = siliconflow_model or os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
        self.siliconflow_llm = SiliconFlowLLM(siliconflow_api_key, model)
        
        logger.info(f"🚀 LLM SEO Enhancer initialized with Silicon Flow model: {model}")

    async def enhance_seo_analysis(self, seo_data: Dict) -> Dict:
        """
        Enhanced SEO analysis using Silicon Flow API with timing and progress tracking
        """
        import time
        start_time = time.time()
        logger.info("🚀 Starting LLM SEO analysis with SiliconFlow...")
        
        try:
            # Use Silicon Flow API for comprehensive analysis
            logger.info("📡 Using SiliconFlow API for comprehensive analysis")
            analysis_start = time.time()
            result = await self.siliconflow_llm.analyze_seo_data(seo_data, "comprehensive")
            analysis_time = time.time() - analysis_start
            logger.info(f"✅ SiliconFlow analysis completed in {analysis_time:.2f}s")
            
            # Add timing metadata
            result["llm_analysis_metadata"] = {
                "total_execution_time": analysis_time,
                "provider": "siliconflow",
                "status": "completed"
            }
            
            return result
                
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"💥 Critical error in LLM analysis after {total_time:.2f}s: {e}")
            # Return original data with error information
            return {
                **seo_data,
                "llm_analysis": {
                    "status": "error",
                    "error_message": str(e),
                    "execution_time": total_time,
                    "recommendations": ["Unable to complete LLM analysis - check SiliconFlow API key and network connectivity"]
                }
            }

    def _format_output(self, raw_analysis: Dict) -> Dict:
        """Format analysis results into a clean, structured output"""
        # Provide fallback values for expected structure
        entity_analysis = raw_analysis.get("entity_analysis", {})
        credibility_analysis = raw_analysis.get("credibility_analysis", {})
        conversation_analysis = raw_analysis.get("conversation_analysis", {})
        platform_analysis = raw_analysis.get("cross_platform_presence", {})
        recommendations = raw_analysis.get("recommendations", {})
        
        return {
            "summary": {
                "entity_score": entity_analysis.get("knowledge_panel_readiness", 0),
                "credibility_score": sum(credibility_analysis.get("neeat_scores", {}).values()) / max(len(credibility_analysis.get("neeat_scores", {})), 1),
                "conversation_score": conversation_analysis.get("engagement_score", 0),
                "platform_score": sum(platform_analysis.get("visibility_scores", {}).values()) / max(len(platform_analysis.get("visibility_scores", {})), 1),
            },
            "detailed_analysis": raw_analysis,
            "quick_wins": recommendations.get("quick_wins", []),
            "strategic_recommendations": recommendations.get("strategic_recommendations", []),
        }

    async def enhanced_professional_analysis(self, enhanced_context: Dict) -> Dict:
        """
        🎯 Enhanced LLM analysis using professional diagnostic data
        
        This method integrates 150+ diagnostic checkpoints with AI insights to provide
        professional-grade SEO analysis comparable to Ahrefs, SEMrush, and Screaming Frog.
        
        Args:
            enhanced_context: Comprehensive context including:
                - professional_analysis: 150+ diagnostic checkpoints data
                - basic_content: Traditional SEO analysis results
                - pagespeed_insights: Core Web Vitals and performance data
                - trends_insights: Google Trends and keyword data
        
        Returns:
            Professional-level SEO analysis and recommendations with:
            - Strategic assessment combining diagnostic insights
            - Professional-grade optimization priorities
            - Implementation timeline with ROI projections
            - Risk mitigation strategies
        """
        import time
        start_time = time.time()
        logger.info("🎯 Starting Enhanced Professional Analysis with Diagnostic Integration")
        
        try:
            # Use Silicon Flow for professional analysis
            logger.info("📡 Using SiliconFlow for professional diagnostic integration")
            result = await self.siliconflow_llm.analyze_seo_data(enhanced_context, "professional")
            
            # Enhance with diagnostic metadata
            if 'professional_analysis' in enhanced_context:
                prof_data = enhanced_context['professional_analysis']
                result['diagnostic_metadata'] = {
                    'total_checkpoints': len(prof_data.get('all_issues', [])),
                    'overall_score': prof_data.get('overall_score', 0),
                    'critical_issues': len([i for i in prof_data.get('all_issues', []) if i.get('priority') == 'critical']),
                    'analysis_source': 'siliconflow_professional'
                }
            
            # Add execution timing
            execution_time = time.time() - start_time
            result['professional_analysis_metadata'] = {
                'execution_time': execution_time,
                'provider': 'siliconflow',
                'status': 'completed',
                'analysis_depth': 'professional_grade'
            }
            
            logger.info(f"✅ Enhanced professional analysis completed in {execution_time:.2f}s")
            return result
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"💥 Critical error in enhanced professional analysis after {execution_time:.2f}s: {e}")
            
            # Fallback to basic analysis
            try:
                basic_result = await self.enhance_seo_analysis(enhanced_context.get('basic_content', {}))
                basic_result['professional_analysis_error'] = {
                    'error_message': str(e),
                    'fallback_used': 'basic_analysis',
                    'execution_time': execution_time
                }
                return basic_result
            except Exception as fallback_error:
                logger.error(f"💥 Even fallback analysis failed: {fallback_error}")
                return {
                    'professional_analysis_failed': True,
                    'error_message': str(e),
                    'fallback_error': str(fallback_error),
                    'execution_time': execution_time,
                    'recommendations': ['Professional analysis unavailable - please check SiliconFlow API key and network connectivity']
                }


# Example usage with async support
async def enhanced_modern_analyze(
    site: str, sitemap: Optional[str] = None, siliconflow_api_key: str = None, **kwargs
):
    """
    Enhanced analysis incorporating modern SEO principles using SiliconFlow
    """
    from pyseoanalyzer import analyze

    # Run original analysis
    original_results = analyze(site, sitemap, **kwargs)

    # Enhance with modern SEO analysis if API key provided
    if siliconflow_api_key or os.getenv("SILICONFLOW_API_KEY"):
        enhancer = LLMSEOEnhancer(siliconflow_api_key)
        enhanced_results = await enhancer.enhance_seo_analysis(original_results)
        return enhancer._format_output(enhanced_results)

    return original_results