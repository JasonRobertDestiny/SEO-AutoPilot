"""
SEO Analysis Report Generator

This module provides comprehensive report generation for SEO analysis results,
supporting multiple output formats including HTML, PDF, JSON, and CSV.
"""

import json
import csv
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64

# Optional PDF support - gracefully handle missing dependencies
try:
    from weasyprint import HTML, CSS
    PDF_SUPPORT = True
except (ImportError, OSError) as e:
    PDF_SUPPORT = False
    # Only print warning if explicitly trying to use PDF functionality
    # print(f"Note: PDF support not available: {e}")


class SEOReportGenerator:
    """Generates comprehensive SEO analysis reports in multiple formats."""
    
    def __init__(self):
        self.supported_formats = ['html', 'json', 'csv', 'txt']
        if PDF_SUPPORT:
            self.supported_formats.append('pdf')
    
    def generate_report(self, analysis_data: Dict[str, Any], format_type: str = 'html') -> Dict[str, Any]:
        """
        Generate a comprehensive SEO report in the specified format.
        
        Args:
            analysis_data: Complete SEO analysis results
            format_type: Output format ('html', 'json', 'csv', 'txt')
            
        Returns:
            Dictionary containing report content and metadata
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.supported_formats}")
        
        # Prepare consolidated data
        report_data = self._prepare_report_data(analysis_data)
        
        # Generate report based on format
        if format_type == 'html':
            content = self._generate_html_report(report_data)
            mimetype = 'text/html'
        elif format_type == 'pdf':
            if not PDF_SUPPORT:
                raise ValueError(
                    "PDF support not available. WeasyPrint requires additional system dependencies. "
                    "For Windows users: Consider using HTML format instead, or install GTK+ libraries. "
                    "See: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation"
                )
            content = self._generate_pdf_report(report_data)
            mimetype = 'application/pdf'
        elif format_type == 'json':
            content = self._generate_json_report(report_data)
            mimetype = 'application/json'
        elif format_type == 'csv':
            content = self._generate_csv_report(report_data)
            mimetype = 'text/csv'
        elif format_type == 'txt':
            content = self._generate_txt_report(report_data)
            mimetype = 'text/plain'
        
        return {
            'content': content,
            'filename': self._generate_filename(report_data.get('url', 'unknown'), format_type),
            'mimetype': mimetype,
            'format': format_type,
            'generated_at': datetime.now().isoformat()
        }
    
    def _prepare_report_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and consolidate analysis data for comprehensive reporting."""
        url = analysis_data.get('url', 'Unknown URL')
        
        # Calculate overall SEO score using detailed algorithm
        seo_score = self._calculate_overall_score(analysis_data)
        
        # Extract all available data sources
        basic_metrics = analysis_data.get('basic_seo_analysis', {})
        llm_analysis = analysis_data.get('llm_analysis', {})
        professional_analysis = analysis_data.get('professional_analysis', {})
        pagespeed_insights = analysis_data.get('pagespeed_insights', {})
        trends_insights = analysis_data.get('trends_insights', {})
        enhanced_llm_analysis = analysis_data.get('enhanced_llm_analysis', {})
        
        # Process pages data if available
        pages_data = analysis_data.get('pages', [])
        if pages_data:
            # Use first page data and aggregate if multiple pages
            first_page = pages_data[0]
            basic_metrics = basic_metrics or first_page
            
            # Extract professional analysis from page if not at root level
            if not professional_analysis and 'professional_analysis' in first_page:
                professional_analysis = first_page['professional_analysis']
        
        # Consolidate recommendations from all sources
        recommendations = self._consolidate_comprehensive_recommendations(
            basic_metrics, llm_analysis, professional_analysis, 
            pagespeed_insights, trends_insights, enhanced_llm_analysis
        )
        
        # Identify critical issues from all sources
        critical_issues = self._identify_comprehensive_critical_issues(
            basic_metrics, professional_analysis, pagespeed_insights
        )
        
        # Generate strategic roadmap
        strategic_roadmap = self._generate_strategic_roadmap(
            seo_score, recommendations, critical_issues
        )
        
        # Analyze performance metrics
        performance_summary = self._analyze_performance_metrics(pagespeed_insights)
        
        # Process trends analysis
        trends_summary = self._process_trends_analysis(trends_insights)
        
        return {
            'url': url,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'seo_score': seo_score,
            'grade': self._get_grade_from_score(seo_score),
            'basic_metrics': basic_metrics,
            'llm_analysis': llm_analysis,
            'professional_analysis': professional_analysis,
            'pagespeed_insights': pagespeed_insights,
            'trends_insights': trends_insights,
            'enhanced_llm_analysis': enhanced_llm_analysis,
            'performance_summary': performance_summary,
            'trends_summary': trends_summary,
            'recommendations': recommendations,
            'critical_issues': critical_issues,
            'strategic_roadmap': strategic_roadmap,
            'summary': self._generate_comprehensive_executive_summary(
                seo_score, critical_issues, recommendations, 
                performance_summary, trends_summary
            )
        }
    
    def _calculate_overall_score(self, analysis_data: Dict[str, Any]) -> float:
        """🎯 UNIFIED SEO SCORE CALCULATION - Use same logic as API unified scoring system
        
        Priority order:
        1. Backend unified seo_score (most accurate)
        2. Professional diagnostics overall_score 
        3. Basic weighted calculation (fallback)
        
        This ensures reports show the same score as frontend and strategy generators.
        """
        # 🥇 PRIORITY 1: Use Backend Unified Score if available
        if 'seo_score' in analysis_data:
            score_data = analysis_data['seo_score']
            if isinstance(score_data, dict) and score_data.get('score') is not None:
                score = float(score_data['score'])
                print(f"📊 Report using unified backend score: {score:.1f} (source: {score_data.get('source', 'backend')})")
                return round(score, 1)
            elif isinstance(score_data, (int, float)) and score_data > 0:
                score = float(score_data)
                print(f"📊 Report using numeric backend score: {score:.1f}")
                return round(score, 1)
        
        # 🥈 PRIORITY 2: Use Professional Diagnostics Score
        professional_analysis = analysis_data.get('professional_analysis', {})
        if professional_analysis and professional_analysis.get('overall_score') is not None:
            score = float(professional_analysis['overall_score'])
            print(f"📊 Report using professional diagnostics score: {score:.1f}")
            return round(score, 1)
        
        # 🥉 PRIORITY 3: Fallback to basic calculation (legacy compatibility)
        print("⚠️ Report falling back to basic calculation - consider using unified scoring")
        basic_analysis = analysis_data.get('basic_seo_analysis', {})
        
        scores = []
        weights = {}
        
        # Title score (weight: 20%)
        if 'title' in basic_analysis:
            title_text = basic_analysis.get('title', '')
            title_length = len(title_text) if title_text else 0
            if 50 <= title_length <= 60:
                scores.append(100)
            elif 30 <= title_length <= 70:
                scores.append(80)
            else:
                scores.append(40)
            weights['title'] = 0.20
        
        # Description score (weight: 15%)
        if 'description' in basic_analysis:
            desc_text = basic_analysis.get('description', '')
            desc_length = len(desc_text) if desc_text else 0
            if 140 <= desc_length <= 160:
                scores.append(100)
            elif 120 <= desc_length <= 180:
                scores.append(80)
            else:
                scores.append(40)
            weights['description'] = 0.15
        
        # Headings score (weight: 15%)
        headings = basic_analysis.get('headings', {})
        h1_count = len(headings.get('h1', [])) if headings else 0
        if h1_count == 1:
            scores.append(100)
        elif h1_count == 0:
            scores.append(20)
        else:
            scores.append(60)
        weights['headings'] = 0.15
        
        # Images score - use warnings to determine missing alt tags (weight: 10%)
        warnings = basic_analysis.get('warnings', [])
        image_warnings = [w for w in warnings if 'Image missing alt tag' in str(w)]
        if len(image_warnings) == 0:
            scores.append(100)  # No missing alt tags
        elif len(image_warnings) <= 2:
            scores.append(70)   # Few missing alt tags
        else:
            scores.append(30)   # Many missing alt tags
        weights['images'] = 0.10
        
        # Content score (weight: 25%)
        word_count = basic_analysis.get('word_count', 0)
        if word_count >= 300:
            scores.append(100)
        elif word_count >= 150:
            scores.append(80)
        elif word_count >= 50:
            scores.append(60)
        else:
            scores.append(30)
        weights['content'] = 0.25
        
        # Links score - based on warnings about insufficient content (weight: 15%)
        # This is a simplified approach since link data isn't in the basic structure
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
                return round(weighted_score, 1)
        
        return 0.0
    
    def _get_grade_from_score(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _consolidate_recommendations(self, basic_metrics: Dict, llm_analysis: Dict) -> List[Dict[str, str]]:
        """Consolidate recommendations from all analysis sources."""
        recommendations = []
        
        # Basic SEO recommendations
        if 'title' in basic_metrics:
            title_text = basic_metrics.get('title', '')
            title_length = len(title_text) if title_text else 0
            if title_length < 30:
                recommendations.append({
                    'category': 'Title Optimization',
                    'priority': 'High',
                    'issue': 'Title tag is too short',
                    'recommendation': 'Expand title to 50-60 characters for better search visibility'
                })
            elif title_length > 60:
                recommendations.append({
                    'category': 'Title Optimization',
                    'priority': 'High',
                    'issue': 'Title tag is too long',
                    'recommendation': 'Shorten title to 50-60 characters to prevent truncation'
                })
        
        if 'description' in basic_metrics:
            desc_text = basic_metrics.get('description', '')
            desc_length = len(desc_text) if desc_text else 0
            if desc_length < 120:
                recommendations.append({
                    'category': 'Meta Description',
                    'priority': 'Medium',
                    'issue': 'Meta description is too short',
                    'recommendation': 'Expand meta description to 140-160 characters for better CTR'
                })
            elif desc_length > 160:
                recommendations.append({
                    'category': 'Meta Description',
                    'priority': 'Medium',
                    'issue': 'Meta description is too long',
                    'recommendation': 'Shorten meta description to prevent truncation in search results'
                })
        
        # Image optimization - based on warnings
        warnings = basic_metrics.get('warnings', [])
        image_warnings = [w for w in warnings if 'Image missing alt tag' in str(w)]
        if image_warnings:
            recommendations.append({
                'category': 'Image Optimization',
                'priority': 'Medium',
                'issue': f'{len(image_warnings)} images missing alt attributes',
                'recommendation': 'Add descriptive alt text to all images for accessibility and SEO'
            })
        
        # Content recommendations
        word_count = basic_metrics.get('word_count', 0)
        if word_count < 150:
            recommendations.append({
                'category': 'Content Quality',
                'priority': 'High',
                'issue': 'Low word count',
                'recommendation': 'Increase content length to at least 300 words for better search rankings'
            })
        
        # Heading structure recommendations
        headings = basic_metrics.get('headings', {})
        h1_count = len(headings.get('h1', [])) if headings else 0
        if h1_count == 0:
            recommendations.append({
                'category': 'Content Structure',
                'priority': 'High',
                'issue': 'Missing H1 tag',
                'recommendation': 'Add a single H1 tag as the main heading for the page'
            })
        elif h1_count > 1:
            recommendations.append({
                'category': 'Content Structure',
                'priority': 'Medium',
                'issue': 'Multiple H1 tags found',
                'recommendation': 'Use only one H1 tag per page and use H2-H6 for subheadings'
            })
        
        # LLM-based recommendations
        if llm_analysis and 'recommendations' in llm_analysis:
            llm_recs = llm_analysis['recommendations']
            if isinstance(llm_recs, list):
                for rec in llm_recs[:5]:  # Limit to top 5 LLM recommendations
                    recommendations.append({
                        'category': 'AI Analysis',
                        'priority': 'Medium',
                        'issue': rec.get('issue', 'AI-identified improvement area'),
                        'recommendation': rec.get('recommendation', str(rec))
                    })
        
        return recommendations
    
    def _identify_critical_issues(self, basic_metrics: Dict) -> List[Dict[str, str]]:
        """Identify critical SEO issues that need immediate attention."""
        issues = []
        
        # Missing title
        title_text = basic_metrics.get('title', '')
        if not title_text:
            issues.append({
                'type': 'Missing Title Tag',
                'severity': 'Critical',
                'description': 'No title tag found - essential for search rankings'
            })
        
        # Missing description
        desc_text = basic_metrics.get('description', '')
        if not desc_text:
            issues.append({
                'type': 'Missing Meta Description',
                'severity': 'High',
                'description': 'No meta description found - important for click-through rates'
            })
        
        # No H1 tags
        headings = basic_metrics.get('headings', {})
        h1_tags = headings.get('h1', []) if headings else []
        if not h1_tags:
            issues.append({
                'type': 'Missing H1 Tag',
                'severity': 'High',
                'description': 'No H1 heading found - important for content structure'
            })
        
        # Multiple H1 tags
        elif len(h1_tags) > 1:
            issues.append({
                'type': 'Multiple H1 Tags',
                'severity': 'Medium',
                'description': f"{len(h1_tags)} H1 tags found - should have only one per page"
            })
        
        # Low content
        word_count = basic_metrics.get('word_count', 0)
        if word_count < 100:
            issues.append({
                'type': 'Insufficient Content',
                'severity': 'High',
                'description': f'Very low word count ({word_count} words) - content may be too thin'
            })
        
        # Image alt tag issues
        warnings = basic_metrics.get('warnings', [])
        image_warnings = [w for w in warnings if 'Image missing alt tag' in str(w)]
        if len(image_warnings) > 3:
            issues.append({
                'type': 'Multiple Missing Alt Tags',
                'severity': 'Medium',
                'description': f'{len(image_warnings)} images missing alt attributes - impacts accessibility'
            })
        
        return issues
    
    def _generate_executive_summary(self, score: float, issues: List, recommendations: List) -> str:
        """Generate an executive summary of the SEO analysis."""
        grade = self._get_grade_from_score(score)
        
        summary = f"This website received an overall SEO score of {score}/100 (Grade: {grade}). "
        
        if score >= 80:
            summary += "The website demonstrates strong SEO fundamentals with minor areas for improvement. "
        elif score >= 60:
            summary += "The website has a solid SEO foundation but several areas need attention. "
        else:
            summary += "The website requires significant SEO improvements to achieve better search rankings. "
        
        critical_issues = [issue for issue in issues if issue.get('severity') == 'Critical']
        high_issues = [issue for issue in issues if issue.get('severity') == 'High']
        
        if critical_issues:
            summary += f"There are {len(critical_issues)} critical issues that require immediate attention. "
        
        if high_issues:
            summary += f"Additionally, {len(high_issues)} high-priority issues should be addressed soon. "
        
        summary += f"A total of {len(recommendations)} specific recommendations have been provided to improve search performance."
        
        return summary
    
    def _generate_filename(self, url: str, format_type: str) -> str:
        """Generate appropriate filename for the report."""
        # Clean URL for filename
        clean_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '')
        if len(clean_url) > 50:
            clean_url = clean_url[:50]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"seo_report_{clean_url}_{timestamp}.{format_type}"
    
    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate a comprehensive HTML report."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Analysis Report - {url}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
            color: #2d3748;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 8px solid rgba(255,255,255,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            font-size: 32px;
            font-weight: bold;
            background: rgba(255,255,255,0.1);
        }}
        .grade-{grade_lower} {{
            border-color: {grade_color};
            color: {grade_color};
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 20px;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 24px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2d3748;
        }}
        .metric-label {{
            color: #718096;
            font-size: 14px;
            margin-top: 5px;
        }}
        .issue-list, .rec-list {{
            list-style: none;
            padding: 0;
        }}
        .issue-item, .rec-item {{
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e53e3e;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .rec-item {{
            border-left-color: #38a169;
        }}
        .priority-high {{
            border-left-color: #e53e3e;
        }}
        .priority-medium {{
            border-left-color: #dd6b20;
        }}
        .priority-low {{
            border-left-color: #38a169;
        }}
        .summary-box {{
            background: #ebf8ff;
            border: 1px solid #bee3f8;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .timestamp {{
            text-align: center;
            color: #718096;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
        .chart-container {{
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        .score-excellent {{ background: #10b981; }}
        .score-good {{ background: #f59e0b; }}
        .score-poor {{ background: #ef4444; }}
        .metric-trend {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }}
        .trend-up {{ color: #10b981; }}
        .trend-down {{ color: #ef4444; }}
        .trend-stable {{ color: #6b7280; }}
        .visualization-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .chart-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .donut-chart {{
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
        }}
        .performance-meter {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 15px 0;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
        }}
        .meter-label {{ font-weight: 600; color: #2d3748; }}
        .meter-value {{ font-size: 18px; font-weight: bold; }}
        .roadmap-timeline {{
            position: relative;
            padding-left: 30px;
        }}
        .roadmap-timeline::before {{
            content: '';
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #667eea;
        }}
        .timeline-item {{
            position: relative;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -37px;
            top: 25px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #667eea;
        }}
        .timeline-phase {{
            color: #667eea;
            font-weight: bold;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SEO Analysis Report</h1>
            <p>{url}</p>
            <div class="score-circle grade-{grade_lower}">
                {seo_score}
            </div>
            <div>Grade: {grade}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="summary-box">
                    {summary}
                </div>
            </div>
            
            <div class="section">
                <h2>Key Metrics</h2>
                <div class="metric-grid">
                    {metrics_html}
                </div>
            </div>
            
            {critical_issues_html}
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul class="rec-list">
                    {recommendations_html}
                </ul>
            </div>
            
            {llm_analysis_html}
            
            {enhanced_llm_html}
            
            {performance_html}
            
            {trends_html}
            
            {professional_html}
            
            {roadmap_html}
            
            {competitive_html}
            
            {content_strategy_html}
            
            <div class="timestamp">
                Report generated on {analysis_date} by SEO AutoPilot
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Determine grade color
        grade_colors = {
            'a+': '#10b981', 'a': '#10b981', 'b': '#f59e0b',
            'c': '#ef4444', 'd': '#ef4444', 'f': '#991b1b'
        }
        grade_color = grade_colors.get(data['grade'].lower(), '#6b7280')
        
        # Generate metrics HTML
        metrics_html = self._generate_metrics_html(data['basic_metrics'])
        
        # Generate critical issues HTML
        critical_issues_html = ""
        if data['critical_issues']:
            issues_html = ""
            for issue in data['critical_issues']:
                severity_class = f"priority-{issue.get('severity', 'medium').lower()}"
                issues_html += f"""
                <li class="issue-item {severity_class}">
                    <strong>{issue.get('type', 'Issue')}</strong> ({issue.get('severity', 'Medium')} Priority)
                    <br>{issue.get('description', '')}
                </li>
                """
            critical_issues_html = f"""
            <div class="section">
                <h2>Critical Issues</h2>
                <ul class="issue-list">
                    {issues_html}
                </ul>
            </div>
            """
        
        # Generate recommendations HTML
        recommendations_html = ""
        for rec in data['recommendations'][:10]:  # Limit to top 10
            priority_class = f"priority-{rec.get('priority', 'medium').lower()}"
            recommendations_html += f"""
            <li class="rec-item {priority_class}">
                <strong>{rec.get('category', 'General')}</strong> ({rec.get('priority', 'Medium')} Priority)
                <br><strong>Issue:</strong> {rec.get('issue', '')}
                <br><strong>Recommendation:</strong> {rec.get('recommendation', '')}
            </li>
            """
        
        # Generate LLM analysis HTML
        llm_analysis_html = ""
        if data['llm_analysis']:
            llm_content = self._generate_llm_analysis_html(data['llm_analysis'])
            if llm_content:
                llm_analysis_html = f"""
                <div class="section">
                    <h2>AI-Powered Analysis</h2>
                    {llm_content}
                </div>
                """
        
        # Generate enhanced LLM analysis HTML
        enhanced_llm_html = ""
        if data.get('enhanced_llm_analysis'):
            enhanced_content = self._generate_enhanced_llm_html(data['enhanced_llm_analysis'])
            if enhanced_content:
                enhanced_llm_html = f"""
                <div class="section">
                    <h2>Strategic AI Insights</h2>
                    {enhanced_content}
                </div>
                """
        
        # Generate performance analysis HTML
        performance_html = ""
        if data.get('performance_summary') and data['performance_summary'].get('status') == 'analyzed':
            performance_content = self._generate_performance_html(data['performance_summary'], data.get('pagespeed_insights', {}))
            performance_html = f"""
            <div class="section">
                <h2>Performance Analysis</h2>
                {performance_content}
            </div>
            """
        
        # Generate trends analysis HTML
        trends_html = ""
        if data.get('trends_summary') and data['trends_summary'].get('status') == 'analyzed':
            trends_content = self._generate_trends_html(data['trends_summary'], data.get('trends_insights', {}))
            trends_html = f"""
            <div class="section">
                <h2>Keyword Trends Analysis</h2>
                {trends_content}
            </div>
            """
        
        # Generate strategic roadmap HTML
        roadmap_html = ""
        if data.get('strategic_roadmap'):
            roadmap_content = self._generate_roadmap_html(data['strategic_roadmap'])
            roadmap_html = f"""
            <div class="section">
                <h2>Strategic Implementation Roadmap</h2>
                {roadmap_content}
            </div>
            """
        
        # Generate professional analysis HTML
        professional_html = ""
        if data.get('professional_analysis'):
            professional_content = self._generate_professional_analysis_html(data['professional_analysis'])
            if professional_content:
                professional_html = f"""
                <div class="section">
                    <h2>Professional SEO Diagnostics</h2>
                    {professional_content}
                </div>
                """
        
        # Generate competitive analysis HTML
        competitive_html = f"""
        <div class="section">
            <h2>Competitive Analysis</h2>
            {self._generate_competitive_analysis_html(data)}
        </div>
        """
        
        # Generate content strategy HTML
        content_strategy_html = f"""
        <div class="section">
            <h2>Content Strategy</h2>
            {self._generate_content_strategy_html(data)}
        </div>
        """
        
        return html_template.format(
            url=data['url'],
            seo_score=data['seo_score'],
            grade=data['grade'],
            grade_lower=data['grade'].lower().replace('+', ''),
            grade_color=grade_color,
            summary=data['summary'],
            metrics_html=metrics_html,
            critical_issues_html=critical_issues_html,
            recommendations_html=recommendations_html,
            llm_analysis_html=llm_analysis_html,
            enhanced_llm_html=enhanced_llm_html,
            performance_html=performance_html,
            trends_html=trends_html,
            professional_html=professional_html,
            roadmap_html=roadmap_html,
            competitive_html=competitive_html,
            content_strategy_html=content_strategy_html,
            analysis_date=data['analysis_date']
        )
    
    def _generate_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for key metrics display with enhanced visualizations."""
        metrics_html = """
        <div class="visualization-grid">
        """
        
        # Title metrics with progress bar
        if 'title' in metrics:
            title_text = metrics.get('title', '')
            title_length = len(title_text) if title_text else 0
            title_score = 100 if 50 <= title_length <= 60 else 80 if 30 <= title_length <= 70 else 40
            title_class = "score-excellent" if title_score >= 80 else "score-good" if title_score >= 60 else "score-poor"
            
            metrics_html += f"""
            <div class="chart-card">
                <div class="metric-value">{title_length} chars</div>
                <div class="metric-label">Title Length</div>
                <div class="progress-bar">
                    <div class="progress-fill {title_class}" style="width: {title_score}%"></div>
                </div>
                <div class="metric-trend">
                    <span>Score: {title_score}/100</span>
                    <span class="{'trend-up' if title_score >= 80 else 'trend-down' if title_score < 60 else 'trend-stable'}">
                        {'↗' if title_score >= 80 else '↘' if title_score < 60 else '→'}
                    </span>
                </div>
            </div>
            """
        
        # Description metrics with progress bar
        if 'description' in metrics:
            desc_text = metrics.get('description', '')
            desc_length = len(desc_text) if desc_text else 0
            desc_score = 100 if 140 <= desc_length <= 160 else 80 if 120 <= desc_length <= 180 else 40
            desc_class = "score-excellent" if desc_score >= 80 else "score-good" if desc_score >= 60 else "score-poor"
            
            metrics_html += f"""
            <div class="chart-card">
                <div class="metric-value">{desc_length} chars</div>
                <div class="metric-label">Meta Description Length</div>
                <div class="progress-bar">
                    <div class="progress-fill {desc_class}" style="width: {desc_score}%"></div>
                </div>
                <div class="metric-trend">
                    <span>Score: {desc_score}/100</span>
                    <span class="{'trend-up' if desc_score >= 80 else 'trend-down' if desc_score < 60 else 'trend-stable'}">
                        {'↗' if desc_score >= 80 else '↘' if desc_score < 60 else '→'}
                    </span>
                </div>
            </div>
            """
        
        # Headings structure visualization
        headings = metrics.get('headings', {})
        h1_count = len(headings.get('h1', [])) if headings else 0
        total_headings = 0
        if headings:
            total_headings = sum(len(headings.get(f'h{i}', [])) for i in range(1, 7))
        
        heading_score = 100 if h1_count == 1 else 20 if h1_count == 0 else 60
        heading_class = "score-excellent" if heading_score >= 80 else "score-good" if heading_score >= 60 else "score-poor"
        
        metrics_html += f"""
        <div class="chart-card">
            <div class="metric-value">{h1_count}</div>
            <div class="metric-label">H1 Tags</div>
            <div class="progress-bar">
                <div class="progress-fill {heading_class}" style="width: {heading_score}%"></div>
            </div>
            <div class="metric-trend">
                <span>Total Headings: {total_headings}</span>
                <span class="{'trend-up' if heading_score >= 80 else 'trend-down' if heading_score < 60 else 'trend-stable'}">
                    {'↗' if heading_score >= 80 else '↘' if heading_score < 60 else '→'}
                </span>
            </div>
        </div>
        """
        
        # Word count with donut chart representation
        word_count = metrics.get('word_count', 0)
        word_score = 100 if word_count >= 300 else 80 if word_count >= 150 else 60 if word_count >= 50 else 30
        word_class = "score-excellent" if word_score >= 80 else "score-good" if word_score >= 60 else "score-poor"
        
        # Calculate percentage for donut chart (based on 500 words as ideal)
        word_percentage = min(100, (word_count / 500) * 100) if word_count > 0 else 0
        
        metrics_html += f"""
        <div class="chart-card">
            <div class="donut-chart">
                <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="10"/>
                    <circle cx="60" cy="60" r="50" fill="none" stroke="{'#10b981' if word_score >= 80 else '#f59e0b' if word_score >= 60 else '#ef4444'}" 
                            stroke-width="10" stroke-dasharray="{word_percentage * 3.14159:.1f} 314.159" 
                            stroke-dashoffset="78.54" transform="rotate(-90 60 60)"/>
                    <text x="60" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#2d3748">{word_count}</text>
                </svg>
            </div>
            <div class="metric-label">Word Count</div>
            <div class="metric-trend">
                <span>Content Depth: {word_percentage:.0f}%</span>
                <span class="{'trend-up' if word_score >= 80 else 'trend-down' if word_score < 60 else 'trend-stable'}">
                    {'↗' if word_score >= 80 else '↘' if word_score < 60 else '→'}
                </span>
            </div>
        </div>
        """
        
        # SEO Issues overview
        warnings = metrics.get('warnings', [])
        warning_count = len(warnings) if warnings else 0
        issue_score = 100 if warning_count == 0 else 70 if warning_count <= 2 else 40 if warning_count <= 5 else 20
        issue_class = "score-excellent" if issue_score >= 80 else "score-good" if issue_score >= 60 else "score-poor"
        
        metrics_html += f"""
        <div class="chart-card">
            <div class="metric-value">{warning_count}</div>
            <div class="metric-label">SEO Issues</div>
            <div class="progress-bar">
                <div class="progress-fill {issue_class}" style="width: {issue_score}%"></div>
            </div>
            <div class="metric-trend">
                <span>Health Score: {issue_score}/100</span>
                <span class="{'trend-up' if issue_score >= 80 else 'trend-down' if issue_score < 60 else 'trend-stable'}">
                    {'↗' if issue_score >= 80 else '↘' if issue_score < 60 else '→'}
                </span>
            </div>
        </div>
        """
        
        metrics_html += "</div>"
        return metrics_html
    
    def _generate_llm_analysis_html(self, llm_data: Dict[str, Any]) -> str:
        """Generate HTML for LLM analysis section."""
        html = ""
        
        if 'entity_optimization' in llm_data:
            entity_score = llm_data['entity_optimization'].get('score', 'N/A')
            html += f"""
            <div class="metric-card">
                <strong>Entity Optimization Score:</strong> {entity_score}
                <p>{llm_data['entity_optimization'].get('analysis', '')}</p>
            </div>
            """
        
        if 'credibility_analysis' in llm_data:
            credibility_score = llm_data['credibility_analysis'].get('score', 'N/A')
            html += f"""
            <div class="metric-card">
                <strong>Credibility Score:</strong> {credibility_score}
                <p>{llm_data['credibility_analysis'].get('analysis', '')}</p>
            </div>
            """
        
        if 'conversational_readiness' in llm_data:
            conv_score = llm_data['conversational_readiness'].get('score', 'N/A')
            html += f"""
            <div class="metric-card">
                <strong>Conversational Search Readiness:</strong> {conv_score}
                <p>{llm_data['conversational_readiness'].get('analysis', '')}</p>
            </div>
            """
        
        return html
    
    def _generate_json_report(self, data: Dict[str, Any]) -> str:
        """Generate a JSON report."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _generate_csv_report(self, data: Dict[str, Any]) -> str:
        """Generate a CSV report."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['SEO Analysis Report'])
        writer.writerow(['URL', data['url']])
        writer.writerow(['Analysis Date', data['analysis_date']])
        writer.writerow(['SEO Score', data['seo_score']])
        writer.writerow(['Grade', data['grade']])
        writer.writerow([])
        
        # Metrics
        writer.writerow(['Metric', 'Value'])
        basic_metrics = data['basic_metrics']
        
        if 'title' in basic_metrics:
            title_text = basic_metrics.get('title', '')
            writer.writerow(['Title Length', len(title_text) if title_text else 0])
        if 'description' in basic_metrics:
            desc_text = basic_metrics.get('description', '')
            writer.writerow(['Description Length', len(desc_text) if desc_text else 0])
        
        headings = basic_metrics.get('headings', {})
        h1_count = len(headings.get('h1', [])) if headings else 0
        writer.writerow(['H1 Count', h1_count])
        
        word_count = basic_metrics.get('word_count', 0)
        writer.writerow(['Word Count', word_count])
        
        warnings = basic_metrics.get('warnings', [])
        writer.writerow(['SEO Warnings', len(warnings) if warnings else 0])
        writer.writerow([])
        
        # Critical Issues
        if data['critical_issues']:
            writer.writerow(['Critical Issues'])
            writer.writerow(['Type', 'Severity', 'Description'])
            for issue in data['critical_issues']:
                writer.writerow([
                    issue.get('type', ''),
                    issue.get('severity', ''),
                    issue.get('description', '')
                ])
            writer.writerow([])
        
        # Recommendations
        writer.writerow(['Recommendations'])
        writer.writerow(['Category', 'Priority', 'Issue', 'Recommendation'])
        for rec in data['recommendations']:
            writer.writerow([
                rec.get('category', ''),
                rec.get('priority', ''),
                rec.get('issue', ''),
                rec.get('recommendation', '')
            ])
        
        return output.getvalue()
    
    def _generate_txt_report(self, data: Dict[str, Any]) -> str:
        """Generate a plain text report."""
        lines = []
        lines.append("="*60)
        lines.append("SEO ANALYSIS REPORT")
        lines.append("="*60)
        lines.append(f"URL: {data['url']}")
        lines.append(f"Analysis Date: {data['analysis_date']}")
        lines.append(f"SEO Score: {data['seo_score']}/100 (Grade: {data['grade']})")
        lines.append("")
        
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-"*40)
        lines.append(data['summary'])
        lines.append("")
        
        # Key Metrics
        lines.append("KEY METRICS")
        lines.append("-"*40)
        basic_metrics = data['basic_metrics']
        
        if 'title' in basic_metrics:
            title_text = basic_metrics.get('title', '')
            lines.append(f"Title Length: {len(title_text) if title_text else 0} characters")
        if 'description' in basic_metrics:
            desc_text = basic_metrics.get('description', '')
            lines.append(f"Description Length: {len(desc_text) if desc_text else 0} characters")
        
        headings = basic_metrics.get('headings', {})
        h1_count = len(headings.get('h1', [])) if headings else 0
        lines.append(f"H1 Tags: {h1_count}")
        
        word_count = basic_metrics.get('word_count', 0)
        lines.append(f"Word Count: {word_count}")
        
        warnings = basic_metrics.get('warnings', [])
        lines.append(f"SEO Warnings: {len(warnings) if warnings else 0}")
        lines.append("")
        
        # Critical Issues
        if data['critical_issues']:
            lines.append("CRITICAL ISSUES")
            lines.append("-"*40)
            for i, issue in enumerate(data['critical_issues'], 1):
                lines.append(f"{i}. {issue.get('type', '')} ({issue.get('severity', '')})")
                lines.append(f"   {issue.get('description', '')}")
            lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-"*40)
        for i, rec in enumerate(data['recommendations'], 1):
            lines.append(f"{i}. {rec.get('category', '')} ({rec.get('priority', '')} Priority)")
            lines.append(f"   Issue: {rec.get('issue', '')}")
            lines.append(f"   Recommendation: {rec.get('recommendation', '')}")
            lines.append("")
        
        lines.append("="*60)
        lines.append("Report generated by SEO Genius")
        
        return "\n".join(lines)
    
    def _consolidate_comprehensive_recommendations(self, basic_metrics: Dict, llm_analysis: Dict, 
                                                 professional_analysis: Dict, pagespeed_insights: Dict,
                                                 trends_insights: Dict, enhanced_llm_analysis: Dict) -> List[Dict[str, str]]:
        """Consolidate recommendations from all analysis sources for comprehensive reporting."""
        recommendations = []
        
        # Start with basic recommendations
        basic_recs = self._consolidate_recommendations(basic_metrics, llm_analysis)
        recommendations.extend(basic_recs)
        
        # Add professional diagnostics recommendations
        if professional_analysis and 'recommendations' in professional_analysis:
            prof_recs = professional_analysis['recommendations']
            if isinstance(prof_recs, list):
                for rec in prof_recs[:10]:  # Limit to top 10
                    if isinstance(rec, dict):
                        recommendations.append({
                            'category': rec.get('category', 'Professional Analysis'),
                            'priority': rec.get('priority', 'Medium'),
                            'issue': rec.get('title', rec.get('issue', 'Professional analysis recommendation')),
                            'recommendation': rec.get('description', rec.get('recommendation', str(rec))),
                            'source': 'professional_diagnostics'
                        })
        
        # Add PageSpeed insights recommendations
        if pagespeed_insights:
            mobile_recs = pagespeed_insights.get('mobile', {}).get('recommendations', [])
            desktop_recs = pagespeed_insights.get('desktop', {}).get('recommendations', [])
            
            for rec in mobile_recs[:5]:  # Top 5 mobile recommendations
                if isinstance(rec, dict):
                    recommendations.append({
                        'category': 'Mobile Performance',
                        'priority': rec.get('priority', 'Medium'),
                        'issue': rec.get('title', 'Mobile performance issue'),
                        'recommendation': rec.get('description', str(rec)),
                        'source': 'pagespeed_mobile'
                    })
            
            for rec in desktop_recs[:5]:  # Top 5 desktop recommendations
                if isinstance(rec, dict):
                    recommendations.append({
                        'category': 'Desktop Performance',
                        'priority': rec.get('priority', 'Medium'),
                        'issue': rec.get('title', 'Desktop performance issue'),
                        'recommendation': rec.get('description', str(rec)),
                        'source': 'pagespeed_desktop'
                    })
        
        # Add trends-based recommendations
        if trends_insights and 'content_opportunities' in trends_insights:
            content_opps = trends_insights['content_opportunities']
            if isinstance(content_opps, list):
                for opp in content_opps[:3]:  # Top 3 content opportunities
                    recommendations.append({
                        'category': 'Content Strategy',
                        'priority': 'Medium',
                        'issue': 'Content opportunity identified',
                        'recommendation': f"Consider creating content around: {opp}",
                        'source': 'trends_analysis'
                    })
        
        # Add enhanced LLM recommendations
        if enhanced_llm_analysis and 'strategic_priorities' in enhanced_llm_analysis:
            strategic_priorities = enhanced_llm_analysis['strategic_priorities']
            if isinstance(strategic_priorities, list):
                for priority in strategic_priorities[:5]:  # Top 5 strategic priorities
                    recommendations.append({
                        'category': 'Strategic Planning',
                        'priority': 'High',
                        'issue': 'Strategic opportunity',
                        'recommendation': str(priority),
                        'source': 'enhanced_llm'
                    })
        
        # Sort by priority and deduplicate
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'Medium'), 2))
        
        # Remove duplicates based on recommendation text
        seen_recommendations = set()
        unique_recommendations = []
        for rec in recommendations:
            rec_text = rec.get('recommendation', '')
            if rec_text not in seen_recommendations:
                seen_recommendations.add(rec_text)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:20]  # Limit to top 20 recommendations
    
    def _identify_comprehensive_critical_issues(self, basic_metrics: Dict, 
                                              professional_analysis: Dict, 
                                              pagespeed_insights: Dict) -> List[Dict[str, str]]:
        """Identify critical issues from all analysis sources."""
        issues = []
        
        # Start with basic critical issues
        basic_issues = self._identify_critical_issues(basic_metrics)
        issues.extend(basic_issues)
        
        # Add professional diagnostics critical issues
        if professional_analysis and 'critical_issues' in professional_analysis:
            prof_issues = professional_analysis['critical_issues']
            if isinstance(prof_issues, list):
                for issue in prof_issues:
                    if isinstance(issue, dict):
                        issues.append({
                            'type': issue.get('category', 'Professional Analysis Issue'),
                            'severity': issue.get('severity', 'High'),
                            'description': issue.get('description', issue.get('title', str(issue))),
                            'source': 'professional_diagnostics'
                        })
        
        # Add performance critical issues
        if pagespeed_insights:
            mobile_performance = pagespeed_insights.get('mobile', {}).get('analysis', {})
            desktop_performance = pagespeed_insights.get('desktop', {}).get('analysis', {})
            
            # Check mobile performance
            mobile_score = mobile_performance.get('performance_score', 100)
            if mobile_score < 50:
                issues.append({
                    'type': 'Poor Mobile Performance',
                    'severity': 'Critical',
                    'description': f'Mobile performance score is critically low ({mobile_score}/100)',
                    'source': 'pagespeed_mobile'
                })
            
            # Check desktop performance
            desktop_score = desktop_performance.get('performance_score', 100)
            if desktop_score < 50:
                issues.append({
                    'type': 'Poor Desktop Performance',
                    'severity': 'Critical',
                    'description': f'Desktop performance score is critically low ({desktop_score}/100)',
                    'source': 'pagespeed_desktop'
                })
            
            # Check Core Web Vitals
            mobile_cwv = mobile_performance.get('core_web_vitals', {})
            if mobile_cwv.get('lcp', 0) > 4000:  # LCP > 4s is poor
                issues.append({
                    'type': 'Poor Largest Contentful Paint',
                    'severity': 'High',
                    'description': f'LCP is {mobile_cwv.get("lcp", 0)/1000:.1f}s (should be < 2.5s)',
                    'source': 'core_web_vitals'
                })
            
            if mobile_cwv.get('cls', 0) > 0.25:  # CLS > 0.25 is poor
                issues.append({
                    'type': 'Poor Cumulative Layout Shift',
                    'severity': 'High',
                    'description': f'CLS is {mobile_cwv.get("cls", 0):.3f} (should be < 0.1)',
                    'source': 'core_web_vitals'
                })
        
        # Sort by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        issues.sort(key=lambda x: severity_order.get(x.get('severity', 'Medium'), 2))
        
        return issues[:15]  # Limit to top 15 critical issues
    
    def _generate_strategic_roadmap(self, seo_score: float, recommendations: List, 
                                  critical_issues: List) -> Dict[str, Any]:
        """Generate a strategic 30/60/90-day roadmap based on analysis."""
        roadmap = {
            'immediate_actions': [],  # 0-30 days
            'short_term_goals': [],   # 30-60 days
            'long_term_strategy': []  # 60-90 days
        }
        
        # Immediate actions (0-30 days) - Critical issues and high-priority quick wins
        critical_count = len([issue for issue in critical_issues if issue.get('severity') == 'Critical'])
        high_priority_recs = [rec for rec in recommendations if rec.get('priority') in ['Critical', 'High']]
        
        roadmap['immediate_actions'] = [
            f"Fix {critical_count} critical issues immediately" if critical_count > 0 else "Monitor critical metrics",
            "Implement top 3 high-priority recommendations",
            "Optimize title tags and meta descriptions",
            "Fix missing alt attributes on images",
            "Ensure proper H1 tag structure"
        ]
        
        # Short-term goals (30-60 days) - Medium priority optimizations
        medium_priority_recs = [rec for rec in recommendations if rec.get('priority') == 'Medium']
        
        roadmap['short_term_goals'] = [
            "Improve page loading speed (Core Web Vitals)",
            "Expand content length and quality",
            "Optimize internal linking structure",
            "Implement schema markup",
            "Enhance mobile user experience"
        ]
        
        # Long-term strategy (60-90 days) - Strategic improvements
        roadmap['long_term_strategy'] = [
            "Develop comprehensive content strategy",
            "Build authoritative backlink profile",
            "Implement advanced technical SEO",
            "Create topic clusters and pillar pages",
            "Monitor and iterate based on performance data"
        ]
        
        # Customize based on SEO score
        if seo_score < 50:
            roadmap['immediate_actions'].insert(0, "Address fundamental SEO issues")
            roadmap['short_term_goals'].insert(0, "Establish basic SEO foundation")
        elif seo_score < 70:
            roadmap['immediate_actions'].insert(0, "Optimize existing content")
            roadmap['short_term_goals'].insert(0, "Enhance technical implementation")
        else:
            roadmap['immediate_actions'].insert(0, "Fine-tune high-performing elements")
            roadmap['short_term_goals'].insert(0, "Focus on advanced optimizations")
        
        return roadmap
    
    def _analyze_performance_metrics(self, pagespeed_insights: Dict) -> Dict[str, Any]:
        """Analyze and summarize performance metrics from PageSpeed Insights."""
        if not pagespeed_insights:
            return {'status': 'no_data', 'summary': 'No performance data available'}
        
        mobile_data = pagespeed_insights.get('mobile', {}).get('analysis', {})
        desktop_data = pagespeed_insights.get('desktop', {}).get('analysis', {})
        
        summary = {
            'mobile_score': mobile_data.get('performance_score', 0),
            'desktop_score': desktop_data.get('performance_score', 0),
            'mobile_cwv': mobile_data.get('core_web_vitals', {}),
            'desktop_cwv': desktop_data.get('core_web_vitals', {}),
            'status': 'analyzed'
        }
        
        # Determine overall performance status
        avg_score = (summary['mobile_score'] + summary['desktop_score']) / 2
        if avg_score >= 90:
            summary['performance_status'] = 'excellent'
        elif avg_score >= 75:
            summary['performance_status'] = 'good'
        elif avg_score >= 50:
            summary['performance_status'] = 'needs_improvement'
        else:
            summary['performance_status'] = 'poor'
        
        # Generate performance summary text
        summary['summary'] = f"Overall performance: {summary['performance_status'].title()} (Mobile: {summary['mobile_score']}/100, Desktop: {summary['desktop_score']}/100)"
        
        return summary
    
    def _process_trends_analysis(self, trends_insights: Dict) -> Dict[str, Any]:
        """Process and summarize trends analysis data."""
        if not trends_insights:
            return {'status': 'no_data', 'summary': 'No trends data available'}
        
        analysis_summary = trends_insights.get('analysis_summary', {})
        content_opportunities = trends_insights.get('content_opportunities', [])
        
        summary = {
            'analyzed_keywords': analysis_summary.get('analyzed_keywords', 0),
            'rising_trends': analysis_summary.get('rising_trends', 0),
            'falling_trends': analysis_summary.get('falling_trends', 0),
            'stable_trends': analysis_summary.get('stable_trends', 0),
            'content_opportunities_count': len(content_opportunities),
            'top_opportunities': content_opportunities[:5] if content_opportunities else [],
            'status': 'analyzed'
        }
        
        # Generate trends summary text
        if summary['analyzed_keywords'] > 0:
            summary['summary'] = f"Analyzed {summary['analyzed_keywords']} keywords: {summary['rising_trends']} rising, {summary['stable_trends']} stable, {summary['falling_trends']} declining trends. {summary['content_opportunities_count']} content opportunities identified."
        else:
            summary['summary'] = "No keyword trends data available for analysis"
        
        return summary
    
    def _generate_comprehensive_executive_summary(self, score: float, issues: List, 
                                                recommendations: List, performance_summary: Dict,
                                                trends_summary: Dict) -> str:
        """Generate an enhanced executive summary incorporating all analysis components."""
        grade = self._get_grade_from_score(score)
        
        summary = f"This comprehensive SEO analysis reveals an overall score of {score}/100 (Grade: {grade}). "
        
        # Overall assessment
        if score >= 85:
            summary += "The website demonstrates excellent SEO implementation with advanced optimization opportunities available. "
        elif score >= 70:
            summary += "The website shows strong SEO fundamentals with several areas for strategic improvement. "
        elif score >= 50:
            summary += "The website has a foundation for SEO but requires significant improvements across multiple areas. "
        else:
            summary += "The website needs comprehensive SEO restructuring to achieve competitive search rankings. "
        
        # Critical issues assessment
        critical_issues = [issue for issue in issues if issue.get('severity') == 'Critical']
        high_issues = [issue for issue in issues if issue.get('severity') == 'High']
        
        if critical_issues:
            summary += f"{len(critical_issues)} critical issues require immediate attention. "
        if high_issues:
            summary += f"{len(high_issues)} high-priority issues should be addressed within 30 days. "
        
        # Performance assessment
        if performance_summary.get('status') == 'analyzed':
            perf_status = performance_summary.get('performance_status', 'unknown')
            summary += f"Website performance is {perf_status}. "
        
        # Trends assessment
        if trends_summary.get('status') == 'analyzed':
            rising_trends = trends_summary.get('rising_trends', 0)
            if rising_trends > 0:
                summary += f"{rising_trends} rising keyword trends present content opportunities. "
        
        # Recommendations summary
        total_recs = len(recommendations)
        summary += f"This report provides {total_recs} specific, actionable recommendations organized into a strategic 90-day implementation roadmap for measurable SEO improvement."
        
        return summary
    
    def _generate_enhanced_llm_html(self, enhanced_llm_data: Dict[str, Any]) -> str:
        """Generate HTML for enhanced LLM analysis section."""
        html = ""
        
        if 'strategic_priorities' in enhanced_llm_data:
            priorities = enhanced_llm_data['strategic_priorities']
            if isinstance(priorities, list) and priorities:
                html += f"""
                <div class="metric-card">
                    <strong>Strategic Priorities:</strong>
                    <ul>
                """
                for priority in priorities[:5]:
                    html += f"<li>{priority}</li>"
                html += "</ul></div>"
        
        if 'opportunity_areas' in enhanced_llm_data:
            opportunities = enhanced_llm_data['opportunity_areas']
            if isinstance(opportunities, list) and opportunities:
                html += f"""
                <div class="metric-card">
                    <strong>Opportunity Areas:</strong>
                    <ul>
                """
                for opp in opportunities[:5]:
                    html += f"<li>{opp}</li>"
                html += "</ul></div>"
        
        if 'quick_wins' in enhanced_llm_data:
            quick_wins = enhanced_llm_data['quick_wins']
            if isinstance(quick_wins, list) and quick_wins:
                html += f"""
                <div class="metric-card">
                    <strong>Quick Wins:</strong>
                    <ul>
                """
                for win in quick_wins[:3]:
                    html += f"<li>{win}</li>"
                html += "</ul></div>"
        
        return html
    
    def _generate_performance_html(self, performance_summary: Dict[str, Any], pagespeed_insights: Dict[str, Any]) -> str:
        """Generate HTML for performance analysis section."""
        html = f"""
        <div class="summary-box">
            <p><strong>Performance Summary:</strong> {performance_summary.get('summary', 'No performance data available')}</p>
        </div>
        <div class="metric-grid">
        """
        
        # Mobile and Desktop scores
        mobile_score = performance_summary.get('mobile_score', 0)
        desktop_score = performance_summary.get('desktop_score', 0)
        
        html += f"""
        <div class="metric-card">
            <div class="metric-value">{mobile_score}</div>
            <div class="metric-label">Mobile Performance Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{desktop_score}</div>
            <div class="metric-label">Desktop Performance Score</div>
        </div>
        """
        
        # Core Web Vitals
        mobile_cwv = performance_summary.get('mobile_cwv', {})
        if mobile_cwv:
            lcp = mobile_cwv.get('lcp', 0)
            cls = mobile_cwv.get('cls', 0)
            fcp = mobile_cwv.get('fcp', 0)
            
            html += f"""
            <div class="metric-card">
                <div class="metric-value">{lcp/1000:.1f}s</div>
                <div class="metric-label">Largest Contentful Paint</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{cls:.3f}</div>
                <div class="metric-label">Cumulative Layout Shift</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{fcp/1000:.1f}s</div>
                <div class="metric-label">First Contentful Paint</div>
            </div>
            """
        
        html += "</div>"
        
        # Performance recommendations
        mobile_recs = pagespeed_insights.get('mobile', {}).get('recommendations', [])
        if mobile_recs:
            html += """
            <h3>Performance Optimization Recommendations</h3>
            <ul class="rec-list">
            """
            for rec in mobile_recs[:5]:
                if isinstance(rec, dict):
                    title = rec.get('title', 'Performance optimization')
                    description = rec.get('description', str(rec))
                    html += f"""
                    <li class="rec-item">
                        <strong>{title}</strong>
                        <br>{description}
                    </li>
                    """
            html += "</ul>"
        
        return html
    
    def _generate_trends_html(self, trends_summary: Dict[str, Any], trends_insights: Dict[str, Any]) -> str:
        """Generate HTML for trends analysis section."""
        html = f"""
        <div class="summary-box">
            <p><strong>Trends Summary:</strong> {trends_summary.get('summary', 'No trends data available')}</p>
        </div>
        <div class="metric-grid">
        """
        
        # Trends metrics
        analyzed_keywords = trends_summary.get('analyzed_keywords', 0)
        rising_trends = trends_summary.get('rising_trends', 0)
        stable_trends = trends_summary.get('stable_trends', 0)
        falling_trends = trends_summary.get('falling_trends', 0)
        
        html += f"""
        <div class="metric-card">
            <div class="metric-value">{analyzed_keywords}</div>
            <div class="metric-label">Keywords Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{rising_trends}</div>
            <div class="metric-label">Rising Trends</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{stable_trends}</div>
            <div class="metric-label">Stable Trends</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{falling_trends}</div>
            <div class="metric-label">Declining Trends</div>
        </div>
        """
        
        html += "</div>"
        
        # Content opportunities
        opportunities = trends_summary.get('top_opportunities', [])
        if opportunities:
            html += """
            <h3>Content Opportunities</h3>
            <ul class="rec-list">
            """
            for opp in opportunities:
                html += f"""
                <li class="rec-item">
                    <strong>Content Opportunity:</strong> {opp}
                </li>
                """
            html += "</ul>"
        
        return html
    
    def _generate_roadmap_html(self, roadmap: Dict[str, Any]) -> str:
        """Generate HTML for strategic roadmap section with timeline visualization."""
        html = """
        <div class="roadmap-timeline">
        """
        
        # Immediate actions (0-30 days)
        immediate = roadmap.get('immediate_actions', [])
        html += f"""
        <div class="timeline-item">
            <div class="timeline-phase">Phase 1: Immediate Actions (0-30 days)</div>
            <h4 style="color: #e53e3e; margin-bottom: 15px;">🚨 Critical Priority</h4>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for action in immediate[:5]:
            html += f"<li style='margin-bottom: 8px;'>{action}</li>"
        html += """
            </ul>
            <div class="performance-meter" style="margin-top: 15px;">
                <span class="meter-label">Expected Impact:</span>
                <span class="meter-value" style="color: #e53e3e;">High</span>
            </div>
        </div>
        """
        
        # Short-term goals (30-60 days)
        short_term = roadmap.get('short_term_goals', [])
        html += f"""
        <div class="timeline-item">
            <div class="timeline-phase">Phase 2: Short-term Goals (30-60 days)</div>
            <h4 style="color: #f59e0b; margin-bottom: 15px;">⚡ Medium Priority</h4>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for goal in short_term[:5]:
            html += f"<li style='margin-bottom: 8px;'>{goal}</li>"
        html += """
            </ul>
            <div class="performance-meter" style="margin-top: 15px;">
                <span class="meter-label">Expected Impact:</span>
                <span class="meter-value" style="color: #f59e0b;">Medium</span>
            </div>
        </div>
        """
        
        # Long-term strategy (60-90 days)
        long_term = roadmap.get('long_term_strategy', [])
        html += f"""
        <div class="timeline-item">
            <div class="timeline-phase">Phase 3: Long-term Strategy (60-90 days)</div>
            <h4 style="color: #10b981; margin-bottom: 15px;">🎯 Strategic Focus</h4>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for strategy in long_term[:5]:
            html += f"<li style='margin-bottom: 8px;'>{strategy}</li>"
        html += """
            </ul>
            <div class="performance-meter" style="margin-top: 15px;">
                <span class="meter-label">Expected Impact:</span>
                <span class="meter-value" style="color: #10b981;">Sustainable Growth</span>
            </div>
        </div>
        """
        
        html += "</div>"
        
        # Add progress tracking section
        html += """
        <div class="chart-container" style="margin-top: 30px;">
            <h4>Implementation Progress Tracker</h4>
            <div class="performance-meter">
                <span class="meter-label">Phase 1 (Critical)</span>
                <div style="flex: 1; margin: 0 15px;">
                    <div class="progress-bar">
                        <div class="progress-fill score-poor" style="width: 0%"></div>
                    </div>
                </div>
                <span class="meter-value">0%</span>
            </div>
            <div class="performance-meter">
                <span class="meter-label">Phase 2 (Medium)</span>
                <div style="flex: 1; margin: 0 15px;">
                    <div class="progress-bar">
                        <div class="progress-fill score-good" style="width: 0%"></div>
                    </div>
                </div>
                <span class="meter-value">0%</span>
            </div>
            <div class="performance-meter">
                <span class="meter-label">Phase 3 (Strategic)</span>
                <div style="flex: 1; margin: 0 15px;">
                    <div class="progress-bar">
                        <div class="progress-fill score-excellent" style="width: 0%"></div>
                    </div>
                </div>
                <span class="meter-value">0%</span>
            </div>
        </div>
        """
        
        return html
    
    def _generate_professional_analysis_html(self, professional_analysis: Dict[str, Any]) -> str:
        """Generate HTML for professional analysis section."""
        html = ""
        
        # Overall score
        overall_score = professional_analysis.get('overall_score', 0)
        if overall_score:
            html += f"""
            <div class="summary-box">
                <p><strong>Professional Analysis Score:</strong> {overall_score:.1f}/100</p>
            </div>
            """
        
        # Category scores
        category_scores = professional_analysis.get('category_scores', {})
        if category_scores:
            html += """
            <div class="metric-grid">
            """
            for category, score in category_scores.items():
                html += f"""
                <div class="metric-card">
                    <div class="metric-value">{score:.1f}</div>
                    <div class="metric-label">{category.replace('_', ' ').title()}</div>
                </div>
                """
            html += "</div>"
        
        # Top issues
        critical_issues = professional_analysis.get('critical_issues', [])
        if critical_issues:
            html += """
            <h3>Professional Diagnostic Issues</h3>
            <ul class="issue-list">
            """
            for issue in critical_issues[:5]:
                if isinstance(issue, dict):
                    severity_class = f"priority-{issue.get('severity', 'medium').lower()}"
                    html += f"""
                    <li class="issue-item {severity_class}">
                        <strong>{issue.get('title', 'Professional Issue')}</strong> ({issue.get('severity', 'Medium')} Priority)
                        <br>{issue.get('description', '')}
                    </li>
                    """
            html += "</ul>"
        
        return html    
    def _generate_competitive_analysis_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for competitive analysis section."""
        html = """
        <h3>Competitive Positioning Analysis</h3>
        <div class="metric-grid">
        """
        
        # Extract SEO score for competitive context
        seo_score = data.get("seo_score", 0)
        
        # Competitive position based on score
        if seo_score >= 85:
            competitive_status = "Market Leader"
            competitive_color = "#10b981"
            competitive_desc = "Your website demonstrates market-leading SEO practices with competitive advantages."
        elif seo_score >= 70:
            competitive_status = "Strong Competitor"
            competitive_color = "#f59e0b"
            competitive_desc = "Your website is well-positioned but has opportunities to gain competitive advantages."
        elif seo_score >= 50:
            competitive_status = "Catching Up"
            competitive_color = "#ef4444"
            competitive_desc = "Your website needs improvements to compete effectively in search results."
        else:
            competitive_status = "Behind Competition"
            competitive_color = "#991b1b"
            competitive_desc = "Significant SEO improvements are needed to compete effectively."
        
        html += f"""
        <div class="metric-card" style="border-left-color: {competitive_color}">
            <div class="metric-value" style="color: {competitive_color}">{competitive_status}</div>
            <div class="metric-label">Competitive Position</div>
            <p style="margin-top: 10px; font-size: 14px;">{competitive_desc}</p>
        </div>
        """
        
        # Add competitive sections HTML
        html += self._generate_content_strategy_html(data)
        
        html += "</div>"
        return html
    
    def _generate_content_strategy_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for content strategy section."""
        basic_metrics = data.get("basic_metrics", {})
        word_count = basic_metrics.get("word_count", 0)
        
        html = f"""
        <div class="metric-card">
            <h4>Content Strategy</h4>
            <p>Current content: {word_count} words</p>
            <ul>
                <li>Expand content for better rankings</li>
                <li>Create topic clusters</li>
                <li>Develop content calendar</li>
                <li>Focus on user intent</li>
            </ul>
        </div>
        """
        return html
    
    def _generate_pdf_report(self, data: Dict[str, Any]) -> bytes:
        """Generate a PDF report from HTML content."""
        if not PDF_SUPPORT:
            raise ValueError(
                "PDF support not available. WeasyPrint requires additional system dependencies. "
                "For Windows users: Consider using HTML format instead, or install GTK+ libraries. "
                "See: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation"
            )
        
        # Generate HTML content first
        html_content = self._generate_html_report(data)
        
        # Custom CSS for PDF optimization
        pdf_css = CSS(string="""
            @page {
                size: A4;
                margin: 1in;
            }
            
            body {
                font-size: 11pt;
                line-height: 1.4;
            }
            
            .container {
                max-width: 100%;
                box-shadow: none;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            .score-circle {
                page-break-inside: avoid;
            }
            
            .section {
                page-break-inside: avoid;
                margin-bottom: 20pt;
            }
            
            .chart-card, .metric-card {
                page-break-inside: avoid;
                margin-bottom: 15pt;
            }
            
            .roadmap-timeline {
                page-break-inside: avoid;
            }
            
            .timeline-item {
                page-break-inside: avoid;
                margin-bottom: 20pt;
            }
            
            h1, h2, h3 {
                page-break-after: avoid;
            }
            
            /* Ensure colors print correctly */
            .progress-fill, .score-excellent, .score-good, .score-poor {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            /* Optimize chart visibility for PDF */
            .donut-chart svg {
                width: 80px;
                height: 80px;
            }
            
            .visualization-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 15pt;
            }
        """)
        
        try:
            # Convert HTML to PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(stylesheets=[pdf_css])
            return pdf_bytes
        except Exception as e:
            raise ValueError(f"PDF generation failed: {e}. Try using HTML format instead.")
