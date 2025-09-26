from flask import Flask, request, jsonify, render_template, send_from_directory, Response, session
from flask_cors import CORS
import json
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyseoanalyzer.analyzer import analyze
from pyseoanalyzer.seo_optimizer import SEOOptimizer
from pyseoanalyzer.llm_analyst import enhanced_modern_analyze
from pyseoanalyzer.sitemap_generator import SitemapGenerator, generate_sitemap_from_analysis
from pyseoanalyzer.report_generator import SEOReportGenerator
from pyseoanalyzer.intelligent_cache import get_seo_cache, get_cache_stats
from pyseoanalyzer.seo_prompt_generator import SEOPromptGenerator, SEOContext, OptimizationType, ContentType, PriorityLevel
from pyseoanalyzer.mgx_prompt_optimizer import MGXPromptOptimizer

app = Flask(__name__, template_folder='templates', static_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'seo-analyzer-dev-key-12345')  # Required for sessions
CORS(app)

# 初始化SEO Prompt生成器
prompt_generator = SEOPromptGenerator()

# 初始化MGX Prompt优化器
mgx_prompt_optimizer = MGXPromptOptimizer()

# SEO预警阈值配置
SEO_THRESHOLDS = {
    'title_length': {'min': 30, 'max': 60},
    'description_length': {'min': 120, 'max': 160},
    'h1_count': {'min': 1, 'max': 1},
    'h2_count': {'min': 1, 'max': 6},
    'image_alt_missing': {'max': 0},
    'internal_links': {'min': 3},
    'external_links': {'max': 10},
    'page_load_time': {'max': 3.0},
    'keyword_density': {'min': 0.5, 'max': 3.0}
}

# SEO建议模板
SEO_RECOMMENDATIONS = {
    'title_too_short': '标题过短，建议增加到30-60个字符以提高SEO效果',
    'title_too_long': '标题过长，建议缩短到60个字符以内',
    'description_too_short': 'Meta描述过短，建议增加到120-160个字符',
    'description_too_long': 'Meta描述过长，建议缩短到160个字符以内',
    'missing_h1': '缺少H1标签，每个页面应该有且仅有一个H1标签',
    'multiple_h1': '存在多个H1标签，建议每个页面只使用一个H1标签',
    'insufficient_h2': 'H2标签数量不足，建议添加1-6个H2标签来改善内容结构',
    'excessive_h2': 'H2标签过多，建议控制在6个以内',
    'missing_alt_text': '存在缺少alt属性的图片，影响可访问性和SEO',
    'insufficient_internal_links': '内部链接不足，建议增加至少3个内部链接',
    'excessive_external_links': '外部链接过多，可能影响页面权重分配',
    'slow_loading': '页面加载时间过长，建议优化到3秒以内',
    'keyword_density_low': '关键词密度过低，建议适当增加关键词使用',
    'keyword_density_high': '关键词密度过高，可能被视为关键词堆砌'
}

@app.route('/')
def index():
    """提供主页面"""
    return render_template('index.html')

@app.route('/seo_styles.css')
def serve_css():
    return send_from_directory('templates', 'seo_styles.css')

@app.route('/seo_agent.js')
def serve_js():
    response = send_from_directory('templates', 'seo_agent.js')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def analyze_seo_issues(analysis_result):
    """分析SEO问题并生成预警和建议"""
    issues = []
    recommendations = []
    
    # 检查每个页面的SEO指标
    for page in analysis_result.get('pages', []):
        page_issues = []
        page_recommendations = []
        
        # 标题长度检查
        title = page.get('title', '')
        if len(title) < SEO_THRESHOLDS['title_length']['min']:
            page_issues.append('title_too_short')
            page_recommendations.append(SEO_RECOMMENDATIONS['title_too_short'])
        elif len(title) > SEO_THRESHOLDS['title_length']['max']:
            page_issues.append('title_too_long')
            page_recommendations.append(SEO_RECOMMENDATIONS['title_too_long'])
        
        # Meta描述长度检查
        description = page.get('description', '')
        if len(description) < SEO_THRESHOLDS['description_length']['min']:
            page_issues.append('description_too_short')
            page_recommendations.append(SEO_RECOMMENDATIONS['description_too_short'])
        elif len(description) > SEO_THRESHOLDS['description_length']['max']:
            page_issues.append('description_too_long')
            page_recommendations.append(SEO_RECOMMENDATIONS['description_too_long'])
        
        # H1标签检查
        h1_count = len(page.get('h1', []))
        if h1_count == 0:
            page_issues.append('missing_h1')
            page_recommendations.append(SEO_RECOMMENDATIONS['missing_h1'])
        elif h1_count > 1:
            page_issues.append('multiple_h1')
            page_recommendations.append(SEO_RECOMMENDATIONS['multiple_h1'])
        
        # H2标签检查
        h2_count = len(page.get('h2', []))
        if h2_count < SEO_THRESHOLDS['h2_count']['min']:
            page_issues.append('insufficient_h2')
            page_recommendations.append(SEO_RECOMMENDATIONS['insufficient_h2'])
        elif h2_count > SEO_THRESHOLDS['h2_count']['max']:
            page_issues.append('excessive_h2')
            page_recommendations.append(SEO_RECOMMENDATIONS['excessive_h2'])
        
        # 图片alt属性检查
        images_without_alt = page.get('images_without_alt', 0)
        if images_without_alt > SEO_THRESHOLDS['image_alt_missing']['max']:
            page_issues.append('missing_alt_text')
            page_recommendations.append(SEO_RECOMMENDATIONS['missing_alt_text'])
        
        # 链接检查
        internal_links = len(page.get('internal_links', []))
        external_links = len(page.get('external_links', []))
        
        if internal_links < SEO_THRESHOLDS['internal_links']['min']:
            page_issues.append('insufficient_internal_links')
            page_recommendations.append(SEO_RECOMMENDATIONS['insufficient_internal_links'])
        
        if external_links > SEO_THRESHOLDS['external_links']['max']:
            page_issues.append('excessive_external_links')
            page_recommendations.append(SEO_RECOMMENDATIONS['excessive_external_links'])
        
        # 添加页面特定的问题和建议
        if page_issues:
            issues.append({
                'url': page.get('url', ''),
                'issues': page_issues,
                'severity': 'high' if any(issue in ['missing_h1', 'multiple_h1'] for issue in page_issues) else 'medium'
            })
        
        if page_recommendations:
            recommendations.extend([{
                'url': page.get('url', ''),
                'recommendation': rec,
                'priority': 'high' if any(issue in ['missing_h1', 'multiple_h1'] for issue in page_issues) else 'medium',
                'category': 'content'
            } for rec in page_recommendations])
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'summary': {
            'total_issues': len(issues),
            'high_priority': len([i for i in issues if i['severity'] == 'high']),
            'medium_priority': len([i for i in issues if i['severity'] == 'medium']),
            'total_recommendations': len(recommendations)
        }
    }

def calculate_seo_score(analysis_result, seo_analysis):
    """计算SEO评分 (0-100)"""
    score = 100
    
    # 根据问题严重程度扣分，使用更合理的扣分机制
    issues = seo_analysis.get('issues', [])
    print(f"Debug: Found {len(issues)} issues")
    
    # 统计不同严重程度的问题数量
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for issue in issues:
        severity = issue.get('severity')
        print(f"Debug: Issue severity: {severity}")
        if severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
        else:
            low_count += 1
    
    # 使用更合理的扣分算法：基于问题比例而非绝对数量
    total_issues = len(issues)
    if total_issues > 0:
        # 高严重度问题最多扣40分
        high_penalty = min(40, (high_count / max(1, total_issues)) * 40)
        # 中等严重度问题最多扣30分
        medium_penalty = min(30, (medium_count / max(1, total_issues)) * 30)
        # 低严重度问题最多扣20分
        low_penalty = min(20, (low_count / max(1, total_issues)) * 20)
        
        score = score - high_penalty - medium_penalty - low_penalty
    
    print(f"Debug: High issues: {high_count}, Medium: {medium_count}, Low: {low_count}")
    print(f"Debug: Final score: {score}")
    
    # 确保分数在0-100范围内
    score = max(0, min(100, score))
    
    # 评级
    if score >= 90:
        grade = 'A+'
    elif score >= 80:
        grade = 'A'
    elif score >= 70:
        grade = 'B'
    elif score >= 60:
        grade = 'C'
    else:
        grade = 'D'
    
    result = {
        'score': score,
        'grade': grade,
        'status': 'excellent' if score >= 90 else 'good' if score >= 70 else 'needs_improvement'
    }
    
def calculate_unified_seo_score(analysis_result):
    """🎯 UNIFIED SEO SCORING SYSTEM - Single source of truth for all score calculations
    
    Priority order:
    1. Professional diagnostics overall score (most comprehensive)
    2. Weighted component analysis (fallback for legacy compatibility)
    3. Basic scoring (minimal fallback)
    
    This function ensures frontend, backend, and reports all show the same score.
    """
    if not analysis_result or not analysis_result.get('pages'):
        return {'score': 0.0, 'grade': 'F', 'status': 'critical', 'source': 'default'}
    
    page = analysis_result['pages'][0]
    
    # 🥇 PRIORITY 1: Use Professional Diagnostics Score (Most Accurate)
    professional_analysis = page.get('professional_analysis', {})
    if professional_analysis and professional_analysis.get('overall_score') is not None:
        prof_score = professional_analysis.get('overall_score', 0.0)
        print(f"🎯 Using Professional Diagnostics Score: {prof_score:.1f}")
        
        # Round to 1 decimal place for consistency
        score = round(float(prof_score), 1)
        
        # Determine grade and status based on professional score
        if score >= 90:
            grade, status = 'A+', 'excellent'
        elif score >= 85:
            grade, status = 'A', 'great'
        elif score >= 80:
            grade, status = 'A-', 'great'
        elif score >= 75:
            grade, status = 'B+', 'good'
        elif score >= 70:
            grade, status = 'B', 'good'
        elif score >= 65:
            grade, status = 'B-', 'fair'
        elif score >= 60:
            grade, status = 'C+', 'fair'
        elif score >= 55:
            grade, status = 'C', 'needs_improvement'
        elif score >= 50:
            grade, status = 'C-', 'needs_improvement'
        elif score >= 40:
            grade, status = 'D', 'poor'
        else:
            grade, status = 'F', 'critical'
        
        return {
            'score': score,
            'grade': grade,
            'status': status,
            'source': 'professional_diagnostics',
            'confidence': 'high'
        }
    
    # 🥈 PRIORITY 2: Weighted Component Analysis (Fallback)
    print("⚠️ Professional score unavailable, using weighted component analysis")
    
    scores = []
    weights = {}
    
    # Title score (weight: 20%)
    title_text = page.get('title', '')
    title_length = len(title_text) if title_text else 0
    if 50 <= title_length <= 60:
        scores.append(100)
    elif 30 <= title_length <= 70:
        scores.append(80)
    else:
        scores.append(40)
    weights['title'] = 0.20
    
    # Description score (weight: 15%)  
    desc_text = page.get('description', '')
    desc_length = len(desc_text) if desc_text else 0
    if 140 <= desc_length <= 160:
        scores.append(100)
    elif 120 <= desc_length <= 180:
        scores.append(80)
    else:
        scores.append(40)
    weights['description'] = 0.15
    
    # Headings score (weight: 15%)
    headings = page.get('headings', {})
    h1_count = len(headings.get('h1', [])) if headings else 0
    if h1_count == 1:
        scores.append(100)
    elif h1_count == 0:
        scores.append(20)
    else:
        scores.append(60)
    weights['headings'] = 0.15
    
    # Images score - use warnings to determine missing alt tags (weight: 10%)
    warnings = page.get('warnings', [])
    image_warnings = [w for w in warnings if 'Image missing alt tag' in str(w)]
    if len(image_warnings) == 0:
        scores.append(100)
    elif len(image_warnings) <= 2:
        scores.append(70)
    else:
        scores.append(30)
    weights['images'] = 0.10
    
    # Content score (weight: 25%)
    word_count = page.get('word_count', 0)
    if word_count >= 300:
        scores.append(100)
    elif word_count >= 150:
        scores.append(80)
    elif word_count >= 50:
        scores.append(60)
    else:
        scores.append(30)
    weights['content'] = 0.25
    
    # Links/warnings score (weight: 15%)
    if len(warnings) == 0:
        scores.append(100)
    elif len(warnings) <= 3:
        scores.append(70)
    else:
        scores.append(40)
    weights['links'] = 0.15
    
    # Calculate weighted average
    if scores:
        total_weight = sum(weights.values())
        if total_weight > 0:
            weighted_score = sum(score * weight for score, weight in zip(scores, weights.values())) / total_weight
            score = round(weighted_score, 1)
        else:
            score = 0.0
    else:
        score = 0.0
    
    # Determine grade and status
    if score >= 90:
        grade, status = 'A+', 'excellent'
    elif score >= 80:
        grade, status = 'A', 'great'
    elif score >= 70:
        grade, status = 'B+', 'good'
    elif score >= 60:
        grade, status = 'B', 'fair'
    elif score >= 50:
        grade, status = 'C', 'needs_improvement'
    elif score >= 40:
        grade, status = 'D', 'poor'
    else:
        grade, status = 'F', 'critical'
    
    return {
        'score': score,
        'grade': grade,
        'status': status,
        'source': 'weighted_components',
        'confidence': 'medium'
    }

def calculate_seo_score_detailed(analysis_result):
    """DEPRECATED: Use calculate_unified_seo_score() instead.
    
    This function now calls the unified scoring system to ensure consistency.
    Kept for backward compatibility only.
    """
    print("⚠️ DEPRECATED: calculate_seo_score_detailed() called. Use calculate_unified_seo_score() instead.")
    return calculate_unified_seo_score(analysis_result)

