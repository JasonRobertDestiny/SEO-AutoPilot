"""
Enhanced LLM Analyst with multi-data source integration for SEO Agent.

This module extends the existing LLM analysis capabilities to incorporate
Google Analytics and Search Console data for comprehensive SEO insights.
"""

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from .siliconflow_llm import SiliconFlowLLM

import asyncio
import json
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class DataDrivenInsights(BaseModel):
    """Enhanced insights incorporating Google data."""
    performance_summary: str = Field(description="Summary of overall performance")
    opportunity_areas: List[str] = Field(description="Key areas for improvement")
    strategic_priorities: List[str] = Field(description="Strategic priorities based on data")
    quick_wins: List[str] = Field(description="Quick improvements to implement")
    long_term_projects: List[str] = Field(description="Major projects for long-term success")


class TrendAnalysis(BaseModel):
    """Analysis of trends over time."""
    traffic_trends: str = Field(description="Analysis of traffic patterns")
    ranking_changes: str = Field(description="Search ranking trends")
    user_behavior_changes: str = Field(description="Changes in user behavior")
    content_performance: str = Field(description="Content performance trends")


class PredictiveInsights(BaseModel):
    """Predictive recommendations based on data patterns."""
    future_opportunities: List[str] = Field(description="Predicted opportunities")
    risk_areas: List[str] = Field(description="Potential risks to address")
    growth_predictions: str = Field(description="Growth predictions")
    competitive_advantages: List[str] = Field(description="Potential competitive advantages")


