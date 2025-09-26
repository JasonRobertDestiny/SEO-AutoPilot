"""
Enhanced SEO Analysis Integration System

This module integrates all Phase 1 enhancements into the main SEO analysis workflow:
- Enhanced Content Analyzer
- Technical Performance Analyzer 
- Niche-Specific Analysis Engine
- Competitive Intelligence System

Usage:
    from pyseoanalyzer.enhanced_analysis_integration import perform_comprehensive_seo_analysis
    
    result = await perform_comprehensive_seo_analysis(
        url="https://example.com", 
        html_content=html, 
        enable_all_enhancements=True
    )
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Import all Phase 1 enhancement modules
from .enhanced_content_analyzer import AdvancedContentAnalyzer, WebsiteTypeDetector
from .enhanced_technical_analyzer import EnhancedTechnicalAnalyzer
from .niche_specific_analyzer import NicheSpecificAnalyzer, analyze_niche_specific_seo
from .competitive_intelligence import CompetitiveIntelligenceSystem, analyze_competitive_intelligence

logger = logging.getLogger(__name__)

class ComprehensiveAnalysisResult:
    """Comprehensive analysis result containing all enhancements."""
    
    def __init__(self):
        self.basic_analysis = {}
        self.enhanced_content_analysis = {}
        self.technical_analysis = {}
        self.niche_analysis = {}
        self.competitive_intelligence = {}
        self.analysis_metadata = {
            'timestamp': time.time(),
            'version': '2.0-enhanced',
            'components_used': []
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'basic_analysis': self.basic_analysis,
            'enhanced_content_analysis': self.enhanced_content_analysis,
            'technical_analysis': self.technical_analysis,
            'niche_analysis': self.niche_analysis,
            'competitive_intelligence': self.competitive_intelligence,
            'analysis_metadata': self.analysis_metadata,
            'summary': self._generate_analysis_summary()
        }
    
    def _generate_analysis_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis summary."""
        return {
            'overall_score': self._calculate_overall_score(),
            'primary_website_type': self.niche_analysis.get('website_type', 'general_website'),
            'industry_classification': self.niche_analysis.get('industry', 'general'),
            'content_quality_grade': self._get_content_quality_grade(),
            'technical_performance_grade': self._get_technical_grade(),
            'competitive_position': self.competitive_intelligence.get('market_positioning', {}).get('current_position', 'unknown'),
            'top_recommendations': self._get_top_recommendations(),
            'key_strengths': self._identify_key_strengths(),
            'critical_issues': self._identify_critical_issues()
        }
    
    def _calculate_overall_score(self) -> float:
        """Calculate weighted overall SEO score."""
        scores = []
        weights = []
        
        # Content score (30% weight)
        content_score = self.enhanced_content_analysis.get('content_quality', {}).get('quality_score', 0)
        if content_score > 0:
            scores.append(content_score)
            weights.append(30)
        
        # Technical score (25% weight)
        technical_score = self.technical_analysis.get('technical_score', {}).get('overall_score', 0)
        if technical_score > 0:
            scores.append(technical_score)
            weights.append(25)
        
        # Niche optimization score (20% weight) - derived from niche analysis
        target_keywords = len(self.niche_analysis.get('target_keywords', []))
        niche_score = min(100, (target_keywords / 20) * 100) if target_keywords else 0
        if niche_score > 0:
            scores.append(niche_score)
            weights.append(20)
        
        # Competitive positioning score (15% weight)
        position_mapping = {'market_leader': 90, 'challenger': 75, 'follower': 60, 'niche_player': 70, 'newcomer': 40}
        position = self.competitive_intelligence.get('market_positioning', {}).get('current_position', 'newcomer')
        competitive_score = position_mapping.get(position, 50)
        scores.append(competitive_score)
        weights.append(15)
        
        # Basic analysis score (10% weight)
        basic_word_count = self.basic_analysis.get('word_count', 0)
        basic_score = min(100, (basic_word_count / 1000) * 100) if basic_word_count else 0
        scores.append(basic_score)
        weights.append(10)
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            return round(weighted_sum / total_weight, 1)
        
        return 0.0
    
    def _get_content_quality_grade(self) -> str:
        """Get content quality letter grade."""
        score = self.enhanced_content_analysis.get('content_quality', {}).get('quality_score', 0)
        return self._score_to_grade(score)
    
    def _get_technical_grade(self) -> str:
        """Get technical performance letter grade."""
        score = self.technical_analysis.get('technical_score', {}).get('overall_score', 0)
        return self._score_to_grade(score)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'A-'
        elif score >= 75: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 65: return 'B-'
        elif score >= 60: return 'C+'
        elif score >= 55: return 'C'
        elif score >= 50: return 'C-'
        elif score >= 45: return 'D'
        else: return 'F'
    
    def _get_top_recommendations(self) -> List[str]:
        """Get top 5 actionable recommendations."""
        recommendations = []
        
        # From competitive intelligence
        strategic_recs = self.competitive_intelligence.get('strategic_recommendations', [])
        for rec in strategic_recs[:3]:
            if isinstance(rec, dict) and 'title' in rec:
                recommendations.append(rec['title'])
        
        # From niche analysis
        niche_recs = self.niche_analysis.get('optimization_roadmap', [])
        for phase in niche_recs:
            if isinstance(phase, dict) and 'tasks' in phase:
                recommendations.extend(phase['tasks'][:2])
        
        # From content analysis
        content_issues = self.enhanced_content_analysis.get('content_quality', {}).get('issues', [])
        recommendations.extend(content_issues[:2])
        
        return recommendations[:5]
    
    def _identify_key_strengths(self) -> List[str]:
        """Identify top strengths of the website."""
        strengths = []
        
        # Content strengths
        content_strengths = self.enhanced_content_analysis.get('content_quality', {}).get('strengths', [])
        strengths.extend(content_strengths[:2])
        
        # Technical strengths
        tech_scores = self.technical_analysis.get('technical_score', {}).get('component_scores', {})
        for component, score in tech_scores.items():
            if score >= 80:
                strengths.append(f"Excellent {component.replace('_', ' ')}")
        
        # Competitive strengths
        market_pos = self.competitive_intelligence.get('market_positioning', {})
        if market_pos.get('authority_percentile', 0) >= 70:
            strengths.append("Strong domain authority")
        
        return strengths[:4]
    
    def _identify_critical_issues(self) -> List[str]:
        """Identify critical issues requiring immediate attention."""
        issues = []
        
        # Content issues
        content_issues = self.enhanced_content_analysis.get('content_quality', {}).get('issues', [])
        critical_content = [issue for issue in content_issues if 'critical' in issue.lower() or 'missing' in issue.lower()]
        issues.extend(critical_content)
        
        # Technical issues
        tech_score = self.technical_analysis.get('technical_score', {}).get('overall_score', 0)
        if tech_score < 50:
            issues.append("Critical technical performance issues detected")
        
        # Competitive issues
        comp_gaps = self.competitive_intelligence.get('competitive_gaps', [])
        critical_gaps = [gap for gap in comp_gaps if gap.get('priority') == 'critical']
        for gap in critical_gaps[:2]:
            issues.append(f"Critical gap: {gap.get('title', 'Unknown issue')}")
        
        return issues[:3]