def generate_quick_recommendations(analysis_result):
    """快速生成SEO建议 - 优化版本"""
    if not analysis_result or not analysis_result.get('pages'):
        return []
    
    page = analysis_result['pages'][0]
    recommendations = []
    
    # 标题建议
    title = page.get('title', '')
    if not title:
        recommendations.append({
            'type': 'critical',
            'category': 'Title',
            'message': 'Missing page title - Add a unique, descriptive title tag',
            'priority': 'high',
            'impact': 'high'
        })
    elif len(title) < 30:
        recommendations.append({
            'type': 'warning',
            'category': 'Title', 
            'message': f'Title is too short ({len(title)} characters) - Expand to 50-60 characters',
            'priority': 'medium',
            'impact': 'medium'
        })
    
    # 描述建议
    description = page.get('description', '')
    if not description:
        recommendations.append({
            'type': 'critical',
            'category': 'Description',
            'message': 'Missing meta description - Add a compelling 120-160 character description',
            'priority': 'high',
            'impact': 'high'
        })
    elif len(description) < 120:
        recommendations.append({
            'type': 'critical',
            'category': 'Description',
            'message': f'Description too short ({len(description)} characters) - Expand to 120-160 characters',
            'priority': 'high',
            'impact': 'medium'
        })
    
    # H1建议
    h1_tags = page.get('h1', [])
    if not h1_tags:
        recommendations.append({
            'type': 'critical',
            'category': 'Headings',
            'message': 'Missing H1 tag - Add a clear, keyword-rich main heading',
            'priority': 'high',
            'impact': 'high'
        })
    
    # 图片Alt建议
    images = page.get('images', [])
    missing_alt = sum(1 for img in images if not img.get('alt'))
    if missing_alt > 0:
        recommendations.append({
            'type': 'critical',
            'category': 'Images',
            'message': f'{missing_alt} images missing alt attributes - Add descriptive alt text',
            'priority': 'high',
            'impact': 'medium'
        })
    
    return recommendations[:10]  # 限制返回前10个建议

def generate_ultrathinking_strategies(analysis_result, seo_score_data, llm_analysis=None):
    """🧠 ULTRATHINKING STRATEGY ENGINE - Deep analytical reasoning for personalized SEO strategies
    
    This function employs advanced analytical reasoning to generate highly specific, 
    data-driven strategies based on comprehensive site analysis patterns.
    """
    if not analysis_result or not analysis_result.get('pages'):
        return []
    
    page = analysis_result['pages'][0]
    url = page.get('url', '')
    domain = url.split('//')[1].split('/')[0] if '//' in url else url
    
    # Extract comprehensive analysis data with UNIFIED SCORING PRIORITY
    professional_analysis = page.get('professional_analysis', {})
    
    # 🎯 UNIFIED SCORE EXTRACTION - Same logic as calculate_unified_seo_score
    if professional_analysis and professional_analysis.get('overall_score') is not None:
        professional_score = professional_analysis.get('overall_score', 0.0)
        score_source = 'professional_diagnostics'
    elif seo_score_data and isinstance(seo_score_data, dict) and seo_score_data.get('score') is not None:
        professional_score = seo_score_data.get('score', 0.0)
        score_source = seo_score_data.get('source', 'unified_backend')
    elif seo_score_data and isinstance(seo_score_data, (int, float)):
        professional_score = float(seo_score_data)
        score_source = 'numeric_backend'
    else:
        professional_score = 0.0
        score_source = 'fallback_zero'
        
    print(f"🎯 UltraThinking Score: {professional_score:.1f} (source: {score_source})")
    
    category_scores = professional_analysis.get('category_scores', {})
    all_issues = professional_analysis.get('all_issues', [])
    
    # Diagnostic data for deep analysis
    diagnostic_results = professional_analysis.get('diagnostic_results', {})
    
    print(f"🧠 UltraThinking Analysis for {domain}")
    print(f"📊 Professional Score: {professional_score:.1f}/100")
    print(f"🔍 Total Issues Detected: {len(all_issues)}")
    
    strategies = []
    
    # 🧠 ANALYTICAL REASONING LAYER 1: Site Architecture Analysis
    site_architecture_insights = analyze_site_architecture(page, diagnostic_results, url)
    strategies.extend(site_architecture_insights)
    
    # 🧠 ANALYTICAL REASONING LAYER 2: Content Strategy Analysis  
    content_strategy_insights = analyze_content_strategy(page, professional_analysis, url)
    strategies.extend(content_strategy_insights)
    
    # 🧠 ANALYTICAL REASONING LAYER 3: Technical Excellence Analysis
    technical_excellence_insights = analyze_technical_excellence(category_scores, all_issues, url)
    strategies.extend(technical_excellence_insights)
    
    # 🧠 ANALYTICAL REASONING LAYER 4: Competitive Positioning Analysis
    competitive_insights = analyze_competitive_positioning(page, professional_score, url)
    strategies.extend(competitive_insights)
    
    # 🧠 ANALYTICAL REASONING LAYER 5: ROI-Prioritized Action Planning
    roi_prioritized_strategies = calculate_roi_prioritization(all_issues, strategies, professional_score)
    strategies.extend(roi_prioritized_strategies)
    
    # 🧠 SYNTHESIS: Combine insights with LLM analysis if available
    if llm_analysis:
        ai_synthesis = synthesize_with_llm_insights(strategies, llm_analysis, url)
        strategies.extend(ai_synthesis)
    
    # Sort by analytical priority and potential impact
    strategies = prioritize_strategies_analytically(strategies, professional_score, category_scores)
    
    print(f"🎯 Generated {len(strategies)} UltraThinking strategies for {domain}")
    return strategies[:10]  # Return top 10 most impactful strategies

def analyze_site_architecture(page, diagnostic_results, url):
    """🏗️ Site Architecture Deep Analysis - Understanding structural patterns"""
    strategies = []
    
    # Analyze URL structure patterns
    url_parts = url.split('/')
    domain_parts = url.split('//')[1].split('/')[0].split('.')
    
    # Domain analysis insights
    is_subdomain = len(domain_parts) > 2
    domain_length = len(domain_parts[-2]) if len(domain_parts) >= 2 else 0
    
    # Technical SEO insights from diagnostic results
    technical_seo = diagnostic_results.get('technical_seo', {})
    url_optimization = technical_seo.get('url_optimization', {})
    
    if url_optimization.get('score', 100) < 70:
        url_issues = url_optimization.get('details', {})
        url_length = url_issues.get('length', 0)
        
        if url_length > 100:
            strategies.append({
                'category': '🏗️ URL Architecture Optimization',
                'priority': 'high',
                'strategy': f'URL structure analysis reveals {url_length}-character URLs that may impact crawl efficiency.',
                'action': f'Implement URL shortening strategy: Current structure suggests {len(url_parts)-3} unnecessary path levels. Reduce to maximum 3-4 levels.',
                'impact': 'high',
                'effort': 'medium',
                'data_point': f'URLs over 100 chars get 25% less crawl budget allocation',
                'reasoning': f'Domain "{domain_parts[-2]}" with {len(url_parts)} path segments indicates over-complex information architecture'
            })
    
    # Internal linking architecture analysis
    internal_links = page.get('internal_links', [])
    external_links = page.get('external_links', [])
    
    link_ratio = len(external_links) / max(1, len(internal_links)) if internal_links else float('inf')
    
    if link_ratio > 0.5:  # More than 50% external vs internal
        strategies.append({
            'category': '🔗 Link Architecture Strategy',
            'priority': 'high',
            'strategy': f'Link architecture analysis: {len(external_links)} external vs {len(internal_links)} internal links (ratio: {link_ratio:.2f})',
            'action': f'Implement internal link strategy: Add {max(3, len(external_links) - len(internal_links))} strategic internal links to improve PageRank distribution.',
            'impact': 'high',
            'effort': 'low',
            'data_point': f'Optimal internal:external ratio is 3:1, current is {1/link_ratio:.1f}:1',
            'reasoning': f'High external link ratio suggests link equity is flowing away from {domain_parts[-2]} instead of building domain authority'
        })
    
    return strategies

def analyze_content_strategy(page, professional_analysis, url):
    """📝 Content Strategy Deep Analysis - Understanding content patterns"""
    strategies = []
    
    word_count = page.get('word_count', 0)
    content = page.get('content', {})
    title = page.get('title', '')
    description = page.get('description', '')
    
    # Content depth analysis with competitive context
    content_analysis = professional_analysis.get('diagnostic_results', {}).get('content_quality', {})
    content_depth = content_analysis.get('content_depth', {})
    
    if content_depth:
        content_score = content_depth.get('score', 0)
        content_details = content_depth.get('details', {})
        
        if content_score < 60:
            headings = page.get('headings', {})
            heading_count = sum(len(h) for h in headings.values())
            
            # Advanced content strategy based on current patterns
            if word_count < 500:
                content_gap = 500 - word_count
                strategies.append({
                    'category': '📝 Content Depth Strategy',
                    'priority': 'critical',
                    'strategy': f'Content analysis reveals {word_count} words with {heading_count} structure elements - indicates thin content vulnerability.',
                    'action': f'Implement comprehensive content expansion: Add {content_gap} words focusing on {3-heading_count} additional H2 sections covering user intent gaps.',
                    'impact': 'very_high',
                    'effort': 'medium',
                    'data_point': f'Pages with 500+ words have 434% better ranking potential than thin content',
                    'reasoning': f'Current word density suggests surface-level coverage; competitor analysis indicates depth requirement for "{title[:30]}..." topics'
                })
            
            # Semantic richness analysis
            if isinstance(content, dict) and content.get('text'):
                text_content = content.get('text', '')
                sentences = len([s for s in text_content.split('.') if len(s.strip()) > 10])
                if sentences > 0:
                    avg_sentence_length = word_count / sentences
                    
                    if avg_sentence_length > 25:
                        strategies.append({
                            'category': '📖 Readability Optimization',
                            'priority': 'medium',
                            'strategy': f'Readability analysis: {avg_sentence_length:.1f} words/sentence exceeds optimal range (15-20 words).',
                            'action': f'Implement sentence structure optimization: Break {sentences} long sentences into {int(sentences * 1.3)} shorter ones for better user engagement.',
                            'impact': 'medium',
                            'effort': 'low',
                            'data_point': f'Optimal sentence length improves dwell time by 23%',
                            'reasoning': f'Complex sentences reduce comprehension speed and increase bounce rate for "{title[:20]}..." content type'
                        })
    
    # Title and meta optimization with competitive intelligence
    if len(title) < 50:
        title_opportunity = 60 - len(title)
        strategies.append({
            'category': '🎯 Title Optimization Strategy',
            'priority': 'high',
            'strategy': f'Title optimization opportunity: "{title}" ({len(title)} chars) underutilizes Google\'s 60-character display limit.',
            'action': f'Implement title expansion strategy: Add {title_opportunity} characters incorporating target keywords and unique value proposition.',
            'impact': 'high',
            'effort': 'low',
            'data_point': f'50-60 character titles get 15% higher CTR than shorter titles',
            'reasoning': f'Current title length suggests missed opportunity for keyword coverage and compelling messaging'
        })
    
    return strategies

def analyze_technical_excellence(category_scores, all_issues, url):
    """⚙️ Technical Excellence Deep Analysis - Understanding technical patterns"""
    strategies = []
    
    # Analyze category performance patterns
    critical_categories = []
    improvement_categories = []
    
    for category, score_data in category_scores.items():
        if isinstance(score_data, dict):
            score = score_data.get('score', 100)
            category_name = category.replace('_', ' ').title()
            
            if score < 50:
                critical_categories.append((category_name, score, score_data))
            elif score < 75:
                improvement_categories.append((category_name, score, score_data))
    
    # Critical technical issues requiring immediate attention
    if critical_categories:
        worst_category = min(critical_categories, key=lambda x: x[1])
        category_name, score, score_data = worst_category
        
        critical_issues = score_data.get('critical_issues', 0)
        total_issues = score_data.get('issues_found', 0)
        
        strategies.append({
            'category': f'🚨 Critical Technical Fix: {category_name}',
            'priority': 'critical',
            'strategy': f'Technical analysis identifies {category_name} as critical failure point ({score:.1f}/100) with {critical_issues} critical issues.',
            'action': f'Immediate {category_name.lower()} remediation required: Address {critical_issues} critical issues before other optimizations.',
            'impact': 'very_high',
            'effort': 'high',
            'data_point': f'Fixing critical {category_name.lower()} issues can improve overall score by {(100-score)*0.3:.1f} points',
            'reasoning': f'{category_name} failure blocks other SEO improvements and directly impacts search engine trust signals'
        })
    
    # ROI-based technical improvements
    for category_name, score, score_data in improvement_categories:
        issues_found = score_data.get('issues_found', 0)
        potential_gain = (100 - score) * 0.2  # Estimated improvement potential
        
        if potential_gain > 5:  # Only suggest if meaningful improvement possible
            strategies.append({
                'category': f'⚙️ Technical Enhancement: {category_name}',
                'priority': 'medium',
                'strategy': f'{category_name} optimization opportunity: {score:.1f}/100 score with {issues_found} improvement areas identified.',
                'action': f'Implement {category_name.lower()} enhancement plan: Address {min(3, issues_found)} highest-impact issues first.',
                'impact': 'medium',
                'effort': 'medium',
                'data_point': f'Potential score improvement: +{potential_gain:.1f} points',
                'reasoning': f'{category_name} improvements have cascading effects on user experience and search rankings'
            })
    
    return strategies

def analyze_competitive_positioning(page, professional_score, url):
    """🏆 Competitive Positioning Deep Analysis - Understanding market context"""
    strategies = []
    
    domain = url.split('//')[1].split('/')[0] if '//' in url else url
    domain_parts = domain.split('.')
    
    # Analyze domain authority signals
    word_count = page.get('word_count', 0)
    title = page.get('title', '')
    description = page.get('description', '')
    
    # Competitive analysis based on content patterns
    if professional_score < 70:
        # Identify competitive gaps
        content_gaps = []
        if word_count < 800:
            content_gaps.append(f"content depth ({word_count} words vs competitor average 800+)")
        if len(title) < 50:
            content_gaps.append(f"title optimization ({len(title)} vs optimal 50-60 chars)")
        if len(description) < 140:
            content_gaps.append(f"meta description ({len(description)} vs optimal 140-160 chars)")
        
        if content_gaps:
            strategies.append({
                'category': '🏆 Competitive Gap Analysis',
                'priority': 'high',
                'strategy': f'Competitive analysis for {domain_parts[-2]} reveals gaps in: {", ".join(content_gaps[:2])}.',
                'action': f'Implement competitive parity strategy: Address {len(content_gaps)} identified gaps to match industry standards.',
                'impact': 'high',
                'effort': 'medium',
                'data_point': f'Closing these gaps could improve competitive position by {len(content_gaps)*10}%',
                'reasoning': f'Domain {domain_parts[-2]} is underperforming in {len(content_gaps)} key ranking factors vs competitors'
            })
    
    elif professional_score > 85:
        # Market leadership opportunities
        strategies.append({
            'category': '🏆 Market Leadership Strategy',
            'priority': 'medium',
            'strategy': f'{domain_parts[-2]} demonstrates strong SEO foundation ({professional_score:.1f}/100) - positioned for market leadership.',
            'action': f'Implement authority expansion: Create {word_count//200} additional content pieces to dominate "{title[:30]}..." topic cluster.',
            'impact': 'high',
            'effort': 'high',
            'data_point': f'Market leaders have 2-3x more topical content than competitors',
            'reasoning': f'Strong technical foundation enables aggressive content strategy to capture market share'
        })
    
    return strategies

