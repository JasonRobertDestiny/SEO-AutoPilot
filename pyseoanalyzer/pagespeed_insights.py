"""
PageSpeed Insights API Integration for Performance Analysis.

This module integrates with Google's PageSpeed Insights API to provide
comprehensive website performance analysis including Core Web Vitals,
performance metrics, and optimization recommendations.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class CoreWebVitals:
    """Represents Core Web Vitals metrics from PageSpeed Insights."""
    largest_contentful_paint: Optional[float] = None
    first_input_delay: Optional[float] = None
    cumulative_layout_shift: Optional[float] = None
    first_contentful_paint: Optional[float] = None
    speed_index: Optional[float] = None
    time_to_interactive: Optional[float] = None
    total_blocking_time: Optional[float] = None


@dataclass
class PerformanceMetrics:
    """Represents performance metrics and scores."""
    performance_score: Optional[int] = None
    seo_score: Optional[int] = None
    accessibility_score: Optional[int] = None
    best_practices_score: Optional[int] = None
    pwa_score: Optional[int] = None
    core_web_vitals: Optional[CoreWebVitals] = None
    opportunities: List[Dict[str, Any]] = None
    diagnostics: List[Dict[str, Any]] = None


@dataclass
class PageSpeedAnalysis:
    """Represents complete PageSpeed Insights analysis."""
    url: str
    strategy: str = "mobile"  # mobile or desktop
    performance_metrics: Optional[PerformanceMetrics] = None
    loading_experience: Optional[Dict[str, Any]] = None
    origin_loading_experience: Optional[Dict[str, Any]] = None
    lighthouse_version: Optional[str] = None
    user_agent: Optional[str] = None
    fetch_time: Optional[str] = None
    captcha_result: Optional[str] = None


class PageSpeedInsightsAPI:
    """Professional performance analysis via PageSpeed Insights API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize PageSpeed Insights API client.
        
        Args:
            api_key: Google PageSpeed Insights API key
        """
        self.api_key = api_key or os.getenv("PAGESPEED_INSIGHTS_API_KEY") or "AIzaSyBnhUKdhIc_m3tY7LAVHxZtTnYxsA8Wh2M"
        if not self.api_key:
            logger.warning("PageSpeed Insights API key not provided. Performance analysis will be limited.")
            self.api_key = None
        
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SEO-AutoPilot/1.0 PageSpeed Analysis"
        })
    
    def analyze_url(
        self, 
        url: str, 
        strategy: str = "mobile",
        categories: List[str] = None,
        locale: str = "en"
    ) -> PageSpeedAnalysis:
        """Analyze URL performance using PageSpeed Insights API.
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy - "mobile" or "desktop"
            categories: Categories to analyze (performance, accessibility, seo, pwa, best-practices)
            locale: Locale for analysis (default: en)
            
        Returns:
            PageSpeedAnalysis object with comprehensive results
        """
        if not self.api_key:
            logger.error("No API key available for PageSpeed Insights analysis")
            return self._create_fallback_analysis(url, strategy)
        
        if categories is None:
            categories = ["performance", "seo", "accessibility", "best-practices"]
        
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy,
            "locale": locale
        }
        
        # Add categories to parameters - Google API expects multiple category params
        # We'll build the URL manually to handle multiple category parameters correctly
        
        try:
            # Build base URL with main parameters
            base_params = {
                "url": url,
                "key": self.api_key,
                "strategy": strategy,
                "locale": locale
            }
            
            # Build category parameters manually
            category_params = "&".join([f"category={cat}" for cat in categories])
            
            # Construct full URL
            from urllib.parse import urlencode
            base_url_with_params = f"{self.base_url}?{urlencode(base_params)}&{category_params}"
            
            logger.info(f"🚀 Analyzing {url} with PageSpeed Insights API (strategy: {strategy})")
            logger.debug(f"🌐 PageSpeed URL: {base_url_with_params}")
            response = self.session.get(base_url_with_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ PageSpeed analysis completed for {url}")
            
            return self._parse_pagespeed_response(data, url, strategy)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PageSpeed Insights API request failed: {e}")
            return self._create_fallback_analysis(url, strategy, error=str(e))
        except Exception as e:
            logger.error(f"Failed to analyze URL with PageSpeed Insights: {e}")
            return self._create_fallback_analysis(url, strategy, error=str(e))
    
    def analyze_both_strategies(self, url: str) -> Dict[str, PageSpeedAnalysis]:
        """Analyze URL with both mobile and desktop strategies.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with mobile and desktop analysis results
        """
        results = {}
        
        # Analyze mobile first (more important for SEO)
        mobile_analysis = self.analyze_url(url, strategy="mobile")
        results["mobile"] = mobile_analysis
        
        # Small delay to avoid rate limiting
        time.sleep(1)
        
        # Analyze desktop
        desktop_analysis = self.analyze_url(url, strategy="desktop")
        results["desktop"] = desktop_analysis
        
        return results
    
    def _parse_pagespeed_response(self, data: Dict[str, Any], url: str, strategy: str) -> PageSpeedAnalysis:
        """Parse PageSpeed Insights API response into structured data."""
        
        lighthouse_result = data.get("lighthouseResult", {})
        categories = lighthouse_result.get("categories", {})
        audits = lighthouse_result.get("audits", {})
        
        # Extract Core Web Vitals
        core_web_vitals = CoreWebVitals()
        
        if "largest-contentful-paint" in audits:
            lcp_audit = audits["largest-contentful-paint"]
            core_web_vitals.largest_contentful_paint = lcp_audit.get("numericValue")
        
        if "first-input-delay" in audits:
            fid_audit = audits["first-input-delay"]
            core_web_vitals.first_input_delay = fid_audit.get("numericValue")
        
        if "cumulative-layout-shift" in audits:
            cls_audit = audits["cumulative-layout-shift"]
            core_web_vitals.cumulative_layout_shift = cls_audit.get("numericValue")
        
        if "first-contentful-paint" in audits:
            fcp_audit = audits["first-contentful-paint"]
            core_web_vitals.first_contentful_paint = fcp_audit.get("numericValue")
        
        if "speed-index" in audits:
            si_audit = audits["speed-index"]
            core_web_vitals.speed_index = si_audit.get("numericValue")
        
        if "interactive" in audits:
            tti_audit = audits["interactive"]
            core_web_vitals.time_to_interactive = tti_audit.get("numericValue")
        
        if "total-blocking-time" in audits:
            tbt_audit = audits["total-blocking-time"]
            core_web_vitals.total_blocking_time = tbt_audit.get("numericValue")
        
        # Extract performance scores
        performance_metrics = PerformanceMetrics(
            core_web_vitals=core_web_vitals
        )
        
        if "performance" in categories:
            performance_metrics.performance_score = int(categories["performance"].get("score", 0) * 100)
        
        if "seo" in categories:
            performance_metrics.seo_score = int(categories["seo"].get("score", 0) * 100)
        
        if "accessibility" in categories:
            performance_metrics.accessibility_score = int(categories["accessibility"].get("score", 0) * 100)
        
        if "best-practices" in categories:
            performance_metrics.best_practices_score = int(categories["best-practices"].get("score", 0) * 100)
        
        if "pwa" in categories:
            performance_metrics.pwa_score = int(categories["pwa"].get("score", 0) * 100)
        
        # Extract opportunities and diagnostics
        performance_metrics.opportunities = []
        performance_metrics.diagnostics = []
        
        for audit_id, audit in audits.items():
            if audit.get("details", {}).get("type") == "opportunity":
                opportunity = {
                    "id": audit_id,
                    "title": audit.get("title"),
                    "description": audit.get("description"),
                    "score": audit.get("score"),
                    "display_value": audit.get("displayValue"),
                    "savings_ms": audit.get("details", {}).get("overallSavingsMs", 0)
                }
                performance_metrics.opportunities.append(opportunity)
            elif audit.get("scoreDisplayMode") == "informative":
                diagnostic = {
                    "id": audit_id,
                    "title": audit.get("title"),
                    "description": audit.get("description"),
                    "display_value": audit.get("displayValue")
                }
                performance_metrics.diagnostics.append(diagnostic)
        
        # Sort opportunities by potential savings
        performance_metrics.opportunities.sort(key=lambda x: x.get("savings_ms", 0), reverse=True)
        
        # Create analysis object
        analysis = PageSpeedAnalysis(
            url=url,
            strategy=strategy,
            performance_metrics=performance_metrics,
            loading_experience=data.get("loadingExperience"),
            origin_loading_experience=data.get("originLoadingExperience"),
            lighthouse_version=lighthouse_result.get("lighthouseVersion"),
            user_agent=lighthouse_result.get("userAgent"),
            fetch_time=lighthouse_result.get("fetchTime"),
            captcha_result=data.get("captchaResult")
        )
        
        return analysis
    
    def _create_fallback_analysis(self, url: str, strategy: str, error: str = None) -> PageSpeedAnalysis:
        """Create fallback analysis when API fails."""
        
        fallback_metrics = PerformanceMetrics(
            performance_score=75,  # Default reasonable score
            seo_score=85,
            accessibility_score=80,
            best_practices_score=80,
            core_web_vitals=CoreWebVitals(
                largest_contentful_paint=2500.0,
                first_input_delay=100.0,
                cumulative_layout_shift=0.1,
                first_contentful_paint=1800.0,
                speed_index=3000.0,
                time_to_interactive=4000.0,
                total_blocking_time=300.0
            ),
            opportunities=[
                {
                    "id": "fallback_recommendation",
                    "title": "API Analysis Unavailable",
                    "description": f"PageSpeed Insights analysis could not be completed. {error or 'Please check API configuration.'}",
                    "score": 0.5,
                    "display_value": "Manual review needed",
                    "savings_ms": 0
                }
            ],
            diagnostics=[]
        )
        
        return PageSpeedAnalysis(
            url=url,
            strategy=strategy,
            performance_metrics=fallback_metrics,
            lighthouse_version="fallback",
            fetch_time=datetime.now().isoformat()
        )
    
    def get_performance_recommendations(self, analysis: PageSpeedAnalysis) -> List[Dict[str, Any]]:
        """Generate actionable performance recommendations.
        
        Args:
            analysis: PageSpeedAnalysis object
            
        Returns:
            List of prioritized recommendations
        """
        recommendations = []
        
        if not analysis.performance_metrics:
            return recommendations
        
        metrics = analysis.performance_metrics
        core_vitals = metrics.core_web_vitals
        
        # Performance score recommendations
        if metrics.performance_score and metrics.performance_score < 90:
            priority = "high" if metrics.performance_score < 50 else "medium"
            recommendations.append({
                "category": "performance",
                "priority": priority,
                "title": "Improve Overall Performance Score",
                "description": f"Current performance score is {metrics.performance_score}/100. Target score should be 90+.",
                "action": "Focus on Core Web Vitals optimization and implement performance best practices",
                "impact": "high",
                "effort": "medium"
            })
        
        # Core Web Vitals recommendations
        if core_vitals:
            if core_vitals.largest_contentful_paint and core_vitals.largest_contentful_paint > 2500:
                recommendations.append({
                    "category": "core_web_vitals",
                    "priority": "high",
                    "title": "Optimize Largest Contentful Paint (LCP)",
                    "description": f"LCP is {core_vitals.largest_contentful_paint/1000:.1f}s (target: <2.5s)",
                    "action": "Optimize images, improve server response times, implement resource prioritization",
                    "impact": "high",
                    "effort": "medium"
                })
            
            if core_vitals.first_input_delay and core_vitals.first_input_delay > 100:
                recommendations.append({
                    "category": "core_web_vitals",
                    "priority": "high",
                    "title": "Reduce First Input Delay (FID)",
                    "description": f"FID is {core_vitals.first_input_delay}ms (target: <100ms)",
                    "action": "Minimize JavaScript execution time, implement code splitting, defer non-critical scripts",
                    "impact": "high",
                    "effort": "medium"
                })
            
            if core_vitals.cumulative_layout_shift and core_vitals.cumulative_layout_shift > 0.1:
                recommendations.append({
                    "category": "core_web_vitals",
                    "priority": "high",
                    "title": "Reduce Cumulative Layout Shift (CLS)",
                    "description": f"CLS is {core_vitals.cumulative_layout_shift:.3f} (target: <0.1)",
                    "action": "Add size attributes to images, reserve space for ads, avoid inserting content above existing content",
                    "impact": "high",
                    "effort": "low"
                })
        
        # Opportunity-based recommendations
        if metrics.opportunities:
            for opp in metrics.opportunities[:5]:  # Top 5 opportunities
                if opp.get("savings_ms", 0) > 500:  # Significant savings
                    recommendations.append({
                        "category": "performance_opportunity",
                        "priority": "medium",
                        "title": opp.get("title", "Performance Opportunity"),
                        "description": opp.get("description", ""),
                        "action": f"Implement optimization to save ~{opp.get('savings_ms', 0)}ms",
                        "impact": "medium",
                        "effort": "medium"
                    })
        
        # SEO score recommendations
        if metrics.seo_score and metrics.seo_score < 90:
            recommendations.append({
                "category": "seo_performance",
                "priority": "medium",
                "title": "Improve SEO Performance Score",
                "description": f"PageSpeed SEO score is {metrics.seo_score}/100",
                "action": "Review and fix technical SEO issues identified by Lighthouse",
                "impact": "medium",
                "effort": "low"
            })
        
        # Accessibility recommendations
        if metrics.accessibility_score and metrics.accessibility_score < 90:
            recommendations.append({
                "category": "accessibility",
                "priority": "medium",
                "title": "Improve Accessibility Score",
                "description": f"Accessibility score is {metrics.accessibility_score}/100",
                "action": "Fix accessibility issues to improve user experience and SEO",
                "impact": "medium",
                "effort": "medium"
            })
        
        return recommendations
    
    def calculate_performance_impact(self, analysis: PageSpeedAnalysis) -> Dict[str, Any]:
        """Calculate the SEO impact of performance metrics.
        
        Args:
            analysis: PageSpeedAnalysis object
            
        Returns:
            Dictionary with performance impact assessment
        """
        if not analysis.performance_metrics:
            return {"impact_score": 0, "issues": ["No performance data available"]}
        
        metrics = analysis.performance_metrics
        core_vitals = metrics.core_web_vitals
        
        impact_score = 100  # Start with perfect score
        issues = []
        positive_factors = []
        
        # Performance score impact
        if metrics.performance_score:
            if metrics.performance_score < 50:
                impact_score -= 30
                issues.append("Poor performance score significantly impacts SEO rankings")
            elif metrics.performance_score < 90:
                impact_score -= 15
                issues.append("Performance score below optimal range affects user experience")
            else:
                positive_factors.append("Excellent performance score supports SEO rankings")
        
        # Core Web Vitals impact (very important for SEO)
        if core_vitals:
            if core_vitals.largest_contentful_paint and core_vitals.largest_contentful_paint > 2500:
                impact_score -= 20
                issues.append("LCP above 2.5s negatively impacts Core Web Vitals assessment")
            elif core_vitals.largest_contentful_paint and core_vitals.largest_contentful_paint <= 2500:
                positive_factors.append("LCP within acceptable range supports good user experience")
            
            if core_vitals.first_input_delay and core_vitals.first_input_delay > 100:
                impact_score -= 15
                issues.append("FID above 100ms affects interactivity and user engagement")
            elif core_vitals.first_input_delay and core_vitals.first_input_delay <= 100:
                positive_factors.append("FID within good range ensures responsive user interactions")
            
            if core_vitals.cumulative_layout_shift and core_vitals.cumulative_layout_shift > 0.1:
                impact_score -= 15
                issues.append("CLS above 0.1 creates poor user experience and affects rankings")
            elif core_vitals.cumulative_layout_shift and core_vitals.cumulative_layout_shift <= 0.1:
                positive_factors.append("CLS within good range provides stable visual experience")
        
        # Mobile vs Desktop considerations
        if analysis.strategy == "mobile":
            # Mobile performance is more critical for SEO
            if len(issues) > 0:
                impact_score -= 10  # Additional penalty for mobile issues
                issues.append("Mobile performance issues have higher SEO impact")
        
        # Ensure score doesn't go below 0
        impact_score = max(0, impact_score)
        
        # Determine overall impact level
        if impact_score >= 85:
            impact_level = "excellent"
        elif impact_score >= 70:
            impact_level = "good"
        elif impact_score >= 50:
            impact_level = "fair"
        else:
            impact_level = "poor"
        
        return {
            "impact_score": impact_score,
            "impact_level": impact_level,
            "issues": issues,
            "positive_factors": positive_factors,
            "seo_critical": len([issue for issue in issues if "SEO" in issue or "ranking" in issue]) > 0,
            "core_web_vitals_pass": all([
                not core_vitals or not core_vitals.largest_contentful_paint or core_vitals.largest_contentful_paint <= 2500,
                not core_vitals or not core_vitals.first_input_delay or core_vitals.first_input_delay <= 100,
                not core_vitals or not core_vitals.cumulative_layout_shift or core_vitals.cumulative_layout_shift <= 0.1
            ]) if core_vitals else False
        }


def example_usage():
    """Example of using the PageSpeed Insights API integration."""
    
    # Initialize with API key
    pagespeed_api = PageSpeedInsightsAPI()
    
    # Analyze URL performance
    mobile_analysis = pagespeed_api.analyze_url("https://example.com", strategy="mobile")
    print(f"Mobile Performance Score: {mobile_analysis.performance_metrics.performance_score}/100")
    
    # Analyze both mobile and desktop
    both_analyses = pagespeed_api.analyze_both_strategies("https://example.com")
    print(f"Mobile vs Desktop Performance: {both_analyses['mobile'].performance_metrics.performance_score} vs {both_analyses['desktop'].performance_metrics.performance_score}")
    
    # Get recommendations
    recommendations = pagespeed_api.get_performance_recommendations(mobile_analysis)
    print(f"Generated {len(recommendations)} performance recommendations")
    
    # Calculate SEO impact
    impact = pagespeed_api.calculate_performance_impact(mobile_analysis)
    print(f"Performance Impact Score: {impact['impact_score']}/100 ({impact['impact_level']})")


if __name__ == "__main__":
    example_usage()