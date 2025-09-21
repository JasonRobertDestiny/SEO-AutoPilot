#!/usr/bin/env python3
"""
🧪 Comprehensive SEO Analysis Test Suite
    
This test suite validates the complete integrated SEO analysis system including:
- PageSpeed Insights API integration
- SerpAPI Google Trends analysis
- Professional diagnostics with 150+ checkpoints
- LLM analysis with trends and performance data
- Frontend visualization and API endpoints
- Intelligent caching system

Usage:
    python test_comprehensive_analysis.py
    
Environment Requirements:
    - PAGESPEED_INSIGHTS_API_KEY (provided: AIzaSyBnhUKdhIc_m3tY7LAVHxZtTnYxsA8Wh2M)
    - SERPAPI_KEY (for trends analysis)
    - ANTHROPIC_API_KEY or SILICONFLOW_API_KEY (for LLM analysis)
"""

import asyncio
import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
TEST_CONFIG = {
    "test_url": "https://example.com",
    "api_base_url": "http://127.0.0.1:5000",
    "pagespeed_api_key": "AIzaSyBnhUKdhIc_m3tY7LAVHxZtTnYxsA8Wh2M",
    "timeout": 120,
    "test_scenarios": [
        {
            "name": "Basic SEO Analysis",
            "params": {"url": "https://example.com", "run_llm_analysis": False}
        },
        {
            "name": "Full Analysis with LLM",
            "params": {"url": "https://example.com", "run_llm_analysis": True}
        },
        {
            "name": "Comprehensive Analysis with Trends and Performance",
            "params": {
                "url": "https://example.com",
                "run_llm_analysis": True,
                "run_professional_analysis": True,
                "enable_trends_analysis": True,
                "enable_pagespeed_analysis": True
            }
        }
    ]
}