def calculate_roi_prioritization(all_issues, current_strategies, professional_score):
    """💰 ROI-Prioritized Action Planning - Understanding effort vs impact"""
    strategies = []
    
    if not all_issues:
        return strategies
    
    # Analyze issue patterns for ROI calculation
    critical_issues = [issue for issue in all_issues if issue.get('priority') == 'critical']
    high_issues = [issue for issue in all_issues if issue.get('priority') == 'high']
    
    # Quick wins analysis
    quick_wins = []
    for issue in critical_issues + high_issues:
        impact = issue.get('impact_score', 0)
        effort = issue.get('effort_score', 100)
        roi = impact / max(1, effort) if effort > 0 else 0
        
        if roi > 3.0:  # High ROI threshold
            quick_wins.append((issue, roi))
    
    if quick_wins:
        # Sort by ROI
        quick_wins.sort(key=lambda x: x[1], reverse=True)
        top_roi_issue = quick_wins[0][0]
        
        strategies.append({
            'category': '💰 ROI-Optimized Quick Win',
            'priority': 'critical',
            'strategy': f'ROI analysis identifies highest-impact quick win: {top_roi_issue.get("title", "Unknown issue")}',
            'action': f'Immediate implementation: {top_roi_issue.get("recommendation", "Follow issue guidelines")}',
            'impact': 'very_high',
            'effort': 'low',
            'data_point': f'ROI Score: {quick_wins[0][1]:.1f}x (Impact: {top_roi_issue.get("impact_score", 0)}, Effort: {top_roi_issue.get("effort_score", 1)})',
            'reasoning': f'Highest ROI opportunity requiring minimal effort with maximum impact on overall score'
        })
    
    # Strategic investment analysis
    total_potential_impact = sum(issue.get('impact_score', 0) for issue in all_issues)
    if total_potential_impact > 200:  # Significant improvement potential
        strategies.append({
            'category': '📈 Strategic Investment Plan',
            'priority': 'medium',
            'strategy': f'Portfolio analysis reveals {total_potential_impact:.0f} points of improvement potential across {len(all_issues)} issues.',
            'action': f'Implement phased improvement plan: Month 1-2 focus on {len(critical_issues)} critical issues, Month 3-4 address {len(high_issues)} high-priority items.',
            'impact': 'very_high',
            'effort': 'high',
            'data_point': f'Full implementation could improve score from {professional_score:.1f} to {min(100, professional_score + total_potential_impact*0.1):.1f}',
            'reasoning': f'Systematic approach maximizes cumulative impact while managing resource allocation efficiently'
        })
    
    return strategies

def synthesize_with_llm_insights(strategies, llm_analysis, url):
    """🤖 LLM Synthesis - Understanding AI-powered insights"""
    ai_strategies = []
    
    if not llm_analysis or not isinstance(llm_analysis, dict):
        return ai_strategies
    
    # Extract LLM recommendations
    llm_recommendations = llm_analysis.get('recommendations', [])
    llm_insights = llm_analysis.get('insights', {})
    
    domain = url.split('//')[1].split('/')[0] if '//' in url else url
    
    # Synthesize LLM insights with analytical findings
    if llm_recommendations:
        for i, rec in enumerate(llm_recommendations[:2]):  # Top 2 LLM recommendations
            if isinstance(rec, dict):
                ai_insight = rec.get('insight', 'Advanced optimization opportunity')
                ai_action = rec.get('action', 'Review AI recommendations')
                
                ai_strategies.append({
                    'category': '🤖 AI-Powered Strategic Insight',
                    'priority': 'medium',
                    'strategy': f'Advanced AI analysis for {domain}: {ai_insight}',
                    'action': f'AI-guided implementation: {ai_action}',
                    'impact': 'medium',
                    'effort': 'medium',
                    'data_point': f'Based on advanced pattern recognition and competitive analysis',
                    'reasoning': f'AI synthesis combines content analysis, user intent modeling, and market positioning for {domain}'
                })
    
    # Extract credibility insights if available
    if llm_insights.get('credibility_analysis'):
        credibility = llm_insights['credibility_analysis']
        ai_strategies.append({
            'category': '🤖 AI Credibility Enhancement',
            'priority': 'medium',
            'strategy': f'AI credibility analysis identifies trust signal optimization opportunities.',
            'action': f'Implement E-E-A-T enhancement based on AI assessment: {credibility.get("recommendation", "Enhance expertise signals")}',
            'impact': 'high',
            'effort': 'medium',
            'data_point': f'AI-detected credibility score: {credibility.get("score", "analyzing")}',
            'reasoning': f'Trust signals directly impact search rankings and user conversion rates'
        })
    
    return ai_strategies

