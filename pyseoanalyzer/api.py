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
    
def calculate_seo_score_detailed(analysis_result):
    """计算详细的SEO分数 - 使用加权算法"""
    if not analysis_result or not analysis_result.get('pages'):
        return {'score': 50, 'grade': 'D', 'status': 'needs_improvement'}
    
    page = analysis_result['pages'][0]
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
        grade = 'A+'
        status = 'excellent'
    elif score >= 80:
        grade = 'A'
        status = 'great'
    elif score >= 70:
        grade = 'B+'
        status = 'good'
    elif score >= 60:
        grade = 'B'
        status = 'fair'
    elif score >= 50:
        grade = 'C'
        status = 'needs_improvement'
    elif score >= 40:
        grade = 'D'
        status = 'poor'
    else:
        grade = 'F'
        status = 'critical'
    
    return {
        'score': score,
        'grade': grade,
        'status': status
    }

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

def generate_strategic_recommendations(analysis_result, seo_score_data, llm_analysis=None):
    """生成基于分析结果的智能战略建议 - 增强数据驱动版本"""
    if not analysis_result or not analysis_result.get('pages'):
        return []
    
    page = analysis_result['pages'][0]
    score = seo_score_data.get('score', 0)
    strategies = []
    
    # 获取专业诊断数据进行更精确的建议
    professional_analysis = page.get('professional_analysis', {})
    professional_score = professional_analysis.get('overall_score', score)
    category_scores = professional_analysis.get('category_scores', {})
    issues = professional_analysis.get('all_issues', [])
    
    # 基于专业分析的优先级问题
    critical_issues = [issue for issue in issues if issue.get('priority') == 'critical']
    high_issues = [issue for issue in issues if issue.get('priority') == 'high']
    
    # 动态生成基于实际数据的战略建议
    if professional_score >= 85:
        strategies.extend([
            {
                'category': 'Performance Excellence',
                'priority': 'medium',
                'strategy': f'Outstanding SEO performance ({professional_score:.1f}/100)! Focus on advanced optimization and competitive advantage.',
                'action': f'Implement structured data markup and optimize for featured snippets. Your content quality is strong.',
                'impact': 'high',
                'effort': 'medium',
                'data_point': f'Professional analysis shows {len(critical_issues)} critical issues remaining'
            },
            {
                'category': 'Market Leadership',
                'priority': 'low', 
                'strategy': 'Expand your topical authority to dominate search results in your niche.',
                'action': f'Create content clusters around your {len(page.get("keywords", [])[:3])} top keywords. Current word count: {page.get("word_count", 0)} words.',
                'impact': 'high',
                'effort': 'high',
                'data_point': f'Page has {page.get("word_count", 0)} words - excellent for content depth'
            }
        ])
    elif professional_score >= 70:
        strategies.extend([
            {
                'category': 'Strategic Enhancement',
                'priority': 'high',
                'strategy': f'Good SEO foundation ({professional_score:.1f}/100) with clear improvement opportunities.',
                'action': f'Address {len(critical_issues + high_issues)} priority issues identified in professional analysis.',
                'impact': 'high', 
                'effort': 'medium',
                'data_point': f'Fixing these issues could boost score by 10-15 points'
            }
        ])
    else:
        strategies.extend([
            {
                'category': 'Foundation Repair',
                'priority': 'critical',
                'strategy': f'SEO needs immediate attention ({professional_score:.1f}/100). Focus on high-impact fixes first.',
                'action': f'Start with {len(critical_issues)} critical issues: {", ".join([issue.get("title", "Unknown") for issue in critical_issues[:3]])}',
                'impact': 'very_high',
                'effort': 'low',
                'data_point': f'Quick wins available - these fixes require minimal effort'
            }
        ])
    
    # 基于具体检测到的问题生成数据驱动的建议
    title = page.get('title', '')
    description = page.get('description', '')
    word_count = page.get('word_count', 0)
    
    # 标题优化 - 基于实际数据
    if not title:
        strategies.append({
            'category': 'Critical SEO Fix',
            'priority': 'critical',
            'strategy': 'Missing title tag is costing you significant organic traffic.',
            'action': f'Add a 50-60 character title tag. Suggested: Include your main keyword from the {word_count} words analyzed.',
            'impact': 'very_high',
            'effort': 'low',
            'data_point': 'Title tags influence 35% of ranking factors'
        })
    elif len(title) < 30:
        strategies.append({
            'category': 'Title Enhancement',
            'priority': 'high', 
            'strategy': f'Title "{title[:30]}..." is {30-len(title)} characters too short.',
            'action': f'Expand to 50-60 characters. Current: {len(title)} chars. Add relevant keywords from your content.',
            'impact': 'high',
            'effort': 'low',
            'data_point': f'Longer titles get 2.5x more clicks than short ones'
        })
    elif len(title) > 60:
        strategies.append({
            'category': 'Title Optimization',
            'priority': 'medium',
            'strategy': f'Title is {len(title)-60} characters too long and may be truncated.',
            'action': f'Trim to 60 characters max. Focus on your most important keyword first.',
            'impact': 'medium', 
            'effort': 'low',
            'data_point': f'Search engines truncate titles after 60 characters'
        })
    
    # 描述优化 - 基于实际数据
    if not description:
        strategies.append({
            'category': 'Meta Description Critical',
            'priority': 'critical',
            'strategy': 'Missing meta description lets search engines write poor snippets.',
            'action': f'Write 140-160 character description with a clear call-to-action. Use insights from your {word_count} word content.',
            'impact': 'high',
            'effort': 'low',
            'data_point': 'Meta descriptions influence 15% of click-through rates'
        })
    elif len(description) < 120:
        strategies.append({
            'category': 'Description Enhancement',
            'priority': 'high',
            'strategy': f'Description is {120-len(description)} characters too short to be effective.',
            'action': f'Expand from {len(description)} to 140-160 characters. Add benefits and call-to-action.',
            'impact': 'medium',
            'effort': 'low', 
            'data_point': 'Longer descriptions get 30% better click-through rates'
        })
    
    # 内容深度建议 - 基于词汇分析
    if word_count < 300:
        strategies.append({
            'category': 'Content Depth',
            'priority': 'high',
            'strategy': f'Content is thin with only {word_count} words. Search engines prefer comprehensive content.',
            'action': f'Expand to 500+ words. Add {500-word_count} more words with relevant subtopics and examples.',
            'impact': 'high',
            'effort': 'medium',
            'data_point': f'Pages with 500+ words rank 53% higher than thin content'
        })
    elif word_count > 2000:
        strategies.append({
            'category': 'Content Organization',
            'priority': 'medium',
            'strategy': f'Excellent content depth ({word_count} words). Focus on structure and readability.',
            'action': 'Add more H2/H3 headings, bullet points, and visual elements to break up text.',
            'impact': 'medium',
            'effort': 'low',
            'data_point': f'Well-structured long content gets 25% more engagement'
        })
    
    # 基于专业诊断的具体技术建议
    if category_scores:
        for category, score_data in category_scores.items():
            if isinstance(score_data, dict) and score_data.get('score', 100) < 60:
                category_name = category.replace('_', ' ').title()
                strategies.append({
                    'category': f'{category_name} Fix',
                    'priority': 'high',
                    'strategy': f'{category_name} score is low ({score_data.get("score", 0):.1f}/100) with {score_data.get("issues_found", 0)} issues.',
                    'action': f'Address {score_data.get("critical_issues", 0)} critical {category_name.lower()} issues first.',
                    'impact': 'high',
                    'effort': 'medium',
                    'data_point': f'Fixing these could improve overall score by {(100-score_data.get("score", 0))*0.2:.1f} points'
                })
    
    # LLM分析增强建议
    if llm_analysis:
        llm_recommendations = llm_analysis.get('recommendations', [])
        for rec in llm_recommendations[:2]:  # 取前2个最重要的LLM建议
            if isinstance(rec, dict):
                strategies.append({
                    'category': 'AI-Powered Insight',
                    'priority': 'medium',
                    'strategy': f'AI analysis suggests: {rec.get("insight", "Advanced optimization opportunity")}',
                    'action': rec.get('action', 'Review AI recommendations for specific implementation steps'),
                    'impact': 'medium',
                    'effort': 'medium',
                    'data_point': 'Based on advanced content and competitive analysis'
                })
    
    # 按优先级和影响力排序
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    impact_order = {'very_high': 0, 'high': 1, 'medium': 2, 'low': 3}
    
    strategies.sort(key=lambda x: (
        priority_order.get(x.get('priority', 'medium'), 2),
        impact_order.get(x.get('impact', 'medium'), 2)
    ))
    
    return strategies[:8]  # 限制返回最重要的8个建议

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
        
        # 第一阶段：基础分析（支持LLM分析和专业诊断）
        run_llm_analysis = data.get('run_llm_analysis', True)  # 默认启用LLM分析
        run_professional_analysis = data.get('run_professional_analysis', True)  # 默认启用专业诊断
        analysis_result = analyze(
            url=url,
            sitemap_url=data.get('sitemap'),
            follow_links=False,  # 禁用链接跟踪以提高速度
            analyze_headings=True,
            analyze_extra_tags=True,
            run_llm_analysis=run_llm_analysis,  # 启用SiliconFlow API分析
            run_professional_analysis=run_professional_analysis  # 启用专业诊断分析
        )
        
        # 第二阶段：计算基础指标（轻量级）
        seo_score = calculate_seo_score_detailed(analysis_result)
        
        # 第三阶段：生成核心建议（优化版本）
        recommendations = generate_quick_recommendations(analysis_result)
        
        # 第四阶段：生成智能战略建议
        strategic_recommendations = generate_strategic_recommendations(
            analysis_result, 
            seo_score, 
            analysis_result.get('llm_analysis')
        )
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 返回优化后的结果
        result = {
            'analysis': analysis_result,
            'seo_score': seo_score,
            'recommendations': recommendations,
            'strategic_recommendations': strategic_recommendations,
            'performance': {
                'execution_time': round(execution_time, 2),
                'optimized': True
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
            
            # 组装完整的分析数据
            seo_score = calculate_seo_score_detailed(analysis_result)
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # 根据环境变量决定是否启用调试模式
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('SEO_ANALYZER_PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)