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


class SEOReportGenerator:
    """Generates comprehensive SEO analysis reports in multiple formats."""
    
    def __init__(self):
        self.supported_formats = ['html', 'json', 'csv', 'txt']
    
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
        """Prepare and consolidate analysis data for reporting."""
        url = analysis_data.get('url', 'Unknown URL')
        
        # Calculate overall SEO score using detailed algorithm
        seo_score = self._calculate_overall_score(analysis_data)
        
        # Extract key metrics
        basic_metrics = analysis_data.get('basic_seo_analysis', {})
        llm_analysis = analysis_data.get('llm_analysis', {})
        
        # Consolidate recommendations
        recommendations = self._consolidate_recommendations(basic_metrics, llm_analysis)
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(basic_metrics)
        
        return {
            'url': url,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'seo_score': seo_score,
            'grade': self._get_grade_from_score(seo_score),
            'basic_metrics': basic_metrics,
            'llm_analysis': llm_analysis,
            'recommendations': recommendations,
            'critical_issues': critical_issues,
            'summary': self._generate_executive_summary(seo_score, critical_issues, recommendations)
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
            
            <div class="timestamp">
                Report generated on {analysis_date} by SEO Genius
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
            analysis_date=data['analysis_date']
        )
    
    def _generate_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for key metrics display."""
        metrics_html = ""
        
        # Title metrics
        if 'title' in metrics:
            title_text = metrics.get('title', '')
            title_length = len(title_text) if title_text else 0
            metrics_html += f"""
            <div class="metric-card">
                <div class="metric-value">{title_length}</div>
                <div class="metric-label">Title Length (chars)</div>
            </div>
            """
        
        # Description metrics
        if 'description' in metrics:
            desc_text = metrics.get('description', '')
            desc_length = len(desc_text) if desc_text else 0
            metrics_html += f"""
            <div class="metric-card">
                <div class="metric-value">{desc_length}</div>
                <div class="metric-label">Description Length (chars)</div>
            </div>
            """
        
        # Headings count
        headings = metrics.get('headings', {})
        h1_count = len(headings.get('h1', [])) if headings else 0
        total_headings = 0
        if headings:
            total_headings = sum(len(headings.get(f'h{i}', [])) for i in range(1, 7))
        
        metrics_html += f"""
        <div class="metric-card">
            <div class="metric-value">{h1_count}</div>
            <div class="metric-label">H1 Tags</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_headings}</div>
            <div class="metric-label">Total Headings</div>
        </div>
        """
        
        # Word count metrics
        word_count = metrics.get('word_count', 0)
        metrics_html += f"""
        <div class="metric-card">
            <div class="metric-value">{word_count}</div>
            <div class="metric-label">Word Count</div>
        </div>
        """
        
        # Warnings count (as proxy for issues)
        warnings = metrics.get('warnings', [])
        warning_count = len(warnings) if warnings else 0
        metrics_html += f"""
        <div class="metric-card">
            <div class="metric-value">{warning_count}</div>
            <div class="metric-label">SEO Warnings</div>
        </div>
        """
        
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