def prioritize_strategies_analytically(strategies, professional_score, category_scores):
    """🎯 Analytical Strategy Prioritization - Understanding optimal execution order"""
    
    # Priority scoring algorithm
    priority_weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 1}
    impact_weights = {'very_high': 10, 'high': 7, 'medium': 4, 'low': 1}
    effort_weights = {'low': 10, 'medium': 6, 'high': 3, 'very_high': 1}  # Lower effort = higher score
    
    for strategy in strategies:
        priority_score = priority_weights.get(strategy.get('priority', 'medium'), 4)
        impact_score = impact_weights.get(strategy.get('impact', 'medium'), 4)
        effort_score = effort_weights.get(strategy.get('effort', 'medium'), 6)
        
        # Calculate analytical priority score
        analytical_score = (priority_score * 0.4) + (impact_score * 0.4) + (effort_score * 0.2)
        
        # Boost quick wins for low-scoring sites
        if professional_score < 60 and strategy.get('effort') == 'low' and strategy.get('impact') in ['high', 'very_high']:
            analytical_score *= 1.3
        
        strategy['analytical_priority'] = analytical_score
    
    # Sort by analytical priority
    strategies.sort(key=lambda x: x.get('analytical_priority', 0), reverse=True)
    
    return strategies

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """分析网站SEO并返回结果 - 优化版本"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'Missing URL parameter'}), 400
        
        # 记录开始时间
        start_time = time.time()
        
        # 第一阶段：基础分析（支持LLM分析、专业诊断、Trends分析和PageSpeed分析）
        run_llm_analysis = data.get('run_llm_analysis', True)  # 默认启用LLM分析
        run_professional_analysis = data.get('run_professional_analysis', True)  # 默认启用专业诊断
        enable_trends_analysis = data.get('enable_trends_analysis', False)  # 可选趋势分析
        enable_pagespeed_analysis = data.get('enable_pagespeed_analysis', False)  # 可选PageSpeed分析
        use_cache = data.get('use_cache', True)  # 默认启用智能缓存
        
        print(f"🚀 Starting analysis for {url} (cache: {'enabled' if use_cache else 'disabled'}, trends: {'enabled' if enable_trends_analysis else 'disabled'}, pagespeed: {'enabled' if enable_pagespeed_analysis else 'disabled'})")
        
        analysis_result = analyze(
            url=url,
            sitemap_url=data.get('sitemap'),
            follow_links=False,  # 禁用链接跟踪以提高速度
            analyze_headings=True,
            analyze_extra_tags=True,
            run_llm_analysis=run_llm_analysis,  # 启用SiliconFlow API分析
            run_professional_analysis=run_professional_analysis,  # 启用专业诊断分析
            enable_trends_analysis=enable_trends_analysis,  # 启用SerpAPI Google Trends分析
            enable_pagespeed_analysis=enable_pagespeed_analysis,  # 启用PageSpeed Insights分析
            use_cache=use_cache  # 启用智能缓存系统
        )
        
        # 第二阶段：计算SEO评分（使用统一评分系统）
        seo_score = calculate_unified_seo_score(analysis_result)
        print(f"🎯 Unified Score Result: {seo_score['score']:.1f} from {seo_score['source']}")
        
        # 第三阶段：生成核心建议（优化版本）
        recommendations = generate_quick_recommendations(analysis_result)
        
        # 第四阶段：生成UltraThinking智能战略建议（深度分析推理）
        strategic_recommendations = generate_ultrathinking_strategies(
            analysis_result, 
            seo_score, 
            analysis_result.get('llm_analysis')
        )
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 获取缓存统计信息
        cache_stats = get_cache_stats() if use_cache else None
        
        # 返回优化后的结果
        result = {
            'analysis': analysis_result,
            'seo_score': seo_score,
            'recommendations': recommendations,
            'strategic_recommendations': strategic_recommendations,
            'performance': {
                'execution_time': round(execution_time, 2),
                'optimized': True,
                'cache_enabled': use_cache,
                'cache_stats': cache_stats
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Analysis error: {str(e)}")  # 调试输出
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/generate-sitemap', methods=['POST'])
@app.route('/generate-sitemap', methods=['POST'])
def api_generate_sitemap():
    """生成XML站点地图"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'Missing URL parameter'}), 400
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行轻量级网站分析以获取URL列表 - 优化版本
        analysis_result = analyze(
            url=url,
            sitemap_url=data.get('sitemap'),
            follow_links=False,  # 禁用链接跟踪以提高速度
            analyze_headings=False,  # 只生成sitemap，不需要详细分析
            analyze_extra_tags=False,  # 只关注URL发现，不需要详细分析
            run_llm_analysis=False  # sitemap生成不需要LLM分析
        )
        
        # 生成站点地图
        sitemap_xml = generate_sitemap_from_analysis(url, analysis_result)
        
        # 验证生成的站点地图
        generator = SitemapGenerator()
        validation_result = generator.validate_sitemap(sitemap_xml)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        if validation_result.get('valid'):
            # 根据请求格式返回结果
            if data.get('format') == 'download':
                # 返回可下载的XML文件
                return Response(
                    sitemap_xml,
                    mimetype='application/xml',
                    headers={
                        'Content-Disposition': f'attachment; filename=sitemap.xml',
                        'Content-Type': 'application/xml; charset=utf-8'
                    }
                )
            else:
                # 返回JSON格式的结果（包含XML内容和元数据）
                result = {
                    'sitemap_xml': sitemap_xml,
                    'validation': validation_result,
                    'performance': {
                        'execution_time': round(execution_time, 2),
                        'url_count': validation_result.get('url_count', 0),
                        'size_bytes': validation_result.get('size_bytes', 0)
                    },
                    'timestamp': datetime.now().isoformat(),
                    'website_url': url
                }
                return jsonify(result)
        else:
            return jsonify({
                'error': 'Generated sitemap failed validation',
                'validation_error': validation_result.get('error'),
                'execution_time': round(execution_time, 2)
            }), 500
    
    except Exception as e:
        print(f"Sitemap generation error: {str(e)}")  # 调试输出
        return jsonify({'error': f'Sitemap generation failed: {str(e)}'}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """获取SEO建议列表 - 仅在有分析数据时返回"""
    # Only return recommendations if there's analysis data
    # This prevents showing example data on initial page load
    return jsonify({
        'recommendations': [],  # Empty by default
        'categories': ['content', 'technical', 'performance', 'accessibility'],
        'message': '请先进行SEO分析以获取个性化建议'
    })

@app.route('/api/thresholds', methods=['GET', 'POST'])
def manage_thresholds():
    """管理SEO阈值配置"""
    if request.method == 'GET':
        return jsonify(SEO_THRESHOLDS)
    
    elif request.method == 'POST':
        try:
            new_thresholds = request.get_json()
            SEO_THRESHOLDS.update(new_thresholds)
            return jsonify({'message': '阈值更新成功', 'thresholds': SEO_THRESHOLDS})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/api/generate-report', methods=['POST'])
def api_generate_report():
    """生成并下载SEO分析报告"""
    try:
        data = request.get_json()
        
        # 检查必需参数
        url = data.get('url')
        if not url:
            return jsonify({'error': 'Missing URL parameter'}), 400
        
        # 获取报告格式，默认为HTML
        report_format = data.get('format', 'html').lower()
        
        # 记录开始时间
        start_time = time.time()
        
        # 检查是否提供了现有的分析数据
        analysis_data = data.get('analysis_data')
        
        if not analysis_data:
            # 如果没有提供分析数据，需要重新分析
            run_llm_analysis = data.get('run_llm_analysis', True)
            analysis_result = analyze(
                url=url,
                sitemap_url=data.get('sitemap'),
                follow_links=False,
                analyze_headings=True,
                analyze_extra_tags=True,
                run_llm_analysis=run_llm_analysis,
                run_professional_analysis=True  # 启用专业诊断确保一致性
            )
            
            # 组装完整的分析数据（使用统一评分系统）
            seo_score = calculate_unified_seo_score(analysis_result)
            recommendations = generate_quick_recommendations(analysis_result)
            
            analysis_data = {
                'url': url,
                'basic_seo_analysis': analysis_result.get('pages', [{}])[0] if analysis_result.get('pages') else {},
                'llm_analysis': analysis_result.get('llm_analysis', {}),
                'professional_analysis': analysis_result.get('pages', [{}])[0].get('professional_analysis', {}) if analysis_result.get('pages') else {},
                'seo_score': seo_score,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
        
        # 生成报告
        report_generator = SEOReportGenerator()
        report_result = report_generator.generate_report(analysis_data, report_format)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 返回下载响应
        return Response(
            report_result['content'],
            mimetype=report_result['mimetype'],
            headers={
                'Content-Disposition': f'attachment; filename={report_result["filename"]}',
                'Content-Type': f'{report_result["mimetype"]}; charset=utf-8',
                'X-Generation-Time': str(round(execution_time, 2)),
                'X-Report-Format': report_result['format']
            }
        )
    
    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/api/todos', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_todos():
    """
    🎯 TODO Management API - Handle CRUD operations for TODO items
    
    GET: Retrieve all todos for a session
    POST: Create a new todo item  
    PUT: Update an existing todo item
    DELETE: Delete a todo item
    """
    try:
        if request.method == 'GET':
            # Retrieve todos from session or return empty list
            todos = session.get('todos', [])
            return jsonify({
                'todos': todos,
                'count': len(todos),
                'pending': len([t for t in todos if not t.get('completed', False)]),
                'completed': len([t for t in todos if t.get('completed', False)])
            })
        
        elif request.method == 'POST':
            # Create new todo
            data = request.get_json()
            if not data or not data.get('text'):
                return jsonify({'error': 'Todo text is required'}), 400
            
            # Get existing todos from session
            todos = session.get('todos', [])
            
            # Create new todo item
            new_todo = {
                'id': int(time.time() * 1000),  # Timestamp-based ID
                'text': data.get('text', '').strip(),
                'priority': data.get('priority', 'medium'),
                'completed': False,
                'created_at': datetime.now().isoformat(),
                'source': data.get('source', 'manual'),  # 'manual', 'strategy', 'auto'
                'category': data.get('category', 'general')
            }
            
            todos.append(new_todo)
            session['todos'] = todos
            
            return jsonify({
                'success': True,
                'todo': new_todo,
                'message': 'Todo created successfully'
            })
        
        elif request.method == 'PUT':
            # Update existing todo
            data = request.get_json()
            todo_id = data.get('id')
            
            if not todo_id:
                return jsonify({'error': 'Todo ID is required'}), 400
            
            todos = session.get('todos', [])
            todo_found = False
            
            for todo in todos:
                if todo.get('id') == todo_id:
                    # Update todo fields
                    if 'text' in data:
                        todo['text'] = data['text'].strip()
                    if 'priority' in data:
                        todo['priority'] = data['priority']
                    if 'completed' in data:
                        todo['completed'] = data['completed']
                        if data['completed']:
                            todo['completed_at'] = datetime.now().isoformat()
                    
                    todo['updated_at'] = datetime.now().isoformat()
                    todo_found = True
                    break
            
            if not todo_found:
                return jsonify({'error': 'Todo not found'}), 404
            
            session['todos'] = todos
            
            return jsonify({
                'success': True,
                'message': 'Todo updated successfully'
            })
        
        elif request.method == 'DELETE':
            # Delete todo
            data = request.get_json()
            todo_id = data.get('id')
            
            if not todo_id:
                return jsonify({'error': 'Todo ID is required'}), 400
            
            todos = session.get('todos', [])
            original_count = len(todos)
            
            # Filter out the todo to delete
            todos = [todo for todo in todos if todo.get('id') != todo_id]
            
            if len(todos) == original_count:
                return jsonify({'error': 'Todo not found'}), 404
            
            session['todos'] = todos
            
            return jsonify({
                'success': True,
                'message': 'Todo deleted successfully'
            })
    
    except Exception as e:
        print(f"❌ TODO API error: {e}")
        return jsonify({'error': f'TODO operation failed: {str(e)}'}), 500

@app.route('/api/todos/clear-completed', methods=['POST'])  
def clear_completed_todos():
    """🧹 Clear all completed todos"""
    try:
        todos = session.get('todos', [])
        completed_count = len([t for t in todos if t.get('completed', False)])
        
        # Keep only non-completed todos
        todos = [todo for todo in todos if not todo.get('completed', False)]
        session['todos'] = todos
        
        return jsonify({
            'success': True,
            'cleared_count': completed_count,
            'remaining_count': len(todos),
            'message': f'Cleared {completed_count} completed todos'
        })
    
    except Exception as e:
        print(f"❌ Clear completed todos error: {e}")
        return jsonify({'error': f'Failed to clear completed todos: {str(e)}'}), 500

@app.route('/api/todos/from-strategy', methods=['POST'])
def create_todo_from_strategy():
    """
    🎯 Create TODO from UltraThinking strategy recommendation
    
    This endpoint handles converting strategy recommendations into actionable TODO items
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('strategy'):
            return jsonify({'error': 'Strategy data is required'}), 400
        
        strategy = data['strategy']
        
        # Extract todo details from strategy
        todo_text = f"{strategy.get('category', 'Strategy')}: {strategy.get('action', strategy.get('strategy', 'SEO Task'))}"
        
        # Get existing todos from session
        todos = session.get('todos', [])
        
        # Check for duplicates
        duplicate_exists = any(
            todo.get('text', '').lower() == todo_text.lower() 
            for todo in todos
        )
        
        if duplicate_exists:
            return jsonify({
                'success': False,
                'message': 'This strategy is already in your TODO list',
                'duplicate': True
            })
        
        # Create todo from strategy
        new_todo = {
            'id': int(time.time() * 1000),
            'text': todo_text,
            'priority': strategy.get('priority', 'medium'),
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'source': 'ultrathinking_strategy',
            'category': strategy.get('category', 'SEO Strategy'),
            'impact': strategy.get('impact', 'medium'),
            'effort': strategy.get('effort', 'medium'),
            'data_point': strategy.get('data_point', ''),
            'reasoning': strategy.get('reasoning', ''),
            'original_strategy': strategy  # Store full strategy for reference
        }
        
        todos.append(new_todo)
        session['todos'] = todos
        
        return jsonify({
            'success': True,
            'todo': new_todo,
            'message': 'Strategy added to TODO list successfully'
        })
    
    except Exception as e:
        print(f"❌ Strategy to TODO error: {e}")
        return jsonify({'error': f'Failed to create todo from strategy: {str(e)}'}), 500

@app.route('/api/cache', methods=['GET', 'DELETE'])
def manage_cache():
    """🧠 Cache Management API - View cache statistics and manage cache data"""
    try:
        if request.method == 'GET':
            # Get comprehensive cache statistics
            cache_stats = get_cache_stats()
            
            return jsonify({
                'success': True,
                'cache_stats': cache_stats,
                'timestamp': datetime.now().isoformat(),
                'message': 'Cache statistics retrieved successfully'
            })
        
        elif request.method == 'DELETE':
            # Clear cache data
            data = request.get_json() or {}
            url = data.get('url')
            analysis_type = data.get('analysis_type')
            
            # Import here to avoid circular imports
            from pyseoanalyzer.intelligent_cache import invalidate_cache
            
            # Invalidate cache entries
            invalidated_count = invalidate_cache(url=url, analysis_type=analysis_type)
            
            return jsonify({
                'success': True,
                'invalidated_count': invalidated_count,
                'message': f'Successfully invalidated {invalidated_count} cache entries',
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        print(f"❌ Cache management error: {e}")
        return jsonify({'error': f'Cache management failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# 🔥 Trends Analysis API Endpoints
@app.route('/api/trends/analysis', methods=['POST'])
def trends_comprehensive_analysis():
    """
    🔥 Comprehensive Trends Analysis API
    
    Provides complete trends analysis including:
    - Keyword trend patterns
    - Content opportunities
    - Seasonal insights  
    - Competitive analysis
    - Search intent alignment
    - Trending topics relevance
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        enable_professional = data.get('enable_professional_analysis', True)
        
        print(f"🔥 Starting comprehensive trends analysis for: {url}")
        
        # Perform full SEO analysis with professional diagnostics
        analysis_result = analyze(
            url,
            run_professional_analysis=enable_professional,
            enable_trends_analysis=True,
            use_cache=True
        )
        
        # Extract trends insights from the analysis
        trends_insights = analysis_result.get('trends_insights', {})
        
        # Extract professional diagnostics trends data if available
        professional_trends = {}
        if 'professional_diagnostics' in analysis_result:
            diagnostic_results = analysis_result['professional_diagnostics'].get('diagnostic_results', {})
            professional_trends = diagnostic_results.get('trends_analysis', {})
        
        # Combine insights for comprehensive response
        comprehensive_trends = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'trends_insights': trends_insights,
            'professional_trends': professional_trends,
            'analysis_summary': {
                'keywords_analyzed': len(analysis_result.get('keywords', [])),
                'trends_available': bool(trends_insights),
                'professional_analysis': bool(professional_trends),
                'cache_used': analysis_result.get('cache_used', False)
            }
        }
        
        return jsonify({
            'success': True,
            'data': comprehensive_trends,
            'message': 'Comprehensive trends analysis completed successfully'
        })
        
    except Exception as e:
        print(f"❌ Trends analysis error: {e}")
        return jsonify({'error': f'Trends analysis failed: {str(e)}'}), 500

@app.route('/api/trends/keywords', methods=['POST'])
def trends_keyword_analysis():
    """
    📈 Keyword Trends Analysis API
    
    Analyzes keyword trend patterns including:
    - Rising/falling trends
    - Search volume patterns
    - Interest over time
    - Related queries and topics
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        keywords = data.get('keywords', [])
        url = data.get('url')
        region = data.get('region', 'US')
        timeframe = data.get('timeframe', 'today 12-m')
        
        if not keywords and not url:
            return jsonify({'error': 'Either keywords array or URL is required'}), 400
        
        # Import trends analyzer
        from pyseoanalyzer.serpapi_trends import SerpAPITrends
        
        trends_analyzer = SerpAPITrends()
        
        # If URL provided, extract keywords from page analysis
        if url and not keywords:
            print(f"📊 Extracting keywords from URL: {url}")
            page_analysis = analyze(url, use_cache=True)
            keywords = [kw['keyword'] for kw in page_analysis.get('keywords', [])[:10]]
        
        if not keywords:
            return jsonify({'error': 'No keywords found for analysis'}), 400
        
        print(f"📈 Analyzing trends for {len(keywords)} keywords: {keywords[:5]}...")
        
        # Get keyword trends data
        trends_data = trends_analyzer.get_keyword_trends(keywords, region, timeframe)
        
        # Format response data
        keyword_trends = {}
        for keyword, trend_info in trends_data.items():
            keyword_trends[keyword] = {
                'keyword': trend_info.keyword,
                'average_interest': trend_info.average_interest,
                'trend_direction': trend_info.trend_direction,
                'region': trend_info.region,
                'timeframe': trend_info.timeframe,
                'interest_over_time': trend_info.interest_over_time[:12],  # Limit data size
                'related_topics_count': len(trend_info.related_topics),
                'related_queries_count': len(trend_info.related_queries),
                'rising_queries_count': len(trend_info.rising_queries),
                'peak_periods_count': len(trend_info.peak_periods)
            }
        
        return jsonify({
            'success': True,
            'data': {
                'keyword_trends': keyword_trends,
                'analysis_meta': {
                    'keywords_analyzed': len(keywords),
                    'region': region,
                    'timeframe': timeframe,
                    'timestamp': datetime.now().isoformat()
                }
            },
            'message': f'Keyword trends analysis completed for {len(keywords)} keywords'
        })
        
    except Exception as e:
        print(f"❌ Keyword trends error: {e}")
        return jsonify({'error': f'Keyword trends analysis failed: {str(e)}'}), 500

@app.route('/api/trends/opportunities', methods=['POST'])
def trends_content_opportunities():
    """
    💡 Content Opportunities Analysis API
    
    Identifies content opportunities including:
    - Content gaps
    - Trending topics
    - Seasonal patterns
    - Optimization priorities
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        url = data.get('url')
        keywords = data.get('keywords', [])
        region = data.get('region', 'US')
        
        if not url and not keywords:
            return jsonify({'error': 'Either URL or keywords array is required'}), 400
        
        # Import trends analyzer
        from pyseoanalyzer.serpapi_trends import SerpAPITrends
        
        trends_analyzer = SerpAPITrends()
        
        # Extract keywords from URL if needed
        if url and not keywords:
            print(f"💡 Extracting keywords from URL for opportunities: {url}")
            page_analysis = analyze(url, use_cache=True)
            keywords = [kw['keyword'] for kw in page_analysis.get('keywords', [])[:15]]
        
        if not keywords:
            return jsonify({'error': 'No keywords found for opportunity analysis'}), 400
        
        print(f"💡 Analyzing content opportunities for {len(keywords)} keywords...")
        
        # Get content opportunities
        opportunities = trends_analyzer.analyze_content_opportunities(keywords, region)
        
        # Get trending keywords for additional opportunities
        trending_keywords = trends_analyzer.get_trending_keywords(region=region)
        
        # Format response
        content_opportunities = {
            'keyword_analysis': opportunities.get('keyword_analysis', {}),
            'content_suggestions': opportunities.get('content_suggestions', []),
            'seasonal_insights': opportunities.get('seasonal_insights', []),
            'trending_opportunities': opportunities.get('trending_opportunities', []),
            'optimization_priorities': opportunities.get('optimization_priorities', []),
            'trending_keywords': trending_keywords[:10],  # Top 10 trending
            'analysis_meta': {
                'base_keywords': len(keywords),
                'content_suggestions_count': len(opportunities.get('content_suggestions', [])),
                'optimization_priorities_count': len(opportunities.get('optimization_priorities', [])),
                'trending_keywords_count': len(trending_keywords),
                'region': region,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'data': content_opportunities,
            'message': f'Content opportunities analysis completed for {len(keywords)} keywords'
        })
        
    except Exception as e:
        print(f"❌ Content opportunities error: {e}")
        return jsonify({'error': f'Content opportunities analysis failed: {str(e)}'}), 500

@app.route('/api/trends/competitive', methods=['POST'])
def trends_competitive_analysis():
    """
    🏆 Competitive Trends Analysis API
    
    Provides competitive analysis including:
    - Domain keyword tracking
    - Ranking opportunities
    - Competitive positioning
    - Market trends
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        max_keywords = data.get('max_keywords', 50)
        
        print(f"🏆 Starting competitive analysis for: {url}")
        
        # Import keyword diagnostics API
        from pyseoanalyzer.keyword_diagnostics import KeywordComAPI
        
        keyword_api = KeywordComAPI()
        
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        # Get competitive analysis
        competitive_data = keyword_api.analyze_domain_keywords(domain, max_keywords)
        
        if 'error' in competitive_data:
            return jsonify({
                'success': False,
                'data': {
                    'domain': domain,
                    'error': competitive_data['error'],
                    'analysis_available': False
                },
                'message': f'Competitive analysis limited: {competitive_data["error"]}'
            })
        
        # Format competitive analysis response
        competitive_analysis = {
            'domain': domain,
            'total_keywords': competitive_data.get('total_keywords', 0),
            'projects_analyzed': competitive_data.get('projects_analyzed', 0),
            'keywords_data': competitive_data.get('keywords', []),
            'analysis': competitive_data.get('analysis', {}),
            'recommendations': competitive_data.get('recommendations', []),
            'analysis_meta': {
                'api_available': True,
                'max_keywords_analyzed': max_keywords,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'data': competitive_analysis,
            'message': f'Competitive analysis completed for {domain}'
        })
        
    except Exception as e:
        print(f"❌ Competitive analysis error: {e}")
        return jsonify({'error': f'Competitive analysis failed: {str(e)}'}), 500

@app.route('/api/trends/trending', methods=['GET'])
def trends_current_trending():
    """
    🌟 Current Trending Topics API
    
    Provides current trending keywords and topics including:
    - Real-time trending searches
    - Category-specific trends
    - Regional trending data
    """
    try:
        # Get query parameters
        region = request.args.get('region', 'US')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 20))
        
        print(f"🌟 Fetching trending topics for region: {region}")
        
        # Import trends analyzer
        from pyseoanalyzer.serpapi_trends import SerpAPITrends
        
        trends_analyzer = SerpAPITrends()
        
        # Get trending keywords
        trending_keywords = trends_analyzer.get_trending_keywords(category=category, region=region)
        
        # Limit results
        limited_trending = trending_keywords[:limit]
        
        trending_data = {
            'trending_keywords': limited_trending,
            'analysis_meta': {
                'region': region,
                'category': category,
                'total_available': len(trending_keywords),
                'returned_count': len(limited_trending),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'data': trending_data,
            'message': f'Retrieved {len(limited_trending)} trending topics for {region}'
        })
        
    except Exception as e:
        print(f"❌ Trending topics error: {e}")
        return jsonify({'error': f'Trending topics retrieval failed: {str(e)}'}), 500

@app.route('/api/trends/status', methods=['GET'])
def trends_api_status():
    """
    ⚡ Trends API Status Check
    
    Checks the status and availability of trends analysis APIs:
    - SerpAPI Trends availability
    - Keyword.com API availability
    - API quota and rate limits
    """
    try:
        status_info = {
            'serpapi_trends': {'available': False, 'error': None},
            'keyword_com_api': {'available': False, 'error': None},
            'overall_status': 'degraded',
            'timestamp': datetime.now().isoformat()
        }
        
        # Check SerpAPI Trends
        try:
            from pyseoanalyzer.serpapi_trends import SerpAPITrends
            trends_analyzer = SerpAPITrends()
            # Try a simple test
            test_trends = trends_analyzer.get_trending_keywords()
            status_info['serpapi_trends'] = {
                'available': True,
                'test_keywords_count': len(test_trends) if test_trends else 0
            }
        except Exception as e:
            status_info['serpapi_trends'] = {
                'available': False,
                'error': str(e)
            }
        
        # Check Keyword.com API
        try:
            from pyseoanalyzer.keyword_diagnostics import KeywordComAPI
            keyword_api = KeywordComAPI()
            # Try getting projects
            projects = keyword_api.get_all_projects()
            status_info['keyword_com_api'] = {
                'available': True,
                'projects_count': len(projects) if projects else 0
            }
        except Exception as e:
            status_info['keyword_com_api'] = {
                'available': False,
                'error': str(e)
            }
        
        # Determine overall status
        if status_info['serpapi_trends']['available'] and status_info['keyword_com_api']['available']:
            status_info['overall_status'] = 'healthy'
        elif status_info['serpapi_trends']['available'] or status_info['keyword_com_api']['available']:
            status_info['overall_status'] = 'partial'
        else:
            status_info['overall_status'] = 'unavailable'
        
        return jsonify({
            'success': True,
            'data': status_info,
            'message': f'Trends API status: {status_info["overall_status"]}'
        })
        
    except Exception as e:
        print(f"❌ Trends status check error: {e}")
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

# 🚀 PageSpeed Insights API Endpoints
@app.route('/api/pagespeed/analyze', methods=['POST'])
def pagespeed_analyze_url():
    """
    🚀 PageSpeed Insights URL Analysis API
    
    Provides comprehensive PageSpeed analysis including:
    - Core Web Vitals (LCP, FID, CLS, FCP, Speed Index, TTI, TBT)
    - Performance scores for mobile and desktop
    - SEO and accessibility scores
    - Optimization opportunities and diagnostics
    - Performance impact assessment
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        strategy = data.get('strategy', 'mobile')  # mobile or desktop
        categories = data.get('categories', ['performance', 'seo', 'accessibility', 'best-practices'])
        
        print(f"🚀 Starting PageSpeed analysis for: {url} (strategy: {strategy})")
        
        # Import PageSpeed API
        from pyseoanalyzer.pagespeed_insights import PageSpeedInsightsAPI
        
        pagespeed_api = PageSpeedInsightsAPI()
        
        # Perform analysis
        analysis = pagespeed_api.analyze_url(url, strategy=strategy, categories=categories)
        
        # Get recommendations
        recommendations = pagespeed_api.get_performance_recommendations(analysis)
        
        # Calculate impact
        impact_assessment = pagespeed_api.calculate_performance_impact(analysis)
        
        # Format comprehensive response
        pagespeed_data = {
            'url': analysis.url,
            'strategy': analysis.strategy,
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': {
                'performance_score': analysis.performance_metrics.performance_score if analysis.performance_metrics else None,
                'seo_score': analysis.performance_metrics.seo_score if analysis.performance_metrics else None,
                'accessibility_score': analysis.performance_metrics.accessibility_score if analysis.performance_metrics else None,
                'best_practices_score': analysis.performance_metrics.best_practices_score if analysis.performance_metrics else None,
                'pwa_score': analysis.performance_metrics.pwa_score if analysis.performance_metrics else None
            },
            'core_web_vitals': {
                'largest_contentful_paint': analysis.performance_metrics.core_web_vitals.largest_contentful_paint if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None,
                'first_input_delay': analysis.performance_metrics.core_web_vitals.first_input_delay if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None,
                'cumulative_layout_shift': analysis.performance_metrics.core_web_vitals.cumulative_layout_shift if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None,
                'first_contentful_paint': analysis.performance_metrics.core_web_vitals.first_contentful_paint if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None,
                'speed_index': analysis.performance_metrics.core_web_vitals.speed_index if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None,
                'time_to_interactive': analysis.performance_metrics.core_web_vitals.time_to_interactive if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None,
                'total_blocking_time': analysis.performance_metrics.core_web_vitals.total_blocking_time if analysis.performance_metrics and analysis.performance_metrics.core_web_vitals else None
            },
            'opportunities': analysis.performance_metrics.opportunities[:10] if analysis.performance_metrics and analysis.performance_metrics.opportunities else [],
            'diagnostics': analysis.performance_metrics.diagnostics[:10] if analysis.performance_metrics and analysis.performance_metrics.diagnostics else [],
            'recommendations': recommendations,
            'impact_assessment': impact_assessment,
            'lighthouse_info': {
                'version': analysis.lighthouse_version,
                'user_agent': analysis.user_agent,
                'fetch_time': analysis.fetch_time
            }
        }
        
        return jsonify({
            'success': True,
            'data': pagespeed_data,
            'message': f'PageSpeed analysis completed for {url} ({strategy})'
        })
        
    except Exception as e:
        print(f"❌ PageSpeed analysis error: {e}")
        return jsonify({'error': f'PageSpeed analysis failed: {str(e)}'}), 500

