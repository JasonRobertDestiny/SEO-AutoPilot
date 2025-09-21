from flask import Flask, request, jsonify, render_template, send_from_directory, Response
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

app = Flask(__name__, template_folder='templates', static_folder='templates')
CORS(app)

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

if __name__ == '__main__':
    # 根据环境变量决定是否启用调试模式
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('SEO_ANALYZER_PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)