class EnhancedAnalysisIntegrator:
    """Main integration class for enhanced SEO analysis."""
    
    def __init__(self, pagespeed_api_key: Optional[str] = None):
        self.pagespeed_api_key = pagespeed_api_key
        self.content_analyzer = AdvancedContentAnalyzer()
        self.technical_analyzer = EnhancedTechnicalAnalyzer(pagespeed_api_key)
        self.niche_analyzer = NicheSpecificAnalyzer()
        self.competitive_system = CompetitiveIntelligenceSystem()
    
    async def perform_comprehensive_analysis(self, 
                                           url: str,
                                           html_content: str,
                                           basic_page_data: Dict[str, Any],
                                           enable_all_enhancements: bool = True,
                                           enable_competitive_intelligence: bool = True) -> ComprehensiveAnalysisResult:
        """
        Perform comprehensive SEO analysis with all Phase 1 enhancements.
        
        Args:
            url: Website URL to analyze
            html_content: Raw HTML content
            basic_page_data: Basic page analysis data from existing system
            enable_all_enhancements: Whether to run all enhancement modules
            enable_competitive_intelligence: Whether to include competitive analysis
            
        Returns:
            ComprehensiveAnalysisResult with all analysis components
        """
        
        result = ComprehensiveAnalysisResult()
        result.basic_analysis = basic_page_data
        
        try:
            # Phase 1.1: Enhanced Content Analysis
            if enable_all_enhancements:
                logger.info("🔍 Starting enhanced content analysis...")
                
                enhanced_content = self.content_analyzer.extract_comprehensive_content(html_content, url)
                website_type_info = WebsiteTypeDetector.detect_website_type_advanced(enhanced_content, url)
                enhanced_content['website_type_info'] = website_type_info
                
                result.enhanced_content_analysis = enhanced_content
                result.analysis_metadata['components_used'].append('enhanced_content_analyzer')
                
                logger.info(f"✅ Content analysis complete: {enhanced_content.get('total_word_count', 0)} words detected")
            
            # Phase 1.2: Technical Performance Analysis
            if enable_all_enhancements:
                logger.info("⚡ Starting technical performance analysis...")
                
                technical_analysis = await self.technical_analyzer.analyze_technical_performance(url, html_content)
                result.technical_analysis = technical_analysis
                result.analysis_metadata['components_used'].append('technical_analyzer')
                
                tech_score = technical_analysis.get('technical_score', {}).get('overall_score', 0)
                logger.info(f"✅ Technical analysis complete: Overall score {tech_score}")
            
            # Phase 1.3: Niche-Specific Analysis
            if enable_all_enhancements and result.enhanced_content_analysis:
                logger.info("🎯 Starting niche-specific analysis...")
                
                # Prepare data for niche analysis
                website_data = {
                    'url': url,
                    'title': basic_page_data.get('title', ''),
                    'description': basic_page_data.get('description', ''),
                    'word_count': result.enhanced_content_analysis.get('total_word_count', 0)
                }
                
                niche_analysis = analyze_niche_specific_seo(
                    website_data, 
                    result.enhanced_content_analysis,
                    result.technical_analysis
                )
                
                result.niche_analysis = niche_analysis
                result.analysis_metadata['components_used'].append('niche_analyzer')
                
                website_type = niche_analysis.get('website_type', 'general')
                logger.info(f"✅ Niche analysis complete: Detected as {website_type}")
            
            # Phase 1.4: Competitive Intelligence Analysis
            if enable_competitive_intelligence and result.niche_analysis:
                logger.info("🏆 Starting competitive intelligence analysis...")
                
                website_data = {
                    'url': url,
                    'title': basic_page_data.get('title', ''),
                    'description': basic_page_data.get('description', '')
                }
                
                competitive_intel = await analyze_competitive_intelligence(
                    website_data,
                    result.niche_analysis,
                    result.enhanced_content_analysis,
                    result.technical_analysis
                )
                
                result.competitive_intelligence = competitive_intel
                result.analysis_metadata['components_used'].append('competitive_intelligence')
                
                position = competitive_intel.get('market_positioning', {}).get('current_position', 'unknown')
                competitor_count = len(competitive_intel.get('competitor_profiles', []))
                logger.info(f"✅ Competitive analysis complete: Position as {position}, {competitor_count} competitors analyzed")
            
            logger.info(f"🎉 Comprehensive analysis complete! Used components: {', '.join(result.analysis_metadata['components_used'])}")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            # Return partial results even if some components fail
            result.analysis_metadata['error'] = str(e)
            result.analysis_metadata['partial_results'] = True
            return result