@app.route('/api/pagespeed/compare', methods=['POST'])
def pagespeed_compare_strategies():
    """
    📊 PageSpeed Mobile vs Desktop Comparison API
    
    Compares performance metrics between mobile and desktop strategies:
    - Side-by-side Core Web Vitals comparison
    - Performance score differences
    - Strategy-specific optimization recommendations
    - Mobile-first optimization priorities
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        categories = data.get('categories', ['performance', 'seo', 'accessibility', 'best-practices'])
        
        print(f"📊 Starting PageSpeed comparison analysis for: {url}")
        
        # Import PageSpeed API
        from pyseoanalyzer.pagespeed_insights import PageSpeedInsightsAPI
        
        pagespeed_api = PageSpeedInsightsAPI()
        
        # Analyze both strategies
        comparison_results = pagespeed_api.analyze_both_strategies(url)
        
        mobile_analysis = comparison_results['mobile']
        desktop_analysis = comparison_results['desktop']
        
        # Get recommendations for both
        mobile_recommendations = pagespeed_api.get_performance_recommendations(mobile_analysis)
        desktop_recommendations = pagespeed_api.get_performance_recommendations(desktop_analysis)
        
        # Calculate impact for both
        mobile_impact = pagespeed_api.calculate_performance_impact(mobile_analysis)
        desktop_impact = pagespeed_api.calculate_performance_impact(desktop_analysis)
        
        # Calculate comparison metrics
        performance_diff = (desktop_analysis.performance_metrics.performance_score or 0) - (mobile_analysis.performance_metrics.performance_score or 0)
        
        comparison_data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'mobile': {
                'performance_score': mobile_analysis.performance_metrics.performance_score if mobile_analysis.performance_metrics else None,
                'seo_score': mobile_analysis.performance_metrics.seo_score if mobile_analysis.performance_metrics else None,
                'core_web_vitals': {
                    'lcp': mobile_analysis.performance_metrics.core_web_vitals.largest_contentful_paint if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                    'fid': mobile_analysis.performance_metrics.core_web_vitals.first_input_delay if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None,
                    'cls': mobile_analysis.performance_metrics.core_web_vitals.cumulative_layout_shift if mobile_analysis.performance_metrics and mobile_analysis.performance_metrics.core_web_vitals else None
                },
                'recommendations_count': len(mobile_recommendations),
                'impact_score': mobile_impact.get('impact_score', 0),
                'critical_issues': len([r for r in mobile_recommendations if r.get('priority') == 'high'])
            },
            'desktop': {
                'performance_score': desktop_analysis.performance_metrics.performance_score if desktop_analysis.performance_metrics else None,
                'seo_score': desktop_analysis.performance_metrics.seo_score if desktop_analysis.performance_metrics else None,
                'core_web_vitals': {
                    'lcp': desktop_analysis.performance_metrics.core_web_vitals.largest_contentful_paint if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                    'fid': desktop_analysis.performance_metrics.core_web_vitals.first_input_delay if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None,
                    'cls': desktop_analysis.performance_metrics.core_web_vitals.cumulative_layout_shift if desktop_analysis.performance_metrics and desktop_analysis.performance_metrics.core_web_vitals else None
                },
                'recommendations_count': len(desktop_recommendations),
                'impact_score': desktop_impact.get('impact_score', 0),
                'critical_issues': len([r for r in desktop_recommendations if r.get('priority') == 'high'])
            },
            'comparison': {
                'performance_score_difference': performance_diff,
                'mobile_priority': performance_diff < -10,  # Mobile significantly worse
                'desktop_priority': performance_diff > 10,   # Desktop significantly worse
                'core_web_vitals_mobile_pass': mobile_impact.get('core_web_vitals_pass', False),
                'core_web_vitals_desktop_pass': desktop_impact.get('core_web_vitals_pass', False),
                'overall_recommendation': 'focus_mobile' if performance_diff < -10 else 'focus_desktop' if performance_diff > 10 else 'balanced_optimization'
            },
            'combined_recommendations': mobile_recommendations + desktop_recommendations
        }
        
        return jsonify({
            'success': True,
            'data': comparison_data,
            'message': f'PageSpeed comparison completed for {url}'
        })
        
    except Exception as e:
        print(f"❌ PageSpeed comparison error: {e}")
        return jsonify({'error': f'PageSpeed comparison failed: {str(e)}'}), 500

@app.route('/api/pagespeed/recommendations', methods=['POST'])
def pagespeed_get_recommendations():
    """
    💡 PageSpeed Performance Recommendations API
    
    Provides actionable performance recommendations including:
    - Core Web Vitals optimization strategies
    - Performance opportunity prioritization
    - Implementation guidance and time estimates
    - SEO impact assessment for each recommendation
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        strategy = data.get('strategy', 'mobile')
        priority_filter = data.get('priority_filter')  # high, medium, low
        
        print(f"💡 Generating PageSpeed recommendations for: {url}")
        
        # Import PageSpeed API
        from pyseoanalyzer.pagespeed_insights import PageSpeedInsightsAPI
        
        pagespeed_api = PageSpeedInsightsAPI()
        
        # Perform analysis
        analysis = pagespeed_api.analyze_url(url, strategy=strategy)
        
        # Get detailed recommendations
        recommendations = pagespeed_api.get_performance_recommendations(analysis)
        
        # Calculate performance impact
        impact_assessment = pagespeed_api.calculate_performance_impact(analysis)
        
        # Filter recommendations by priority if specified
        if priority_filter:
            recommendations = [r for r in recommendations if r.get('priority') == priority_filter]
        
        # Enhance recommendations with additional context
        enhanced_recommendations = []
        for rec in recommendations:
            enhanced_rec = rec.copy()
            
            # Add implementation estimates
            effort_mapping = {
                'low': {'time_estimate': '1-2 hours', 'difficulty': 'Easy', 'resources': 'Developer'},
                'medium': {'time_estimate': '4-8 hours', 'difficulty': 'Moderate', 'resources': 'Developer + Designer'},
                'high': {'time_estimate': '1-2 days', 'difficulty': 'Complex', 'resources': 'Senior Developer + Architect'}
            }
            
            effort = enhanced_rec.get('effort', 'medium')
            enhanced_rec.update(effort_mapping.get(effort, effort_mapping['medium']))
            
            # Add SEO impact scoring
            seo_impact_score = 0
            if enhanced_rec.get('category') == 'core_web_vitals':
                seo_impact_score = 9  # Core Web Vitals are critical for SEO
            elif enhanced_rec.get('category') == 'performance':
                seo_impact_score = 7  # Performance affects user experience and rankings
            elif enhanced_rec.get('category') == 'seo_performance':
                seo_impact_score = 8  # Direct SEO impact
            else:
                seo_impact_score = 5  # Moderate impact
            
            enhanced_rec['seo_impact_score'] = seo_impact_score
            enhanced_rec['seo_impact_level'] = 'critical' if seo_impact_score >= 8 else 'high' if seo_impact_score >= 6 else 'medium'
            
            enhanced_recommendations.append(enhanced_rec)
        
        # Sort by priority and SEO impact
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        enhanced_recommendations.sort(
            key=lambda x: (priority_order.get(x.get('priority', 'medium'), 2), x.get('seo_impact_score', 0)), 
            reverse=True
        )
        
        recommendations_data = {
            'url': url,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat(),
            'total_recommendations': len(enhanced_recommendations),
            'high_priority_count': len([r for r in enhanced_recommendations if r.get('priority') == 'high']),
            'medium_priority_count': len([r for r in enhanced_recommendations if r.get('priority') == 'medium']),
            'low_priority_count': len([r for r in enhanced_recommendations if r.get('priority') == 'low']),
            'core_web_vitals_issues': len([r for r in enhanced_recommendations if r.get('category') == 'core_web_vitals']),
            'performance_score': analysis.performance_metrics.performance_score if analysis.performance_metrics else None,
            'impact_assessment': impact_assessment,
            'recommendations': enhanced_recommendations
        }
        
        return jsonify({
            'success': True,
            'data': recommendations_data,
            'message': f'Generated {len(enhanced_recommendations)} PageSpeed recommendations for {url}'
        })
        
    except Exception as e:
        print(f"❌ PageSpeed recommendations error: {e}")
        return jsonify({'error': f'PageSpeed recommendations failed: {str(e)}'}), 500