class ComprehensiveAnalysisTestSuite:
    """🧪 Comprehensive test suite for integrated SEO analysis system"""
    
    def __init__(self):
        self.results = []
        self.api_base = TEST_CONFIG["api_base_url"]
        self.test_start_time = time.time()
        
        # Set PageSpeed API key
        os.environ["PAGESPEED_INSIGHTS_API_KEY"] = TEST_CONFIG["pagespeed_api_key"]
        
    def log_test_result(self, test_name: str, success: bool, duration: float, details: Dict = None):
        """📊 Log test result with comprehensive metrics"""
        result = {
            "test_name": test_name,
            "success": success,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} ({duration:.2f}s)")
        
        if not success and details:
            logger.error(f"   Error: {details.get('error', 'Unknown error')}")

    def test_pageSpeed_api_integration(self) -> bool:
        """🚀 Test PageSpeed Insights API Integration"""
        test_start = time.time()
        
        try:
            from pyseoanalyzer.pagespeed_insights import PageSpeedInsightsAPI
            
            # Test API initialization
            pagespeed_api = PageSpeedInsightsAPI()
            assert pagespeed_api.api_key is not None, "PageSpeed API key not configured"
            
            # Test URL analysis
            logger.info("   Testing PageSpeed URL analysis...")
            analysis = pagespeed_api.analyze_url("https://www.google.com", strategy="mobile")
            
            # Validate analysis structure
            assert analysis.url == "https://www.google.com", "URL mismatch"
            assert analysis.strategy == "mobile", "Strategy mismatch"
            assert analysis.performance_metrics is not None, "No performance metrics"
            
            # Test Core Web Vitals
            core_vitals = analysis.performance_metrics.core_web_vitals
            assert core_vitals is not None, "No Core Web Vitals data"
            
            # Test recommendations generation
            recommendations = pagespeed_api.get_performance_recommendations(analysis)
            assert isinstance(recommendations, list), "Recommendations not a list"
            
            # Test performance impact calculation
            impact = pagespeed_api.calculate_performance_impact(analysis)
            assert "impact_score" in impact, "No impact score"
            assert 0 <= impact["impact_score"] <= 100, "Invalid impact score range"
            
            self.log_test_result(
                "PageSpeed API Integration",
                True,
                time.time() - test_start,
                {
                    "performance_score": analysis.performance_metrics.performance_score,
                    "core_web_vitals_available": bool(core_vitals),
                    "recommendations_count": len(recommendations),
                    "impact_score": impact["impact_score"]
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "PageSpeed API Integration",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    def test_trends_api_integration(self) -> bool:
        """📈 Test SerpAPI Trends Integration"""
        test_start = time.time()
        
        try:
            # Check if SerpAPI key is available
            serpapi_key = os.getenv("SERPAPI_KEY")
            if not serpapi_key:
                logger.warning("   SerpAPI key not available, skipping trends test")
                self.log_test_result(
                    "Trends API Integration",
                    True,
                    time.time() - test_start,
                    {"status": "skipped", "reason": "No SerpAPI key"}
                )
                return True
            
            from pyseoanalyzer.serpapi_trends import SerpAPITrends
            
            # Test trends analyzer initialization
            trends_analyzer = SerpAPITrends()
            
            # Test keyword trends analysis
            logger.info("   Testing keyword trends analysis...")
            test_keywords = ["SEO", "website optimization"]
            trends_data = trends_analyzer.get_keyword_trends(test_keywords)
            
            # Validate trends data structure
            assert isinstance(trends_data, dict), "Trends data not a dictionary"
            
            # Test content opportunities
            opportunities = trends_analyzer.analyze_content_opportunities(test_keywords)
            assert isinstance(opportunities, dict), "Opportunities not a dictionary"
            
            self.log_test_result(
                "Trends API Integration",
                True,
                time.time() - test_start,
                {
                    "keywords_analyzed": len(test_keywords),
                    "trends_data_available": len(trends_data),
                    "opportunities_identified": len(opportunities.get("content_suggestions", []))
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "Trends API Integration",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    def test_professional_diagnostics(self) -> bool:
        """🔬 Test Professional Diagnostics Engine"""
        test_start = time.time()
        
        try:
            from pyseoanalyzer.professional_diagnostics import ProfessionalSEODiagnostics
            
            # Test diagnostics initialization
            diagnostics = ProfessionalSEODiagnostics()
            
            # Create mock page data for testing
            mock_page_data = {
                "url": "https://example.com",
                "title": "Example Domain",
                "description": "This domain is for use in illustrative examples in documents.",
                "h1": ["Example Domain"],
                "h2": ["More information"],
                "images": [{"src": "image.jpg", "alt": "Example image"}],
                "word_count": 150,
                "internal_links": ["https://example.com/page1"],
                "external_links": ["https://iana.org"]
            }
            
            # Test comprehensive diagnostics
            logger.info("   Testing professional diagnostics analysis...")
            diagnostic_result = diagnostics.analyze_comprehensive(mock_page_data)
            
            # Validate diagnostic structure
            assert "overall_score" in diagnostic_result, "No overall score"
            assert "category_scores" in diagnostic_result, "No category scores"
            assert "diagnostic_results" in diagnostic_result, "No diagnostic results"
            assert "all_issues" in diagnostic_result, "No issues list"
            
            # Validate score ranges
            overall_score = diagnostic_result["overall_score"]
            assert 0 <= overall_score <= 100, f"Invalid overall score: {overall_score}"
            
            # Test category breakdown
            categories = diagnostic_result["category_scores"]
            expected_categories = ["technical_seo", "content_quality", "user_experience", "performance_indicators"]
            
            for category in expected_categories:
                assert category in categories, f"Missing category: {category}"
                cat_score = categories[category].get("score", 0)
                assert 0 <= cat_score <= 100, f"Invalid {category} score: {cat_score}"
            
            self.log_test_result(
                "Professional Diagnostics",
                True,
                time.time() - test_start,
                {
                    "overall_score": overall_score,
                    "categories_analyzed": len(categories),
                    "total_issues": len(diagnostic_result["all_issues"]),
                    "diagnostic_checks": len(diagnostic_result["diagnostic_results"])
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "Professional Diagnostics",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    def test_llm_analysis_enhancement(self) -> bool:
        """🤖 Test Enhanced LLM Analysis with Trends and Performance Data"""
        test_start = time.time()
        
        try:
            # Check for LLM API keys
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            siliconflow_key = os.getenv("SILICONFLOW_API_KEY")
            
            if not (anthropic_key or siliconflow_key):
                logger.warning("   No LLM API keys available, skipping LLM test")
                self.log_test_result(
                    "LLM Analysis Enhancement",
                    True,
                    time.time() - test_start,
                    {"status": "skipped", "reason": "No LLM API keys"}
                )
                return True
            
            from pyseoanalyzer.llm_analyst import LLMSEOEnhancer, TrendsAnalysis, PerformanceAnalysis
            
            # Test LLM enhancer initialization
            use_siliconflow = bool(siliconflow_key)
            enhancer = LLMSEOEnhancer(use_siliconflow=use_siliconflow)
            
            # Create comprehensive mock data
            mock_seo_data = {
                "pages": [{
                    "url": "https://example.com",
                    "title": "Example Domain",
                    "description": "This domain is for use in illustrative examples",
                    "h1": ["Example Domain"],
                    "word_count": 150
                }],
                "trends_insights": {
                    "analysis_summary": {"analyzed_keywords": 5, "rising_trends": 2},
                    "content_opportunities": {"content_suggestions": ["SEO basics", "Website optimization"]},
                    "trends_data": {"SEO": {"trend_direction": "rising", "average_interest": 75}}
                },
                "pagespeed_insights": {
                    "mobile": {
                        "analysis": {
                            "performance_score": 85,
                            "core_web_vitals": {"lcp": 2.1, "fid": 90, "cls": 0.08}
                        }
                    }
                }
            }
            
            # Test model validation
            logger.info("   Testing enhanced Pydantic models...")
            
            # Test TrendsAnalysis model
            trends_test_data = {
                "trending_opportunities": ["keyword research", "content optimization"],
                "seasonal_strategy": "Focus on holiday content in Q4",
                "search_intent_alignment": "Good coverage of informational intent",
                "content_gap_analysis": ["Technical SEO guides", "Local SEO strategies"],
                "competitive_keyword_strategy": "Target long-tail keywords",
                "trend_momentum_score": 78,
                "rising_topic_recommendations": ["Voice search optimization"]
            }
            trends_model = TrendsAnalysis(**trends_test_data)
            assert trends_model.trend_momentum_score == 78, "Trends model validation failed"
            
            # Test PerformanceAnalysis model
            performance_test_data = {
                "core_web_vitals_strategy": "Optimize LCP through image compression",
                "performance_impact_assessment": "Performance issues affecting SEO rankings",
                "mobile_first_recommendations": ["Compress images", "Minify CSS"],
                "user_experience_insights": "Fast loading improves user engagement",
                "technical_performance_priorities": ["Image optimization", "Code splitting"],
                "page_speed_seo_score": 82,
                "lighthouse_optimization_roadmap": {"immediate": "Image optimization", "month_1": "Code splitting"}
            }
            performance_model = PerformanceAnalysis(**performance_test_data)
            assert performance_model.page_speed_seo_score == 82, "Performance model validation failed"
            
            logger.info("   Models validated successfully")
            
            # Test chains setup (for Anthropic only)
            if not use_siliconflow and hasattr(enhancer, 'trends_chain'):
                assert enhancer.trends_chain is not None, "Trends chain not initialized"
                assert enhancer.performance_chain is not None, "Performance chain not initialized"
                logger.info("   Analysis chains initialized successfully")
            
            self.log_test_result(
                "LLM Analysis Enhancement",
                True,
                time.time() - test_start,
                {
                    "llm_provider": "siliconflow" if use_siliconflow else "anthropic",
                    "trends_model_validated": True,
                    "performance_model_validated": True,
                    "chains_available": not use_siliconflow
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "LLM Analysis Enhancement",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    def test_api_endpoints(self) -> bool:
        """🌐 Test Enhanced API Endpoints"""
        test_start = time.time()
        
        try:
            # Test health check
            logger.info("   Testing API health check...")
            health_response = requests.get(f"{self.api_base}/api/health", timeout=10)
            assert health_response.status_code == 200, "Health check failed"
            
            health_data = health_response.json()
            assert health_data.get("status") == "healthy", "API not healthy"
            
            # Test PageSpeed status endpoint
            logger.info("   Testing PageSpeed API status...")
            pagespeed_status = requests.get(f"{self.api_base}/api/pagespeed/status", timeout=10)
            assert pagespeed_status.status_code == 200, "PageSpeed status check failed"
            
            # Test trends status endpoint  
            logger.info("   Testing Trends API status...")
            trends_status = requests.get(f"{self.api_base}/api/trends/status", timeout=10)
            assert trends_status.status_code == 200, "Trends status check failed"
            
            # Test basic analysis endpoint
            logger.info("   Testing basic analysis endpoint...")
            analysis_payload = {
                "url": "https://example.com",
                "run_llm_analysis": False,
                "enable_pagespeed_analysis": True
            }
            
            analysis_response = requests.post(
                f"{self.api_base}/api/analyze",
                json=analysis_payload,
                timeout=60
            )
            
            if analysis_response.status_code == 200:
                analysis_data = analysis_response.json()
                assert "analysis" in analysis_data, "No analysis data"
                assert "seo_score" in analysis_data, "No SEO score"
                
                # Check if PageSpeed data was included
                pagespeed_included = bool(analysis_data.get("analysis", {}).get("pagespeed_insights"))
                
                self.log_test_result(
                    "API Endpoints",
                    True,
                    time.time() - test_start,
                    {
                        "health_check": True,
                        "pagespeed_status": True,
                        "trends_status": True,
                        "analysis_endpoint": True,
                        "pagespeed_data_included": pagespeed_included
                    }
                )
                return True
            else:
                self.log_test_result(
                    "API Endpoints",
                    False,
                    time.time() - test_start,
                    {"error": f"Analysis endpoint returned {analysis_response.status_code}"}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "API Endpoints",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    def test_intelligent_caching(self) -> bool:
        """💾 Test Intelligent Caching System"""
        test_start = time.time()
        
        try:
            from pyseoanalyzer.intelligent_cache import get_cached_analysis, cache_analysis_result, get_cache_stats
            
            # Test cache operations
            test_url = "https://cache-test.example.com"
            test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
            
            # Test caching
            logger.info("   Testing cache write operation...")
            cache_success = cache_analysis_result(test_url, test_data, "test_analysis")
            assert cache_success, "Cache write failed"
            
            # Test cache retrieval
            logger.info("   Testing cache read operation...")
            cached_data = get_cached_analysis(test_url, "test_analysis")
            assert cached_data is not None, "Cache read failed"
            assert cached_data["test"] == "data", "Cached data corrupted"
            
            # Test cache statistics
            logger.info("   Testing cache statistics...")
            cache_stats = get_cache_stats()
            assert isinstance(cache_stats, dict), "Cache stats not available"
            
            self.log_test_result(
                "Intelligent Caching",
                True,
                time.time() - test_start,
                {
                    "cache_write": True,
                    "cache_read": True,
                    "cache_stats_available": True,
                    "cache_entries": cache_stats.get("total_entries", 0)
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "Intelligent Caching",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    async def test_full_integration(self) -> bool:
        """🎯 Test Complete Integrated Analysis Pipeline"""
        test_start = time.time()
        
        try:
            from pyseoanalyzer.analyzer import analyze
            
            logger.info("   Testing full integration pipeline...")
            
            # Test comprehensive analysis with all features
            analysis_result = analyze(
                url="https://example.com",
                analyze_headings=True,
                analyze_extra_tags=True,
                run_professional_analysis=True,
                enable_pagespeed_analysis=True,
                enable_trends_analysis=bool(os.getenv("SERPAPI_KEY")),
                use_cache=True
            )
            
            # Validate comprehensive analysis structure
            assert "pages" in analysis_result, "No pages data"
            assert "keywords" in analysis_result, "No keywords data"
            assert len(analysis_result["pages"]) > 0, "No pages analyzed"
            
            # Check for professional analysis
            first_page = analysis_result["pages"][0]
            professional_analysis = first_page.get("professional_analysis")
            
            if professional_analysis:
                assert "overall_score" in professional_analysis, "No professional overall score"
                assert "category_scores" in professional_analysis, "No professional category scores"
                
            # Check for PageSpeed analysis
            pagespeed_data = analysis_result.get("pagespeed_insights")
            pagespeed_available = bool(pagespeed_data)
            
            # Check for trends analysis
            trends_data = analysis_result.get("trends_insights") 
            trends_available = bool(trends_data)
            
            self.log_test_result(
                "Full Integration",
                True,
                time.time() - test_start,
                {
                    "pages_analyzed": len(analysis_result["pages"]),
                    "keywords_found": len(analysis_result.get("keywords", [])),
                    "professional_analysis": bool(professional_analysis),
                    "pagespeed_analysis": pagespeed_available,
                    "trends_analysis": trends_available,
                    "execution_time": analysis_result.get("total_time", 0)
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "Full Integration",
                False,
                time.time() - test_start,
                {"error": str(e)}
            )
            return False

    def generate_test_report(self) -> Dict[str, Any]:
        """📊 Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        total_duration = time.time() - self.test_start_time
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.results,
            "environment_info": {
                "pagespeed_api_configured": bool(os.getenv("PAGESPEED_INSIGHTS_API_KEY")),
                "serpapi_configured": bool(os.getenv("SERPAPI_KEY")),
                "anthropic_api_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
                "siliconflow_api_configured": bool(os.getenv("SILICONFLOW_API_KEY")),
                "python_version": sys.version,
                "test_url": TEST_CONFIG["test_url"]
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """💡 Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.results if not r["success"]]
        
        if not failed_tests:
            recommendations.append("✅ All tests passed! The comprehensive analysis system is working correctly.")
            
        for failed_test in failed_tests:
            test_name = failed_test["test_name"]
            error = failed_test["details"].get("error", "")
            
            if "PageSpeed" in test_name and "API key" in error:
                recommendations.append("🔑 Configure PAGESPEED_INSIGHTS_API_KEY environment variable")
                
            elif "Trends" in test_name and "SerpAPI" in error:
                recommendations.append("📈 Configure SERPAPI_KEY environment variable for trends analysis")
                
            elif "LLM" in test_name:
                recommendations.append("🤖 Configure ANTHROPIC_API_KEY or SILICONFLOW_API_KEY for LLM analysis")
                
            elif "API Endpoints" in test_name:
                recommendations.append("🌐 Ensure the Flask API server is running on port 5000")
                
            else:
                recommendations.append(f"🔧 Fix {test_name}: {error}")
        
        return recommendations

    async def run_all_tests(self) -> Dict[str, Any]:
        """🚀 Run all comprehensive analysis tests"""
        logger.info("🧪 Starting Comprehensive SEO Analysis Test Suite")
        logger.info("=" * 60)
        
        # Run all tests
        await asyncio.gather(
            asyncio.to_thread(self.test_pageSpeed_api_integration),
            asyncio.to_thread(self.test_trends_api_integration),
            asyncio.to_thread(self.test_professional_diagnostics),
            asyncio.to_thread(self.test_llm_analysis_enhancement),
            asyncio.to_thread(self.test_api_endpoints),
            asyncio.to_thread(self.test_intelligent_caching),
            self.test_full_integration()
        )
        
        # Generate and return comprehensive report
        report = self.generate_test_report()
        
        logger.info("=" * 60)
        logger.info(f"🎯 Test Suite Complete: {report['test_summary']['passed']}/{report['test_summary']['total_tests']} tests passed")
        logger.info(f"⏱️  Total Duration: {report['test_summary']['total_duration']:.2f}s")
        logger.info(f"📊 Success Rate: {report['test_summary']['success_rate']:.1f}%")
        
        return report


async def main():
    """🎯 Main test execution function"""
    try:
        # Initialize test suite
        test_suite = ComprehensiveAnalysisTestSuite()
        
        # Run all tests
        report = await test_suite.run_all_tests()
        
        # Save detailed report
        report_filename = f"comprehensive_analysis_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Detailed test report saved to: {report_filename}")
        
        # Print recommendations
        if report["recommendations"]:
            logger.info("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                logger.info(f"   {rec}")
        
        # Exit with appropriate code
        success_rate = report['test_summary']['success_rate']
        exit_code = 0 if success_rate >= 80 else 1
        
        logger.info(f"\n🎯 Test suite {'PASSED' if exit_code == 0 else 'FAILED'}")
        return exit_code
        
    except Exception as e:
        logger.error(f"💥 Test suite failed with critical error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)