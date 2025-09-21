import time
from operator import itemgetter
from .website import Website
from .seo_optimizer import enhance_analysis_with_optimization
from .google_integrator import GoogleDataIntegrator
from .intelligent_cache import get_cached_analysis, cache_analysis_result


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
    use_cache=True,  # Enable caching by default
):
    """
    🚀 Enhanced SEO analysis with intelligent caching
    
    Args:
        url: Website URL to analyze
        sitemap_url: Optional sitemap URL
        analyze_headings: Enable heading analysis
        analyze_extra_tags: Enable extra tag analysis
        follow_links: Enable link following
        run_llm_analysis: Enable LLM analysis
        run_professional_analysis: Enable professional diagnostics
        enable_google_integration: Enable Google API integration
        use_cache: Enable intelligent caching (default: True)
    
    Returns:
        Enhanced analysis results with caching support
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
            'enable_google_integration': enable_google_integration
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
            'enable_google_integration': enable_google_integration
        }
        
        # Cache the result for future use
        cache_success = cache_analysis_result(url, enhanced_output, 'full_analysis', **cache_params)
        if cache_success:
            print(f"💾 Cached analysis result for {url}")
        else:
            print(f"⚠️ Failed to cache analysis result for {url}")
    
    return enhanced_output