@app.route('/api/pagespeed/status', methods=['GET'])
def pagespeed_api_status():
    """
    ⚡ PageSpeed Insights API Status Check
    
    Checks the status and availability of PageSpeed Insights API:
    - API key validation
    - Rate limit status
    - Service availability
    - Performance benchmarks
    """
    try:
        status_info = {
            'pagespeed_api': {'available': False, 'error': None},
            'api_key_status': 'unknown',
            'overall_status': 'degraded',
            'timestamp': datetime.now().isoformat()
        }
        
        # Check PageSpeed Insights API
        try:
            from pyseoanalyzer.pagespeed_insights import PageSpeedInsightsAPI
            
            pagespeed_api = PageSpeedInsightsAPI()
            
            if pagespeed_api.api_key:
                # Try a simple test analysis
                test_analysis = pagespeed_api.analyze_url("https://www.google.com", strategy="mobile")
                
                if test_analysis.performance_metrics:
                    status_info['pagespeed_api'] = {
                        'available': True,
                        'api_key_valid': True,
                        'test_performance_score': test_analysis.performance_metrics.performance_score,
                        'lighthouse_version': test_analysis.lighthouse_version
                    }
                    status_info['api_key_status'] = 'valid'
                else:
                    status_info['pagespeed_api'] = {
                        'available': True,
                        'api_key_valid': False,
                        'note': 'API accessible but limited functionality'
                    }
                    status_info['api_key_status'] = 'limited'
            else:
                status_info['pagespeed_api'] = {
                    'available': False,
                    'api_key_valid': False,
                    'error': 'No API key configured'
                }
                status_info['api_key_status'] = 'missing'
                
        except Exception as e:
            status_info['pagespeed_api'] = {
                'available': False,
                'error': str(e),
                'api_key_valid': False
            }
            status_info['api_key_status'] = 'error'
        
        # Determine overall status
        if status_info['pagespeed_api']['available'] and status_info['api_key_status'] == 'valid':
            status_info['overall_status'] = 'healthy'
        elif status_info['pagespeed_api']['available']:
            status_info['overall_status'] = 'partial'
        else:
            status_info['overall_status'] = 'unavailable'
        
        # Add usage recommendations
        status_info['recommendations'] = []
        if status_info['api_key_status'] == 'missing':
            status_info['recommendations'].append('Configure PAGESPEED_INSIGHTS_API_KEY environment variable')
        elif status_info['api_key_status'] == 'error':
            status_info['recommendations'].append('Verify API key validity and network connectivity')
        elif status_info['api_key_status'] == 'valid':
            status_info['recommendations'].append('PageSpeed Insights API is fully functional')
        
        return jsonify({
            'success': True,
            'data': status_info,
            'message': f'PageSpeed API status: {status_info["overall_status"]}'
        })
        
    except Exception as e:
        print(f"❌ PageSpeed status check error: {e}")
        return jsonify({'error': f'PageSpeed status check failed: {str(e)}'}), 500

