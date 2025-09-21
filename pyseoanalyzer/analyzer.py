import time
from operator import itemgetter
from .website import Website
from .seo_optimizer import enhance_analysis_with_optimization
from .google_integrator import GoogleDataIntegrator
from .intelligent_cache import get_cached_analysis, cache_analysis_result
from .serpapi_trends import SerpAPITrends
from .pagespeed_insights import PageSpeedInsightsAPI


def calc_total_time(start_time):
    return time.time() - start_time


def analyze(
    url,
    sitemap_url=None,
    analyze_headings=False,
    analyze_extra_tags=False,
    follow_links=True,
    run_llm_analysis=False,
    run_professional_analysis=True,
    enable_google_integration=False,
    enable_trends_analysis=False,
    enable_pagespeed_analysis=False,
    use_cache=True,  # Enable caching by default
):
    """
    🚀 Enhanced SEO analysis with intelligent caching, trends, and PageSpeed integration
    
    Args:
        url: Website URL to analyze
        sitemap_url: Optional sitemap URL
        analyze_headings: Enable heading analysis
        analyze_extra_tags: Enable extra tag analysis
        follow_links: Enable link following
        run_llm_analysis: Enable LLM analysis
        run_professional_analysis: Enable professional diagnostics
        enable_google_integration: Enable Google API integration
        enable_trends_analysis: Enable SerpAPI Google Trends analysis
        enable_pagespeed_analysis: Enable PageSpeed Insights API analysis
        use_cache: Enable intelligent caching (default: True)
    
    Returns:
        Enhanced analysis results with caching, trends, and performance support
    """
    start_time = time.time()
    
    # 🧠 Check cache first if enabled
    if use_cache:
        # Generate cache parameters based on analysis configuration
        cache_params = {
            'sitemap_url': sitemap_url,
            'analyze_headings': analyze_headings,
            'analyze_extra_tags': analyze_extra_tags,
            'follow_links': follow_links,
            'run_llm_analysis': run_llm_analysis,
            'run_professional_analysis': run_professional_analysis,
            'enable_google_integration': enable_google_integration,
            'enable_trends_analysis': enable_trends_analysis,
            'enable_pagespeed_analysis': enable_pagespeed_analysis
        }
        
        # Try to get cached result
        cached_result = get_cached_analysis(url, 'full_analysis', **cache_params)
        if cached_result:
            print(f"🎯 Cache HIT: Using cached analysis for {url}")
            return cached_result

    print(f"🔍 Cache MISS: Performing fresh analysis for {url}")

    output = {
        "pages": [],
        "keywords": [],
        "errors": [],
        "total_time": 0,  # Initialize to 0 before calculation
        "google_insights": None,
        "trends_insights": None,
        "pagespeed_insights": None,
    }

    site = Website(
        base_url=url,
        sitemap=sitemap_url,
        analyze_headings=analyze_headings,
        analyze_extra_tags=analyze_extra_tags,
        follow_links=follow_links,
        run_llm_analysis=run_llm_analysis,
        run_professional_analysis=run_professional_analysis,
    )

    site.crawl()

    for p in site.crawled_pages:
        output["pages"].append(p.as_dict())

    output["duplicate_pages"] = [
        list(site.content_hashes[p])
        for p in site.content_hashes
        if len(site.content_hashes[p]) > 1
    ]

    sorted_words = sorted(site.wordcount.items(), key=itemgetter(1), reverse=True)
    sorted_bigrams = sorted(site.bigrams.items(), key=itemgetter(1), reverse=True)
    sorted_trigrams = sorted(site.trigrams.items(), key=itemgetter(1), reverse=True)

    output["keywords"] = []

    for w in sorted_words:
        if w[1] > 1:  # Lower threshold to capture more keywords
            output["keywords"].append(
                {
                    "word": w[0],
                    "keyword": w[0],  # Add both formats for compatibility
                    "count": w[1],
                    "repeats": w[1],  # Add repeats for frontend compatibility
                    "density": round((w[1] / max(len(sorted_words), 1)) * 100, 2)
                }
            )

    for w, v in sorted_bigrams:
        if v > 1:  # Lower threshold
            output["keywords"].append(
                {
                    "word": w,
                    "keyword": w,
                    "count": v,
                    "repeats": v,
                    "density": round((v / max(len(sorted_bigrams), 1)) * 100, 2)
                }
            )

    for w, v in sorted_trigrams:
        if v > 1:  # Lower threshold
            output["keywords"].append(
                {
                    "word": w,
                    "keyword": w,
                    "count": v,
                    "repeats": v,
                    "density": round((v / max(len(sorted_trigrams), 1)) * 100, 2)
                }
            )

    # Sort one last time...
    output["keywords"] = sorted(
        output["keywords"], key=itemgetter("count"), reverse=True
    )
    
    # 🔥 Add Google Trends analysis if enabled
    if enable_trends_analysis and output["keywords"]:
        try:
            # Extract top keywords for trends analysis
            top_keywords = [kw["keyword"] for kw in output["keywords"][:10]]  # Top 10 keywords
            
            trends_analyzer = SerpAPITrends()
            trends_data = trends_analyzer.get_keyword_trends(top_keywords)
            content_opportunities = trends_analyzer.analyze_content_opportunities(top_keywords)
            
            # Enhance keywords with trends data
            for keyword_obj in output["keywords"]:
                keyword = keyword_obj["keyword"]
                if keyword in trends_data:
                    trend_info = trends_data[keyword]
                    keyword_obj["trend_data"] = {
                        "average_interest": trend_info.average_interest,
                        "trend_direction": trend_info.trend_direction,
                        "related_queries_count": len(trend_info.related_queries),
                        "rising_queries_count": len(trend_info.rising_queries),
                        "peak_periods": len(trend_info.peak_periods)
                    }
            
            # Add comprehensive trends insights
            output["trends_insights"] = {
                "analysis_summary": {
                    "analyzed_keywords": len(trends_data),
                    "rising_trends": len([t for t in trends_data.values() if t.trend_direction == "rising"]),
                    "falling_trends": len([t for t in trends_data.values() if t.trend_direction == "falling"]),
                    "stable_trends": len([t for t in trends_data.values() if t.trend_direction == "stable"])
                },
                "content_opportunities": content_opportunities,
                "trends_data": {k: {
                    "keyword": v.keyword,
                    "average_interest": v.average_interest,
                    "trend_direction": v.trend_direction,
                    "related_topics_count": len(v.related_topics),
                    "related_queries_count": len(v.related_queries),
                    "rising_queries_count": len(v.rising_queries),
                    "peak_periods_count": len(v.peak_periods)
                } for k, v in trends_data.items()}
            }
            
            print(f"🔥 Trends analysis completed for {len(trends_data)} keywords")
            
        except Exception as e:
            output["errors"].append(f"Trends analysis failed: {str(e)}")
            print(f"⚠️ Trends analysis error: {str(e)}")

    # 🚀 Add PageSpeed Insights analysis if enabled
    if enable_pagespeed_analysis:
        try:
            print(f"🚀 Starting PageSpeed Insights analysis for {url}")
            
            pagespeed_api = PageSpeedInsightsAPI()
            
            # Analyze both mobile and desktop performance
            mobile_analysis = pagespeed_api.analyze_url(url, strategy="mobile")
            desktop_analysis = pagespeed_api.analyze_url(url, strategy="desktop")
            
            # Get performance recommendations
            mobile_recommendations = pagespeed_api.get_performance_recommendations(mobile_analysis)
            desktop_recommendations = pagespeed_api.get_performance_recommendations(desktop_analysis)
            
            # Calculate performance impact
            mobile_impact = pagespeed_api.calculate_performance_impact(mobile_analysis)
            desktop_impact = pagespeed_api.calculate_performance_impact(desktop_analysis)
            
            # Combine insights
            output["pagespeed_insights"] = {
                "mobile": {
                    "analysis": {
                        "url": mobile_analysis.url,
                        "strategy": mobile_analysis.strategy,
                        "performance_score": mobile_analysis.performance_metrics.performance_score if mobile_analysis.performance_metrics else None,
                        "seo_score": mobile_analysis.performance_metrics.seo_score if mobile_analysis.performance_metrics else None,
                        "accessibility_score": mobile_analysis.performance_metrics.accessibility_score if mobile_analysis.performance_metrics else None,
                        "best_practices_score": mobile_analysis.performance_metrics.best_practices_score if mobile_analysis.performance_metrics else None,
                        "core_web_vitals": {
                            "lcp": mobile_analysis.performance_metrics.core_web_vitals.largest_contentful_paint if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                            "fid": mobile_analysis.performance_metrics.core_web_vitals.first_input_delay if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                            "cls": mobile_analysis.performance_metrics.core_web_vitals.cumulative_layout_shift if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                            "fcp": mobile_analysis.performance_metrics.core_web_vitals.first_contentful_paint if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                            "si": mobile_analysis.performance_metrics.core_web_vitals.speed_index if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                            "tti": mobile_analysis.performance_metrics.core_web_vitals.time_to_interactive if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                            "tbt": mobile_analysis.performance_metrics.core_web_vitals.total_blocking_time if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None
                        },
                        "lighthouse_version": mobile_analysis.lighthouse_version,
                        "fetch_time": mobile_analysis.fetch_time
                    },
                    "recommendations": mobile_recommendations,
                    "impact_assessment": mobile_impact,
                    "opportunities": mobile_analysis.performance_metrics.opportunities[:10] if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.opportunities else []
                },
                "desktop": {
                    "analysis": {
                        "url": desktop_analysis.url,
                        "strategy": desktop_analysis.strategy,
                        "performance_score": desktop_analysis.performance_metrics.performance_score if desktop_analysis.performance_metrics else None,
                        "seo_score": desktop_analysis.performance_metrics.seo_score if desktop_analysis.performance_metrics else None,
                        "accessibility_score": desktop_analysis.performance_metrics.accessibility_score if desktop_analysis.performance_metrics else None,
                        "best_practices_score": desktop_analysis.performance_metrics.best_practices_score if desktop_analysis.performance_metrics else None,
                        "core_web_vitals": {
                            "lcp": desktop_analysis.performance_metrics.core_web_vitals.largest_contentful_paint if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                            "fid": desktop_analysis.performance_metrics.core_web_vitals.first_input_delay if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                            "cls": desktop_analysis.performance_metrics.core_web_vitals.cumulative_layout_shift if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                            "fcp": desktop_analysis.performance_metrics.core_web_vitals.first_contentful_paint if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                            "si": desktop_analysis.performance_metrics.core_web_vitals.speed_index if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                            "tti": desktop_analysis.performance_metrics.core_web_vitals.time_to_interactive if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                            "tbt": desktop_analysis.performance_metrics.core_web_vitals.total_blocking_time if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None
                        },
                        "lighthouse_version": desktop_analysis.lighthouse_version,
                        "fetch_time": desktop_analysis.fetch_time
                    },
                    "recommendations": desktop_recommendations,
                    "impact_assessment": desktop_impact,
                    "opportunities": desktop_analysis.performance_metrics.opportunities[:10] if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.opportunities else []
                },
                "summary": {
                    "mobile_performance_score": mobile_analysis.performance_metrics.performance_score if mobile_analysis.performance_metrics else None,
                    "desktop_performance_score": desktop_analysis.performance_metrics.performance_score if desktop_analysis.performance_metrics else None,
                    "average_performance_score": (
                        (mobile_analysis.performance_metrics.performance_score or 0) + 
                        (desktop_analysis.performance_metrics.performance_score or 0)
                    ) / 2 if mobile_analysis.performance_metrics and desktop_analysis.performance_metrics else None,
                    "core_web_vitals_pass": mobile_impact.get("core_web_vitals_pass", False),
                    "seo_critical_issues": mobile_impact.get("seo_critical", False) or desktop_impact.get("seo_critical", False),
                    "total_recommendations": len(mobile_recommendations) + len(desktop_recommendations),
                    "high_priority_recommendations": len([r for r in mobile_recommendations + desktop_recommendations if r.get("priority") == "high"])
                }
            }
            
            print(f"🚀 PageSpeed analysis completed - Mobile: {mobile_analysis.performance_metrics.performance_score if mobile_analysis.performance_metrics else 'N/A'}/100, Desktop: {desktop_analysis.performance_metrics.performance_score if desktop_analysis.performance_metrics else 'N/A'}/100")
            
        except Exception as e:
            output["errors"].append(f"PageSpeed analysis failed: {str(e)}")
            print(f"⚠️ PageSpeed analysis error: {str(e)}")

    output["total_time"] = calc_total_time(start_time)

    # 添加SEO优化建议
    enhanced_output = enhance_analysis_with_optimization(output)
    
    # 如果启用Google集成，添加Google数据洞察
    if enable_google_integration:
        try:
            import os
            analytics_view_id = os.getenv('GOOGLE_ANALYTICS_VIEW_ID')
            analytics_measurement_id = os.getenv('GOOGLE_ANALYTICS_MEASUREMENT_ID')
            search_console_url = os.getenv('GOOGLE_SEARCH_CONSOLE_URL')
            
            if (analytics_view_id or analytics_measurement_id) and search_console_url:
                google_integrator = GoogleDataIntegrator()
                insights = google_integrator.get_seo_insights(
                    search_console_site_url=search_console_url,
                    analytics_view_id=analytics_view_id,
                    analytics_measurement_id=analytics_measurement_id
                )
                enhanced_output['google_insights'] = insights
            else:
                enhanced_output['errors'].append("Google integration requires GOOGLE_SEARCH_CONSOLE_URL and either GOOGLE_ANALYTICS_VIEW_ID or GOOGLE_ANALYTICS_MEASUREMENT_ID")
        except Exception as e:
            enhanced_output['errors'].append(f"Google integration failed: {str(e)}")
    
    # 💾 Cache the enhanced result if caching is enabled
    if use_cache and enhanced_output:
        cache_params = {
            'sitemap_url': sitemap_url,
            'analyze_headings': analyze_headings,
            'analyze_extra_tags': analyze_extra_tags,
            'follow_links': follow_links,
            'run_llm_analysis': run_llm_analysis,
            'run_professional_analysis': run_professional_analysis,
            'enable_google_integration': enable_google_integration,
            'enable_trends_analysis': enable_trends_analysis,
            'enable_pagespeed_analysis': enable_pagespeed_analysis
        }
        
        # Cache the result for future use
        cache_success = cache_analysis_result(url, enhanced_output, 'full_analysis', **cache_params)
        if cache_success:
            print(f"💾 Cached analysis result for {url}")
        else:
            print(f"⚠️ Failed to cache analysis result for {url}")
    
    return enhanced_output