# Convenience functions for integration with existing codebase

async def perform_comprehensive_seo_analysis(url: str,
                                           html_content: str,
                                           basic_page_data: Dict[str, Any],
                                           pagespeed_api_key: Optional[str] = None,
                                           enable_all_enhancements: bool = True) -> Dict[str, Any]:
    """
    Main entry point for comprehensive SEO analysis with all enhancements.
    
    This function can be called from the existing Page.analyze() method or
    used as a standalone comprehensive analysis function.
    
    Usage:
        # In page.py analyze() method:
        if self.run_enhanced_analysis:
            enhanced_results = await perform_comprehensive_seo_analysis(
                self.url, html_content, self.as_dict(), pagespeed_api_key
            )
            self.enhanced_analysis_results = enhanced_results
    
    Returns:
        Dictionary containing all analysis results ready for JSON serialization
    """
    
    integrator = EnhancedAnalysisIntegrator(pagespeed_api_key)
    
    result = await integrator.perform_comprehensive_analysis(
        url=url,
        html_content=html_content,
        basic_page_data=basic_page_data,
        enable_all_enhancements=enable_all_enhancements
    )
    
    return result.to_dict()

def integrate_with_existing_page_class(page_instance, html_content: str, pagespeed_api_key: str = None):
    """
    Helper function to integrate enhanced analysis with existing Page class.
    
    Usage:
        # Add to Page.analyze() method around line 310:
        if self.run_enhanced_analysis:
            self.enhanced_analysis = integrate_with_existing_page_class(
                self, html_without_comments, pagespeed_api_key
            )
    """
    
    try:
        # Run the comprehensive analysis
        loop = asyncio.get_event_loop()
        enhanced_results = loop.run_until_complete(
            perform_comprehensive_seo_analysis(
                url=page_instance.url,
                html_content=html_content,
                basic_page_data=page_instance.as_dict(),
                pagespeed_api_key=pagespeed_api_key,
                enable_all_enhancements=True
            )
        )
        
        # Update page instance with enhanced data
        enhanced_content = enhanced_results.get('enhanced_content_analysis', {})
        if enhanced_content.get('total_word_count', 0) > page_instance.total_word_count:
            page_instance.total_word_count = enhanced_content['total_word_count']
            logger.info(f"📊 Updated word count for {page_instance.url}: {page_instance.total_word_count} words")
        
        return enhanced_results
        
    except Exception as e:
        logger.error(f"Enhanced analysis integration failed: {e}")
        return {
            'error': str(e),
            'status': 'integration_failed',
            'fallback_message': 'Using basic analysis results'
        }