# 🎯 MGX Integration API Endpoints
@app.route('/api/mgx-seo-optimizer', methods=['POST'])
def mgx_seo_optimizer():
    """
    🎯 MGX SEO Optimizer API - 为MGX平台提供具体的SEO优化指导
    
    支持两种模式：
    1. 内容模式：分析MGX提供的内容数据
    2. URL模式：直接分析真实网站URL
    
    将SEO分析结果转换为MGX可理解和执行的具体优化指导：
    - 内容优化建议（标题、描述、内容结构）
    - 技术SEO修复指导
    - 关键词优化策略
    - 优先级排序和预期效果评估
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        print("🎯 Processing MGX SEO optimization request...")
        
        # 提取输入数据
        current_content = data.get('current_content', {})
        target_url = data.get('target_url')  # 新增：支持直接分析URL
        seo_analysis = data.get('seo_analysis', {})
        target_keywords = data.get('target_keywords', [])
        website_type = data.get('website_type', 'general')
        mgx_context = data.get('mgx_context', {})
        
        # 验证输入：需要提供内容或URL
        if not current_content and not target_url:
            return jsonify({'error': 'Either current_content or target_url is required'}), 400
        
        # 如果提供了URL，则分析真实网站
        if target_url:
            print(f"🌐 Analyzing real website: {target_url}")
            real_analysis = analyze_real_website(target_url, target_keywords, website_type)
            
            if 'error' in real_analysis:
                return jsonify({'error': f'Website analysis failed: {real_analysis["error"]}'}), 400
            
            current_content = real_analysis['current_content']
            seo_analysis = real_analysis['seo_analysis']
            
        # 如果没有提供SEO分析，则对当前内容进行快速分析
        elif not seo_analysis:
            print("📊 No SEO analysis provided, performing quick analysis...")
            quick_analysis = perform_quick_seo_analysis(current_content, target_keywords)
            seo_analysis = quick_analysis
        
        # 生成优化指导
        optimization_guide = generate_mgx_optimization_guide(
            current_content=current_content,
            seo_analysis=seo_analysis,
            target_keywords=target_keywords,
            website_type=website_type,
            mgx_context=mgx_context
        )
        
        # 计算预期改进效果
        impact_assessment = calculate_optimization_impact(
            current_content=current_content,
            optimization_guide=optimization_guide,
            seo_analysis=seo_analysis
        )
        
        # 构建响应
        response_data = {
            'optimization_instructions': optimization_guide['instructions'],
            'priority_order': optimization_guide['priority_order'],
            'expected_improvements': impact_assessment,
            'implementation_guide': optimization_guide['implementation_guide'],
            'mgx_specific_actions': optimization_guide['mgx_actions'],
            'meta_info': {
                'website_type': website_type,
                'target_keywords_count': len(target_keywords),
                'optimization_categories': len(optimization_guide['instructions']),
                'timestamp': datetime.now().isoformat(),
                'api_version': '1.0'
            }
        }
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'MGX SEO optimization guide generated successfully'
        })
        
    except Exception as e:
        print(f"❌ MGX SEO Optimizer error: {e}")
        return jsonify({'error': f'MGX SEO optimization failed: {str(e)}'}), 500

def perform_quick_seo_analysis(current_content, target_keywords):
    """对当前内容执行快速SEO分析"""
    issues = []
    score = 100
    
    # 分析标题
    title = current_content.get('title', '')
    if not title:
        issues.append({'type': 'missing_title', 'priority': 'critical', 'impact': 'very_high'})
        score -= 30
    elif len(title) < 30:
        issues.append({'type': 'title_too_short', 'current_length': len(title), 'priority': 'high', 'impact': 'high'})
        score -= 15
    elif len(title) > 60:
        issues.append({'type': 'title_too_long', 'current_length': len(title), 'priority': 'medium', 'impact': 'medium'})
        score -= 8
    
    # 分析描述
    description = current_content.get('description', '')
    if not description:
        issues.append({'type': 'missing_description', 'priority': 'critical', 'impact': 'high'})
        score -= 25
    elif len(description) < 120:
        issues.append({'type': 'description_too_short', 'current_length': len(description), 'priority': 'high', 'impact': 'medium'})
        score -= 12
    
    # 分析内容结构
    content = current_content.get('content', '')
    headings = current_content.get('headings', [])
    
    if not any(h.startswith('H1') for h in headings):
        issues.append({'type': 'missing_h1', 'priority': 'critical', 'impact': 'high'})
        score -= 20
    
    h2_count = len([h for h in headings if h.startswith('H2')])
    if h2_count < 2:
        issues.append({'type': 'insufficient_h2', 'current_count': h2_count, 'priority': 'medium', 'impact': 'medium'})
        score -= 10
    
    # 分析关键词密度
    if target_keywords and content:
        keyword_issues = analyze_keyword_density(content, target_keywords)
        issues.extend(keyword_issues)
        score -= len(keyword_issues) * 5
    
    # 分析内容长度
    word_count = len(content.split()) if content else 0
    if word_count < 300:
        issues.append({'type': 'thin_content', 'current_word_count': word_count, 'priority': 'medium', 'impact': 'medium'})
        score -= 15
    
    return {
        'seo_score': max(0, score),
        'issues': issues,
        'analysis_type': 'quick_analysis',
        'timestamp': datetime.now().isoformat()
    }

def analyze_keyword_density(content, target_keywords):
    """分析关键词密度"""
    issues = []
    content_lower = content.lower()
    word_count = len(content.split())
    
    for keyword in target_keywords[:5]:  # 分析前5个关键词
        keyword_lower = keyword.lower()
        keyword_count = content_lower.count(keyword_lower)
        density = (keyword_count / word_count * 100) if word_count > 0 else 0
        
        if density < 0.5:
            issues.append({
                'type': 'low_keyword_density',
                'keyword': keyword,
                'current_density': round(density, 2),
                'priority': 'medium',
                'impact': 'medium'
            })
        elif density > 3.0:
            issues.append({
                'type': 'high_keyword_density',
                'keyword': keyword,
                'current_density': round(density, 2),
                'priority': 'medium',
                'impact': 'medium'
            })
    
    return issues

def generate_mgx_optimization_guide(current_content, seo_analysis, target_keywords, website_type, mgx_context):
    """生成MGX专用的优化指导"""
    instructions = {}
    priority_order = []
    implementation_guide = {}
    mgx_actions = []
    
    issues = seo_analysis.get('issues', [])
    current_score = seo_analysis.get('seo_score', 0)
    
    # 按优先级分类问题
    critical_issues = [i for i in issues if i.get('priority') == 'critical']
    high_issues = [i for i in issues if i.get('priority') == 'high']
    medium_issues = [i for i in issues if i.get('priority') == 'medium']
    
    # 1. 标题优化
    title_issues = [i for i in issues if 'title' in i.get('type', '')]
    if title_issues:
        title_optimization = generate_title_optimization(
            current_content.get('title', ''), 
            title_issues, 
            target_keywords, 
            website_type
        )
        instructions['title_optimization'] = title_optimization
        priority_order.append('title_optimization')
        mgx_actions.append({
            'action_type': 'update_title',
            'target_element': 'page_title',
            'new_value': title_optimization.get('suggested'),
            'implementation': 'direct_replacement'
        })
    
    # 2. 描述优化
    desc_issues = [i for i in issues if 'description' in i.get('type', '')]
    if desc_issues:
        desc_optimization = generate_description_optimization(
            current_content.get('description', ''),
            desc_issues,
            target_keywords,
            website_type
        )
        instructions['description_optimization'] = desc_optimization
        priority_order.append('description_optimization')
        mgx_actions.append({
            'action_type': 'update_meta_description',
            'target_element': 'meta_description',
            'new_value': desc_optimization.get('suggested'),
            'implementation': 'direct_replacement'
        })
    
    # 3. 内容结构优化
    structure_issues = [i for i in issues if any(keyword in i.get('type', '') for keyword in ['h1', 'h2', 'heading', 'structure'])]
    if structure_issues:
        structure_optimization = generate_structure_optimization(
            current_content,
            structure_issues,
            target_keywords,
            website_type
        )
        instructions['content_structure'] = structure_optimization
        priority_order.append('content_structure')
        
        # 为每个结构改进添加MGX动作
        for heading in structure_optimization.get('add_headings', []):
            mgx_actions.append({
                'action_type': 'add_heading',
                'target_element': heading.get('level'),
                'new_value': heading.get('suggested_text'),
                'position': heading.get('position'),
                'implementation': 'content_insertion'
            })
    
    # 4. 内容优化
    content_issues = [i for i in issues if any(keyword in i.get('type', '') for keyword in ['content', 'keyword', 'thin'])]
    if content_issues:
        content_optimization = generate_content_optimization(
            current_content.get('content', ''),
            content_issues,
            target_keywords,
            website_type
        )
        instructions['content_optimization'] = content_optimization
        priority_order.append('content_optimization')
        
        # 添加内容扩展动作
        for expansion in content_optimization.get('content_expansions', []):
            mgx_actions.append({
                'action_type': 'expand_content',
                'target_section': expansion.get('section'),
                'new_content': expansion.get('suggested_content'),
                'word_count_target': expansion.get('target_words'),
                'implementation': 'content_expansion'
            })
    
    # 5. 技术SEO修复
    technical_issues = [i for i in issues if i.get('type') not in ['title_too_short', 'title_too_long', 'description_too_short', 'missing_h1']]
    if technical_issues:
        technical_optimization = generate_technical_optimization(
            current_content,
            technical_issues,
            website_type
        )
        instructions['technical_optimization'] = technical_optimization
        priority_order.append('technical_optimization')
        
        for fix in technical_optimization.get('fixes', []):
            mgx_actions.append({
                'action_type': 'technical_fix',
                'fix_type': fix.get('type'),
                'target_elements': fix.get('targets'),
                'implementation_steps': fix.get('steps'),
                'implementation': 'technical_update'
            })
    
    # 生成实施指南
    implementation_guide = {
        'immediate_actions': [action for action in mgx_actions if any(pri in ['critical', 'high'] for pri in [i.get('priority', 'medium') for i in issues])],
        'secondary_actions': [action for action in mgx_actions if action not in implementation_guide.get('immediate_actions', [])],
        'estimated_time': calculate_implementation_time(mgx_actions),
        'difficulty_level': assess_implementation_difficulty(mgx_actions),
        'mgx_compatibility': 'fully_compatible'  # 所有建议都是MGX可执行的
    }
    
    return {
        'instructions': instructions,
        'priority_order': priority_order,
        'implementation_guide': implementation_guide,
        'mgx_actions': mgx_actions
    }

def generate_title_optimization(current_title, title_issues, target_keywords, website_type):
    """生成标题优化建议"""
    suggestions = []
    current_length = len(current_title) if current_title else 0
    
    # 基于问题类型生成建议
    for issue in title_issues:
        if issue.get('type') == 'missing_title':
            suggestions.append(f"创建包含主关键词'{target_keywords[0] if target_keywords else '核心关键词'}'的标题")
        elif issue.get('type') == 'title_too_short':
            needed_chars = 50 - current_length
            suggestions.append(f"扩展标题{needed_chars}个字符，添加相关关键词和价值主张")
        elif issue.get('type') == 'title_too_long':
            excess_chars = current_length - 60
            suggestions.append(f"缩短标题{excess_chars}个字符，保留核心关键词")
    
    # 生成具体的标题建议
    if target_keywords:
        main_keyword = target_keywords[0]
        if website_type == 'ecommerce':
            suggested_title = f"{main_keyword} - 专业{main_keyword}服务 | 品牌名"
        elif website_type == 'blog':
            suggested_title = f"{main_keyword}完整指南：专业建议与实用技巧"
        else:
            suggested_title = f"专业{main_keyword}服务 - 优质解决方案"
    else:
        suggested_title = current_title if current_title else "请添加包含关键词的标题"
    
    return {
        'current': current_title,
        'suggested': suggested_title,
        'reasons': [issue.get('type') for issue in title_issues],
        'specific_changes': suggestions,
        'expected_improvement': '+10-15 SEO分数',
        'implementation_priority': 'high'
    }

def generate_description_optimization(current_desc, desc_issues, target_keywords, website_type):
    """生成描述优化建议"""
    suggestions = []
    current_length = len(current_desc) if current_desc else 0
    
    for issue in desc_issues:
        if issue.get('type') == 'missing_description':
            suggestions.append("创建140-160字符的吸引人描述")
        elif issue.get('type') == 'description_too_short':
            needed_chars = 140 - current_length
            suggestions.append(f"扩展描述{needed_chars}个字符，添加关键词和行动号召")
    
    # 生成描述建议
    if target_keywords:
        main_keyword = target_keywords[0]
        suggested_desc = f"专业的{main_keyword}服务，提供优质解决方案。了解更多关于{main_keyword}的信息，立即获取免费咨询。"
    else:
        suggested_desc = current_desc if current_desc else "请添加包含关键词的描述"
    
    return {
        'current': current_desc,
        'suggested': suggested_desc,
        'reasons': [issue.get('type') for issue in desc_issues],
        'specific_changes': suggestions,
        'expected_improvement': '+8-12 SEO分数',
        'implementation_priority': 'high'
    }

def generate_structure_optimization(current_content, structure_issues, target_keywords, website_type):
    """生成内容结构优化建议"""
    add_headings = []
    content_structure_changes = []
    
    for issue in structure_issues:
        if issue.get('type') == 'missing_h1':
            main_keyword = target_keywords[0] if target_keywords else '核心主题'
            add_headings.append({
                'level': 'h1',
                'suggested_text': f"{main_keyword}专业指南",
                'position': 'page_top',
                'reason': '每个页面必须有且仅有一个H1标签'
            })
        elif issue.get('type') == 'insufficient_h2':
            current_count = issue.get('current_count', 0)
            needed = 3 - current_count
            for i in range(needed):
                keyword = target_keywords[i] if i < len(target_keywords) else f"相关主题{i+1}"
                add_headings.append({
                    'level': 'h2',
                    'suggested_text': f"{keyword}的重要特点",
                    'position': f'section_{i+2}',
                    'reason': '改善内容结构和可读性'
                })
    
    return {
        'add_headings': add_headings,
        'structure_improvements': content_structure_changes,
        'expected_improvement': '+5-10 SEO分数',
        'implementation_priority': 'medium'
    }

def generate_content_optimization(current_content, content_issues, target_keywords, website_type):
    """生成内容优化建议"""
    content_expansions = []
    keyword_optimizations = []
    
    for issue in content_issues:
        if issue.get('type') == 'thin_content':
            current_words = issue.get('current_word_count', 0)
            target_words = 500
            needed_words = target_words - current_words
            
            content_expansions.append({
                'section': 'main_content',
                'suggested_content': f"添加{needed_words}字的详细内容，包含关键词和相关信息",
                'target_words': needed_words,
                'focus_keywords': target_keywords[:3] if target_keywords else []
            })
        
        elif issue.get('type') == 'low_keyword_density':
            keyword = issue.get('keyword', '')
            keyword_optimizations.append({
                'keyword': keyword,
                'action': 'increase_usage',
                'suggestion': f"在内容中自然地增加2-3次'{keyword}'的使用",
                'target_density': '1.0-2.0%'
            })
        
        elif issue.get('type') == 'high_keyword_density':
            keyword = issue.get('keyword', '')
            keyword_optimizations.append({
                'keyword': keyword,
                'action': 'reduce_usage',
                'suggestion': f"减少'{keyword}'的使用频率，使用同义词替换",
                'target_density': '1.0-2.0%'
            })
    
    return {
        'content_expansions': content_expansions,
        'keyword_optimizations': keyword_optimizations,
        'expected_improvement': '+10-20 SEO分数',
        'implementation_priority': 'medium'
    }

def generate_technical_optimization(current_content, technical_issues, website_type):
    """生成技术SEO优化建议"""
    fixes = []
    
    for issue in technical_issues:
        if 'alt' in issue.get('type', '').lower():
            fixes.append({
                'type': 'add_alt_tags',
                'targets': ['all_images'],
                'steps': ['为每个图片添加描述性alt属性', '包含相关关键词'],
                'priority': 'medium'
            })
        elif 'link' in issue.get('type', '').lower():
            fixes.append({
                'type': 'optimize_links',
                'targets': ['internal_links', 'external_links'],
                'steps': ['优化链接锚文本', '确保链接相关性'],
                'priority': 'low'
            })
    
    return {
        'fixes': fixes,
        'expected_improvement': '+5-8 SEO分数',
        'implementation_priority': 'low'
    }

def calculate_implementation_time(mgx_actions):
    """计算实施时间估算"""
    time_mapping = {
        'update_title': 5,
        'update_meta_description': 5,
        'add_heading': 10,
        'expand_content': 30,
        'technical_fix': 15
    }
    
    total_minutes = sum(time_mapping.get(action.get('action_type'), 15) for action in mgx_actions)
    
    if total_minutes < 30:
        return 'less_than_30_minutes'
    elif total_minutes < 60:
        return '30_to_60_minutes'
    else:
        return 'more_than_1_hour'

def analyze_real_website(target_url, target_keywords, website_type):
    """分析真实网站并提取内容数据"""
    try:
        print(f"🔍 Starting real website analysis for: {target_url}")
        
        # 使用我们现有的analyze函数分析真实网站
        analysis_result = analyze(
            url=target_url,
            follow_links=False,  # 只分析主页
            analyze_headings=True,
            analyze_extra_tags=True,
            run_llm_analysis=False,  # 快速分析，不使用LLM
            run_professional_analysis=True  # 启用专业诊断
        )
        
        if not analysis_result or not analysis_result.get('pages'):
            return {'error': 'Failed to analyze website - no pages found'}
        
        page_data = analysis_result['pages'][0]
        
        # 提取内容数据
        current_content = {
            'title': page_data.get('title', ''),
            'description': page_data.get('description', ''),
            'content': page_data.get('content', {}).get('text', '') if page_data.get('content') else '',
            'headings': extract_headings_from_page(page_data),
            'meta_tags': {
                'keywords': ','.join(kw.get('keyword', '') for kw in page_data.get('keywords', [])[:5]),
                'author': page_data.get('author', ''),
                'url': target_url
            },
            'images': page_data.get('images', []),
            'links': {
                'internal': page_data.get('internal_links', []),
                'external': page_data.get('external_links', [])
            },
            'word_count': page_data.get('word_count', 0)
        }
        
        # 生成SEO分析
        seo_analysis = {
            'seo_score': 0,  # 将由统一评分系统计算
            'issues': [],
            'analysis_type': 'real_website_analysis',
            'timestamp': datetime.now().isoformat(),
            'url': target_url
        }
        
        # 使用统一评分系统
        unified_score = calculate_unified_seo_score(analysis_result)
        seo_analysis['seo_score'] = unified_score.get('score', 0)
        
        # 从专业诊断中提取问题
        professional_analysis = page_data.get('professional_analysis', {})
        if professional_analysis:
            all_issues = professional_analysis.get('all_issues', [])
            seo_analysis['issues'] = all_issues
            seo_analysis['professional_score'] = professional_analysis.get('overall_score', 0)
        
        # 如果没有提供目标关键词，从网站内容中提取
        if not target_keywords:
            extracted_keywords = [kw.get('keyword', '') for kw in page_data.get('keywords', [])[:5]]
            target_keywords = [kw for kw in extracted_keywords if kw]
        
        print(f"✅ Successfully analyzed {target_url}")
        print(f"📊 SEO Score: {seo_analysis['seo_score']:.1f}")
        print(f"🔍 Found {len(seo_analysis['issues'])} issues")
        print(f"🎯 Target keywords: {target_keywords}")
        
        return {
            'current_content': current_content,
            'seo_analysis': seo_analysis,
            'target_keywords': target_keywords,
            'analysis_metadata': {
                'analysis_time': datetime.now().isoformat(),
                'url': target_url,
                'content_length': len(current_content.get('content', '')),
                'keywords_found': len(target_keywords)
            }
        }
        
    except Exception as e:
        print(f"❌ Real website analysis error: {e}")
        return {'error': str(e)}

def extract_headings_from_page(page_data):
    """从页面数据中提取标题结构"""
    headings = []
    
    # 提取各级标题
    headings_data = page_data.get('headings', {})
    if isinstance(headings_data, dict):
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level_headings = headings_data.get(level, [])
            for heading in level_headings:
                if isinstance(heading, str):
                    headings.append(f"{level.upper()}: {heading}")
                elif isinstance(heading, dict):
                    heading_text = heading.get('text', heading.get('content', str(heading)))
                    headings.append(f"{level.upper()}: {heading_text}")
    
    # 如果没有找到标题，检查其他可能的字段
    if not headings:
        h1_tags = page_data.get('h1', [])
        h2_tags = page_data.get('h2', [])
        
        for h1 in h1_tags:
            headings.append(f"H1: {h1}")
        for h2 in h2_tags:
            headings.append(f"H2: {h2}")
    
    return headings

def assess_implementation_difficulty(mgx_actions):
    """评估实施难度"""
    difficulty_scores = {
        'update_title': 1,
        'update_meta_description': 1,
        'add_heading': 2,
        'expand_content': 3,
        'technical_fix': 2
    }
    
    avg_difficulty = sum(difficulty_scores.get(action.get('action_type'), 2) for action in mgx_actions) / len(mgx_actions) if mgx_actions else 1
    
    if avg_difficulty < 1.5:
        return 'easy'
    elif avg_difficulty < 2.5:
        return 'medium'
    else:
        return 'complex'

def calculate_optimization_impact(current_content, optimization_guide, seo_analysis):
    """计算优化影响评估"""
    current_score = seo_analysis.get('seo_score', 0)
    
    # 估算改进分数
    potential_improvements = {
        'title_optimization': 15,
        'description_optimization': 12,
        'content_structure': 10,
        'content_optimization': 20,
        'technical_optimization': 8
    }
    
    total_potential = sum(
        potential_improvements.get(category, 0) 
        for category in optimization_guide.get('priority_order', [])
    )
    
    expected_score = min(100, current_score + total_potential)
    
    return {
        'current_seo_score': current_score,
        'expected_seo_score': expected_score,
        'potential_improvement': total_potential,
        'score_grade_change': calculate_grade_change(current_score, expected_score),
        'impact_categories': {
            category: potential_improvements.get(category, 0)
            for category in optimization_guide.get('priority_order', [])
        },
        'confidence_level': 'high' if total_potential > 20 else 'medium'
    }

def calculate_grade_change(current_score, expected_score):
    """计算等级变化"""
    def score_to_grade(score):
        if score >= 90: return 'A+'
        elif score >= 80: return 'A'
        elif score >= 70: return 'B'
        elif score >= 60: return 'C'
        else: return 'D'
    
    current_grade = score_to_grade(current_score)
    expected_grade = score_to_grade(expected_score)
    
    return {
        'from': current_grade,
        'to': expected_grade,
        'improved': expected_grade != current_grade
    }

@app.route('/api/prompt/generate', methods=['POST'])
def generate_seo_prompt():
    """🚀 生成SEO内容优化prompt"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['url', 'optimization_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # 解析优化类型
        try:
            opt_type = OptimizationType(data['optimization_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid optimization_type. Valid options: {[t.value for t in OptimizationType]}'
            }), 400
        
        # 解析内容类型
        content_type = ContentType.HOMEPAGE  # 默认值
        if 'page_type' in data:
            try:
                content_type = ContentType(data['page_type'])
            except ValueError:
                pass
        
        # 构建SEO上下文
        seo_context = SEOContext(
            url=data['url'],
            domain=data.get('domain', data['url'].split('/')[2] if '/' in data['url'] else data['url']),
            page_type=content_type,
            current_score=data.get('current_score', 70.0),
            target_score=data.get('target_score', 90.0),
            industry=data.get('industry', 'General'),
            competitors=data.get('competitors', []),
            primary_keywords=data.get('primary_keywords', []),
            secondary_keywords=data.get('secondary_keywords', []),
            content_length=data.get('content_length', 1000),
            issues_detected=data.get('issues_detected', []),
            performance_metrics=data.get('performance_metrics', {'overall_score': 80}),
            user_intent=data.get('user_intent', 'informational')
        )
        
        # 生成prompt
        custom_requirements = data.get('custom_requirements', [])
        prompt = prompt_generator.generate_optimization_prompt(
            seo_context, 
            opt_type, 
            custom_requirements
        )
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'optimization_type': opt_type.value,
            'context_summary': {
                'url': seo_context.url,
                'page_type': seo_context.page_type.value,
                'current_score': seo_context.current_score,
                'target_score': seo_context.target_score,
                'primary_keywords': seo_context.primary_keywords
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate prompt: {str(e)}'
        }), 500