class EnhancedLLMSEOAnalyst:
    """Enhanced LLM SEO Analyst with multi-data source integration using SiliconFlow API."""
    
    def __init__(self, siliconflow_api_key: Optional[str] = None, siliconflow_model: Optional[str] = None):
        """Initialize the enhanced analyst with SiliconFlow API.
        
        Args:
            siliconflow_api_key: Silicon Flow API key
            siliconflow_model: Silicon Flow model to use (defaults to env var or Qwen/Qwen2.5-VL-72B-Instruct)
        """
        # Get model from parameter, env var, or default
        model = siliconflow_model or os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
        self.siliconflow_llm = SiliconFlowLLM(siliconflow_api_key, model)
        
        logger.info(f"🚀 Enhanced LLM SEO Analyst initialized with SiliconFlow model: {model}")
    
    
    async def analyze_comprehensive_data(
        self,
        seo_analysis: Dict[str, Any],
        google_insights: Dict[str, Any],
        competitive_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining all data sources using SiliconFlow API.
        
        Args:
            seo_analysis: Traditional SEO analysis results
            google_insights: Google Analytics and Search Console data
            competitive_context: Optional competitive analysis data
            
        Returns:
            Comprehensive analysis results with strategic insights
        """
        import time
        start_time = time.time()
        logger.info("🎯 Starting Enhanced Comprehensive Analysis with SiliconFlow")
        
        try:
            # Extract data from Google insights
            analytics_summary = google_insights.get('analytics_summary', {})
            search_summary = google_insights.get('search_summary', {})
            page_performance = google_insights.get('page_performance', {})
            recommendations = google_insights.get('recommendations', [])
            
            # Prepare comprehensive context for analysis
            comprehensive_context = {
                'seo_analysis': seo_analysis,
                'analytics_summary': analytics_summary,
                'search_summary': search_summary,
                'page_performance': page_performance,
                'competitive_context': competitive_context or {},
                'analysis_type': 'comprehensive_multi_source'
            }
            
            # Use SiliconFlow for comprehensive analysis
            logger.info("📡 Using SiliconFlow for multi-source comprehensive analysis")
            result = await self.siliconflow_llm.analyze_seo_data(comprehensive_context, "comprehensive")
            
            # Structure the results for compatibility
            comprehensive_analysis = {
                "data_driven_insights": self._extract_insights(result),
                "trend_analysis": self._extract_trends(result),
                "predictive_insights": self._extract_predictions(result),
                "google_data_recommendations": recommendations,
                "analysis_timestamp": str(time.time()),
                "siliconflow_metadata": {
                    "model_used": self.siliconflow_llm.model,
                    "provider": "siliconflow",
                    "analysis_type": "comprehensive_multi_source"
                }
            }
            
            execution_time = time.time() - start_time
            comprehensive_analysis["execution_metadata"] = {
                "total_time": execution_time,
                "status": "completed"
            }
            
            logger.info(f"✅ Enhanced comprehensive analysis completed in {execution_time:.2f}s")
            return comprehensive_analysis
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"💥 Enhanced comprehensive analysis failed after {execution_time:.2f}s: {e}")
            
            # Return fallback structure
            return {
                "data_driven_insights": self._get_fallback_insights(seo_analysis),
                "trend_analysis": self._get_fallback_trends(),
                "predictive_insights": self._get_fallback_predictions(),
                "google_data_recommendations": google_insights.get('recommendations', []),
                "analysis_timestamp": str(time.time()),
                "error_metadata": {
                    "error_message": str(e),
                    "execution_time": execution_time,
                    "status": "failed_with_fallback"
                }
            }
    
    def _extract_insights(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data-driven insights from SiliconFlow result."""
        insights = result.get('insights', {})
        return {
            "performance_summary": insights.get('performance_summary', 'Comprehensive SEO analysis completed'),
            "opportunity_areas": insights.get('opportunity_areas', []),
            "strategic_priorities": insights.get('strategic_priorities', []),
            "quick_wins": insights.get('quick_wins', []),
            "long_term_projects": insights.get('long_term_projects', [])
        }
    
    def _extract_trends(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract trend analysis from SiliconFlow result."""
        trends = result.get('trends', {})
        return {
            "traffic_trends": trends.get('traffic_trends', 'Traffic trend analysis based on current data'),
            "ranking_changes": trends.get('ranking_changes', 'Ranking analysis based on SEO metrics'),
            "user_behavior_changes": trends.get('user_behavior_changes', 'User behavior insights from analytics'),
            "content_performance": trends.get('content_performance', 'Content performance evaluation')
        }
    
    def _extract_predictions(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract predictive insights from SiliconFlow result."""
        predictions = result.get('predictions', {})
        return {
            "future_opportunities": predictions.get('future_opportunities', []),
            "risk_areas": predictions.get('risk_areas', []),
            "growth_predictions": predictions.get('growth_predictions', 'Growth projections based on current metrics'),
            "competitive_advantages": predictions.get('competitive_advantages', [])
        }
    
    def _get_fallback_insights(self, seo_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback insights when analysis fails."""
        pages_count = len(seo_analysis.get('pages', []))
        keywords_count = len(seo_analysis.get('keywords', []))
        
        return {
            "performance_summary": f"Basic SEO analysis: {pages_count} pages, {keywords_count} keywords analyzed",
            "opportunity_areas": ["Review technical SEO issues", "Optimize content structure", "Improve keyword targeting"],
            "strategic_priorities": ["Technical optimization", "Content improvement", "Performance enhancement"],
            "quick_wins": ["Fix meta descriptions", "Optimize image alt texts", "Improve internal linking"],
            "long_term_projects": ["Content strategy development", "Site architecture optimization", "Performance monitoring setup"]
        }
    
    def _get_fallback_trends(self) -> Dict[str, Any]:
        """Provide fallback trend analysis."""
        return {
            "traffic_trends": "Trend analysis requires historical data - monitor performance over time",
            "ranking_changes": "Ranking trends need baseline data - establish tracking system",
            "user_behavior_changes": "User behavior analysis pending analytics integration",
            "content_performance": "Content performance evaluation based on SEO metrics"
        }
    
    def _get_fallback_predictions(self) -> Dict[str, Any]:
        """Provide fallback predictive insights."""
        return {
            "future_opportunities": ["Expand keyword targeting", "Improve technical performance", "Enhance content quality"],
            "risk_areas": ["Monitor competitor activity", "Track search algorithm changes", "Maintain technical health"],
            "growth_predictions": "Growth potential depends on consistent optimization efforts",
            "competitive_advantages": ["Focus on unique value proposition", "Optimize for user experience", "Build authority signals"]
        }
    
    def _prepare_seo_summary(self, seo_analysis: Dict[str, Any]) -> str:
        """Prepare SEO analysis summary for LLM processing."""
        summary_parts = []
        
        # Basic metrics
        pages_count = len(seo_analysis.get('pages', []))
        keywords_count = len(seo_analysis.get('keywords', []))
        errors_count = len(seo_analysis.get('errors', []))
        
        summary_parts.append(f"Website analyzed: {pages_count} pages, {keywords_count} keywords, {errors_count} errors")
        
        # SEO optimization insights
        optimization = seo_analysis.get('optimization_recommendations', {})
        if optimization:
            score = optimization.get('overall_score', 0)
            summary_parts.append(f"SEO Score: {score}/100")
            
            issues_by_priority = optimization.get('issues_by_priority', {})
            for priority, count in issues_by_priority.items():
                if count > 0:
                    summary_parts.append(f"{priority.title()} priority issues: {count}")
        
        return "\n".join(summary_parts)
    
    def _format_analytics_data(self, analytics_data: Dict[str, Any]) -> str:
        """Format Google Analytics data for LLM analysis."""
        if not analytics_data:
            return "No analytics data available"
        
        formatted_parts = []
        
        for metric, value in analytics_data.items():
            if isinstance(value, (int, float)):
                formatted_parts.append(f"{metric}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _format_search_data(self, search_data: Dict[str, Any]) -> str:
        """Format Search Console data for LLM analysis."""
        if not search_data:
            return "No search console data available"
        
        formatted_parts = []
        
        for metric, value in search_data.items():
            if isinstance(value, (int, float)):
                if metric in ['avg_ctr', 'avg_position']:
                    formatted_parts.append(f"{metric}: {value:.2f}")
                else:
                    formatted_parts.append(f"{metric}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _format_page_performance(self, page_performance: Dict[str, Any]) -> str:
        """Format page-level performance data."""
        if not page_performance:
            return "No page performance data available"
        
        # Show top 5 pages by performance
        formatted_parts = []
        top_pages = list(page_performance.items())[:5]
        
        for page_path, metrics in top_pages:
            pageviews = metrics.get('pageviews', 0)
            bounce_rate = metrics.get('bounce_rate', 0)
            search_data = metrics.get('search_data', {})
            
            page_info = f"Page {page_path}: {pageviews} views, {bounce_rate:.1%} bounce rate"
            if search_data:
                position = search_data.get('position', 0)
                ctr = search_data.get('ctr', 0)
                page_info += f", Search position: {position:.1f}, CTR: {ctr:.2%}"
            
            formatted_parts.append(page_info)
        
        return "\n".join(formatted_parts)
    
    def generate_strategic_report(self, comprehensive_analysis: Dict[str, Any]) -> str:
        """Generate a strategic SEO report based on comprehensive analysis."""
        
        insights = comprehensive_analysis.get('data_driven_insights', {})
        trends = comprehensive_analysis.get('trend_analysis', {})
        predictive = comprehensive_analysis.get('predictive_insights', {})
        
        report = """
# SEO Agent Strategic Analysis Report

## Executive Summary
{performance_summary}

## Key Opportunity Areas
{opportunity_areas}

## Strategic Priorities
{strategic_priorities}

## Quick Wins (High Impact, Low Effort)
{quick_wins}

## Long-term Strategic Projects
{long_term_projects}

## Performance Trends Analysis
{trend_analysis}

## Predictive Insights & Future Opportunities
{predictive_insights}

## Action Plan
1. Immediate actions (next 30 days)
2. Short-term projects (1-3 months)
3. Long-term initiatives (3-12 months)
""".format(
            performance_summary=insights.get('performance_summary', 'Analysis in progress'),
            opportunity_areas='\n'.join(f'- {area}' for area in insights.get('opportunity_areas', [])),
            strategic_priorities='\n'.join(f'- {priority}' for priority in insights.get('strategic_priorities', [])),
            quick_wins='\n'.join(f'- {win}' for win in insights.get('quick_wins', [])),
            long_term_projects='\n'.join(f'- {project}' for project in insights.get('long_term_projects', [])),
            trend_analysis=f"Traffic: {trends.get('traffic_trends', 'Analyzing...')}\nRankings: {trends.get('ranking_changes', 'Analyzing...')}",
            predictive_insights='\n'.join(f'- {insight}' for insight in predictive.get('future_opportunities', []))
        )
        
        return report


# Example usage
async def main():
    """Example of using the enhanced LLM analyst with SiliconFlow."""
    analyst = EnhancedLLMSEOAnalyst()
    
    # Sample data (in real usage, this would come from actual analysis)
    seo_analysis = {
        "pages": [{"url": "https://example.com"}],
        "keywords": [{"word": "example", "count": 10}],
        "errors": [],
        "optimization_recommendations": {
            "overall_score": 75,
            "issues_by_priority": {"critical": 2, "high": 5}
        }
    }
    
    google_insights = {
        "analytics_summary": {"sessions": 1000, "pageviews": 2500},
        "search_summary": {"total_clicks": 150, "total_impressions": 10000},
        "page_performance": {},
        "recommendations": []
    }
    
    # Run comprehensive analysis
    results = await analyst.analyze_comprehensive_data(
        seo_analysis=seo_analysis,
        google_insights=google_insights
    )
    
    # Generate strategic report
    report = analyst.generate_strategic_report(results)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())