# Report enhancement functions

def generate_enhanced_seo_report(comprehensive_results: Dict[str, Any], 
                                format_type: str = 'detailed') -> Dict[str, Any]:
    """
    Generate an enhanced SEO report from comprehensive analysis results.
    
    Args:
        comprehensive_results: Results from perform_comprehensive_seo_analysis()
        format_type: 'detailed', 'executive_summary', or 'action_plan'
    
    Returns:
        Enhanced report dictionary with prioritized recommendations
    """
    
    summary = comprehensive_results.get('summary', {})
    
    if format_type == 'executive_summary':
        return {
            'overall_score': summary.get('overall_score', 0),
            'website_type': summary.get('primary_website_type', 'general'),
            'industry': summary.get('industry_classification', 'general'),
            'content_grade': summary.get('content_quality_grade', 'C'),
            'technical_grade': summary.get('technical_performance_grade', 'C'),
            'competitive_position': summary.get('competitive_position', 'unknown'),
            'top_3_priorities': summary.get('top_recommendations', [])[:3],
            'key_strengths': summary.get('key_strengths', []),
            'critical_issues': summary.get('critical_issues', [])
        }
    
    elif format_type == 'action_plan':
        niche_roadmap = comprehensive_results.get('niche_analysis', {}).get('optimization_roadmap', [])
        competitive_recs = comprehensive_results.get('competitive_intelligence', {}).get('strategic_recommendations', [])
        
        return {
            'immediate_actions': summary.get('critical_issues', []),
            'short_term_goals': [task for phase in niche_roadmap if phase.get('timeframe') == '0-30 days' for task in phase.get('tasks', [])][:5],
            'medium_term_goals': [task for phase in niche_roadmap if phase.get('timeframe') == '30-60 days' for task in phase.get('tasks', [])][:5],
            'long_term_strategy': [rec.get('title', '') for rec in competitive_recs if rec.get('timeframe', '').endswith('months')][:3],
            'success_metrics': comprehensive_results.get('niche_analysis', {}).get('success_metrics', [])[:5]
        }
    
    # Default: detailed report
    return comprehensive_results

# Performance monitoring

def log_analysis_performance(comprehensive_results: Dict[str, Any]):
    """Log performance metrics for the enhanced analysis."""
    
    metadata = comprehensive_results.get('analysis_metadata', {})
    components_used = metadata.get('components_used', [])
    timestamp = metadata.get('timestamp', time.time())
    
    logger.info(f"📊 Enhanced Analysis Performance Summary:")
    logger.info(f"   Components: {', '.join(components_used)}")
    logger.info(f"   Analysis time: {time.time() - timestamp:.2f} seconds")
    
    summary = comprehensive_results.get('summary', {})
    logger.info(f"   Overall Score: {summary.get('overall_score', 0)}/100")
    logger.info(f"   Content Grade: {summary.get('content_quality_grade', 'N/A')}")
    logger.info(f"   Technical Grade: {summary.get('technical_performance_grade', 'N/A')}")
    logger.info(f"   Website Type: {summary.get('primary_website_type', 'unknown')}")
    logger.info(f"   Industry: {summary.get('industry_classification', 'unknown')}")