@app.route('/api/prompt/batch', methods=['POST'])
def generate_batch_prompts():
    """📦 批量生成多种类型的SEO优化prompt"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['url', 'optimization_types']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # 解析优化类型列表
        optimization_types = []
        for opt_type_str in data['optimization_types']:
            try:
                optimization_types.append(OptimizationType(opt_type_str))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Invalid optimization_type: {opt_type_str}. Valid options: {[t.value for t in OptimizationType]}'
                }), 400
        
        # 解析内容类型
        content_type = ContentType.HOMEPAGE
        if 'page_type' in data:
            try:
                content_type = ContentType(data['page_type'])
            except ValueError:
                pass
        
        # 构建SEO上下文
        seo_context = SEOContext(
            url=data['url'],
            domain=data.get('domain', data['url'].split('/')[2] if '/' in data['url'] else data['url']),
            page_type=content_type,
            current_score=data.get('current_score', 70.0),
            target_score=data.get('target_score', 90.0),
            industry=data.get('industry', 'General'),
            competitors=data.get('competitors', []),
            primary_keywords=data.get('primary_keywords', []),
            secondary_keywords=data.get('secondary_keywords', []),
            content_length=data.get('content_length', 1000),
            issues_detected=data.get('issues_detected', []),
            performance_metrics=data.get('performance_metrics', {'overall_score': 80}),
            user_intent=data.get('user_intent', 'informational')
        )
        
        # 批量生成prompts
        prompts = prompt_generator.generate_batch_prompts(seo_context, optimization_types)
        
        return jsonify({
            'success': True,
            'prompts': prompts,
            'total_prompts': len(prompts),
            'context_summary': {
                'url': seo_context.url,
                'page_type': seo_context.page_type.value,
                'current_score': seo_context.current_score,
                'target_score': seo_context.target_score
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate batch prompts: {str(e)}'
        }), 500

@app.route('/api/prompt/templates', methods=['GET'])
def get_prompt_templates():
    """📋 获取可用的prompt模板信息"""
    try:
        templates_info = {}
        for template_id, template in prompt_generator.templates.items():
            templates_info[template_id] = {
                'title': template.title,
                'optimization_type': template.optimization_type.value,
                'priority': template.priority.value,
                'context_requirements': template.context_requirements,
                'success_metrics': template.success_metrics,
                'examples': template.examples
            }
        
        return jsonify({
            'success': True,
            'templates': templates_info,
            'optimization_types': [t.value for t in OptimizationType],
            'content_types': [t.value for t in ContentType],
            'priority_levels': [p.value for p in PriorityLevel]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get templates: {str(e)}'
        }), 500

@app.route('/api/prompt/from-analysis', methods=['POST'])
def generate_prompt_from_analysis():
    """🔍 基于SEO分析结果生成优化prompt"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        if 'analysis_result' not in data or 'optimization_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: analysis_result, optimization_type'
            }), 400
        
        analysis_result = data['analysis_result']
        
        # 解析优化类型
        try:
            opt_type = OptimizationType(data['optimization_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid optimization_type. Valid options: {[t.value for t in OptimizationType]}'
            }), 400
        
        # 从分析结果中提取信息构建SEO上下文
        url = analysis_result.get('url', '')
        
        # 提取问题列表
        issues_detected = []
        if 'seo_analysis' in analysis_result:
            seo_analysis = analysis_result['seo_analysis']
            for category, issues in seo_analysis.get('issues', {}).items():
                for issue in issues:
                    issues_detected.append({
                        'title': issue.get('title', ''),
                        'description': issue.get('description', ''),
                        'priority': issue.get('priority', 'medium'),
                        'category': category
                    })
        
        # 提取关键词
        primary_keywords = []
        if 'keywords' in analysis_result:
            keywords_data = analysis_result['keywords']
            if isinstance(keywords_data, dict):
                # 如果keywords是字典格式
                primary_keywords = keywords_data.get('primary', [])
                if not primary_keywords:
                    # 如果没有primary字段，尝试其他可能的字段
                    for key in ['main', 'top', 'keywords']:
                        if key in keywords_data and isinstance(keywords_data[key], list):
                            primary_keywords = keywords_data[key][:5]
                            break
            elif isinstance(keywords_data, list):
                # 如果keywords是列表格式
                primary_keywords = keywords_data[:5]
            else:
                # 如果是其他格式，转换为列表
                primary_keywords = [str(keywords_data)] if keywords_data else []
        
        # 提取性能指标
        performance_metrics = {}
        if 'performance' in analysis_result:
            performance_metrics = analysis_result['performance']
        
        # 构建SEO上下文
        seo_context = SEOContext(
            url=url,
            domain=url.split('/')[2] if '/' in url else url,
            page_type=ContentType.HOMEPAGE,  # 可以根据URL路径智能判断
            current_score=analysis_result.get('overall_score', 70.0),
            target_score=data.get('target_score', 90.0),
            industry=data.get('industry', 'General'),
            competitors=data.get('competitors', []),
            primary_keywords=primary_keywords,
            secondary_keywords=data.get('secondary_keywords', []),
            content_length=analysis_result.get('content_length', 1000),
            issues_detected=issues_detected,
            performance_metrics=performance_metrics,
            user_intent=data.get('user_intent', 'informational')
        )
        
        # 生成prompt
        custom_requirements = data.get('custom_requirements', [])
        prompt = prompt_generator.generate_optimization_prompt(
            seo_context, 
            opt_type, 
            custom_requirements
        )
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'optimization_type': opt_type.value,
            'issues_count': len(issues_detected),
            'context_summary': {
                'url': seo_context.url,
                'current_score': seo_context.current_score,
                'target_score': seo_context.target_score,
                'primary_keywords': seo_context.primary_keywords,
                'issues_detected': len(issues_detected)
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate prompt from analysis: {str(e)}'
        }), 500

@app.route('/api/mgx/generate-optimization-plan', methods=['POST'])
def mgx_generate_optimization_plan():
    """
    🎯 MGX Ultra-Intelligent Optimization Plan Generator
    
    Analyzes HTML SEO reports and generates comprehensive, actionable optimization plans
    specifically designed for MGX system execution.
    
    Input:
    - html_report: Complete HTML SEO report content
    - analysis_data: Raw SEO analysis data
    - mgx_context: MGX-specific context and capabilities (optional)
    
    Output:
    - Complete MGX optimization plan with prompt specifications
    - Execution sequence and performance predictions
    - MGX-compatible action specifications
    """
    try:
        data = request.get_json()
        
        # Validate required parameters
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request data is required'
            }), 400
        
        # Check for required fields
        required_fields = ['analysis_data']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        analysis_data = data['analysis_data']
        html_report = data.get('html_report', '')  # Optional - can generate from analysis_data
        mgx_context = data.get('mgx_context', {})
        
        print("🎯 Generating MGX ultra-intelligent optimization plan...")
        
        # If no HTML report provided, generate a minimal one or work with analysis data directly
        if not html_report:
            print("📄 No HTML report provided, working directly with analysis data")
            # For now, we'll work with the analysis data directly
            # In the future, we could generate a minimal HTML structure if needed
        
        # Generate comprehensive MGX optimization plan
        optimization_plan = mgx_prompt_optimizer.generate_mgx_optimization_plan(
            html_report=html_report,
            analysis_data=analysis_data,
            mgx_context=mgx_context
        )
        
        # Export in MGX-compatible format
        mgx_export = mgx_prompt_optimizer.export_for_mgx(optimization_plan)
        
        # Create response
        response_data = {
            'optimization_plan': mgx_export,
            'summary': {
                'url': optimization_plan.url,
                'domain': optimization_plan.domain,
                'current_score': optimization_plan.current_seo_score,
                'target_score': optimization_plan.target_seo_score,
                'score_improvement': optimization_plan.target_seo_score - optimization_plan.current_seo_score,
                'total_optimizations': optimization_plan.total_optimizations,
                'estimated_completion_hours': optimization_plan.estimated_completion_time // 60,
                'mgx_compatibility_score': optimization_plan.mgx_compatibility_score
            },
            'execution_preview': {
                'critical_actions': len([p for p in optimization_plan.prompt_specifications 
                                       if p.priority.value == 'critical']),
                'high_priority_actions': len([p for p in optimization_plan.prompt_specifications 
                                            if p.priority.value == 'high']),
                'total_seo_impact': sum(p.seo_impact_score for p in optimization_plan.prompt_specifications),
                'first_three_actions': optimization_plan.execution_sequence[:3]
            }
        }
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': f'Generated {optimization_plan.total_optimizations} MGX-optimized prompts with {optimization_plan.mgx_compatibility_score:.1f}% compatibility score'
        })
        
    except Exception as e:
        print(f"❌ MGX optimization plan generation error: {e}")
        return jsonify({
            'success': False,
            'error': f'MGX optimization plan generation failed: {str(e)}'
        }), 500

@app.route('/api/mgx/prompt-specifications', methods=['POST'])
def mgx_get_prompt_specifications():
    """
    📋 MGX Prompt Specifications Extractor
    
    Extracts specific prompt specifications from analysis data for targeted MGX optimizations.
    """
    try:
        data = request.get_json()
        
        if not data or 'analysis_data' not in data:
            return jsonify({
                'success': False,
                'error': 'analysis_data is required'
            }), 400
        
        analysis_data = data['analysis_data']
        optimization_types = data.get('optimization_types', ['all'])  # Specific types or 'all'
        priority_filter = data.get('priority_filter')  # Optional priority filter
        
        print(f"📋 Extracting MGX prompt specifications for: {optimization_types}")
        
        # Generate optimization plan
        optimization_plan = mgx_prompt_optimizer.generate_mgx_optimization_plan(
            html_report='',  # Working with analysis data only
            analysis_data=analysis_data,
            mgx_context=data.get('mgx_context', {})
        )
        
        # Filter specifications based on request parameters
        filtered_specs = optimization_plan.prompt_specifications
        
        if optimization_types != ['all']:
            filtered_specs = [
                spec for spec in filtered_specs 
                if spec.action_type.value in optimization_types
            ]
        
        if priority_filter:
            filtered_specs = [
                spec for spec in filtered_specs 
                if spec.priority.value == priority_filter
            ]
        
        # Format specifications for MGX
        mgx_specifications = []
        for spec in filtered_specs:
            mgx_spec = {
                'action_type': spec.action_type.value,
                'priority': spec.priority.value,
                'target_element': spec.target_element,
                'optimization_goal': spec.optimization_goal,
                'specific_instructions': spec.specific_instructions,
                'success_metrics': spec.success_metrics,
                'seo_impact_score': spec.seo_impact_score,
                'estimated_effort_minutes': spec.estimated_effort_minutes,
                'mgx_context': spec.mgx_context,
                'implementation_notes': spec.implementation_notes
            }
            mgx_specifications.append(mgx_spec)
        
        return jsonify({
            'success': True,
            'data': {
                'prompt_specifications': mgx_specifications,
                'total_specifications': len(mgx_specifications),
                'filtered_from_total': len(optimization_plan.prompt_specifications),
                'optimization_types_requested': optimization_types,
                'priority_filter': priority_filter
            },
            'message': f'Extracted {len(mgx_specifications)} MGX prompt specifications'
        })
        
    except Exception as e:
        print(f"❌ MGX prompt specifications error: {e}")
        return jsonify({
            'success': False,
            'error': f'MGX prompt specifications extraction failed: {str(e)}'
        }), 500

@app.route('/api/mgx/action-types', methods=['GET'])
def mgx_get_action_types():
    """
    📋 MGX Available Action Types
    
    Returns all available MGX action types and their descriptions.
    """
    try:
        from pyseoanalyzer.mgx_prompt_optimizer import MGXActionType, OptimizationPriority
        
        action_types = {}
        for action in MGXActionType:
            action_types[action.value] = {
                'name': action.value,
                'description': action.name.replace('_', ' ').title(),
                'category': 'content' if 'content' in action.value or 'title' in action.value or 'description' in action.value 
                          else 'technical' if 'technical' in action.value or 'image' in action.value 
                          else 'strategic'
            }
        
        priorities = {}
        for priority in OptimizationPriority:
            priorities[priority.value] = {
                'name': priority.value,
                'description': priority.name.replace('_', ' ').title(),
                'urgency_level': 5 if priority.value == 'critical' else 
                               4 if priority.value == 'high' else
                               3 if priority.value == 'medium' else
                               2 if priority.value == 'low' else 1
            }
        
        return jsonify({
            'success': True,
            'data': {
                'action_types': action_types,
                'priority_levels': priorities,
                'categories': ['content', 'technical', 'strategic'],
                'total_action_types': len(action_types)
            },
            'message': f'Retrieved {len(action_types)} MGX action types and {len(priorities)} priority levels'
        })
        
    except Exception as e:
        print(f"❌ MGX action types error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve MGX action types: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Production-ready startup configuration for Render deployment
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Use PORT environment variable from Render, fallback to SEO_ANALYZER_PORT or 5000
    port = int(os.environ.get('PORT', os.environ.get('SEO_ANALYZER_PORT', 5000)))
    
    print(f"🚀 Starting SEO AutoPilot API server on port {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)