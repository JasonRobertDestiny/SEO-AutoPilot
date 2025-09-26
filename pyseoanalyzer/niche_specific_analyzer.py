"""
Niche-Specific SEO Analysis Engine

This module provides specialized SEO analysis tailored to specific industries,
website types, and target audiences. It includes industry-specific keyword
strategies, content recommendations, and optimization focus areas.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WebsiteType(Enum):
    """Enumeration of website types."""
    TECH_BLOG = "tech_blog"
    TECH_PORTFOLIO = "tech_portfolio"
    ECOMMERCE = "ecommerce"
    CORPORATE = "corporate"
    PERSONAL_BLOG = "personal_blog"
    NEWS_MEDIA = "news_media"
    EDUCATIONAL = "educational"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    RESTAURANT = "restaurant"
    NONPROFIT = "nonprofit"
    CREATIVE_PORTFOLIO = "creative_portfolio"
    SAAS = "saas"
    CONSULTING = "consulting"

class Industry(Enum):
    """Enumeration of industries."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    CONSTRUCTION = "construction"
    LEGAL = "legal"
    MARKETING = "marketing"
    DESIGN = "design"
    FOOD_SERVICE = "food_service"
    REAL_ESTATE = "real_estate"
    AUTOMOTIVE = "automotive"
    TRAVEL = "travel"
    FITNESS = "fitness"

@dataclass
class NicheAnalysisResult:
    """Result of niche-specific analysis."""
    website_type: WebsiteType
    industry: Industry
    target_keywords: List[str]
    content_strategy: Dict[str, Any]
    technical_priorities: List[str]
    competitor_analysis: Dict[str, Any]
    optimization_roadmap: List[Dict[str, Any]]
    success_metrics: List[str]

class NicheSpecificAnalyzer:
    """Advanced niche-specific SEO analyzer."""
    
    def __init__(self):
        self.industry_keywords = self._load_industry_keywords()
        self.content_strategies = self._load_content_strategies()
        self.technical_priorities = self._load_technical_priorities()
        self.success_metrics = self._load_success_metrics()
    
    def analyze_niche_optimization(self, 
                                 website_data: Dict[str, Any], 
                                 content_analysis: Dict[str, Any], 
                                 performance_data: Dict[str, Any] = None) -> NicheAnalysisResult:
        """
        Perform comprehensive niche-specific SEO analysis.
        
        Args:
            website_data: Basic website information (URL, title, description, etc.)
            content_analysis: Enhanced content analysis results
            performance_data: Technical performance analysis results
            
        Returns:
            NicheAnalysisResult with specialized recommendations
        """
        try:
            # 1. Determine website type and industry
            website_type = self._detect_website_type(website_data, content_analysis)
            industry = self._detect_industry(website_data, content_analysis)
            
            # 2. Generate target keywords for this niche
            target_keywords = self._generate_target_keywords(website_type, industry, content_analysis)
            
            # 3. Create niche-specific content strategy
            content_strategy = self._create_content_strategy(website_type, industry, content_analysis)
            
            # 4. Identify technical priorities for this niche
            tech_priorities = self._identify_technical_priorities(website_type, industry, performance_data)
            
            # 5. Analyze competitive landscape
            competitor_analysis = self._analyze_competitive_landscape(website_type, industry, website_data)
            
            # 6. Create optimization roadmap
            optimization_roadmap = self._create_optimization_roadmap(
                website_type, industry, content_analysis, performance_data
            )
            
            # 7. Define success metrics
            success_metrics = self._define_success_metrics(website_type, industry)
            
            return NicheAnalysisResult(
                website_type=website_type,
                industry=industry,
                target_keywords=target_keywords,
                content_strategy=content_strategy,
                technical_priorities=tech_priorities,
                competitor_analysis=competitor_analysis,
                optimization_roadmap=optimization_roadmap,
                success_metrics=success_metrics
            )
            
        except Exception as e:
            logger.error(f"Niche analysis failed: {e}")
            return self._create_fallback_result()
    
    def _detect_website_type(self, website_data: Dict, content_analysis: Dict) -> WebsiteType:
        """Detect website type using advanced pattern matching."""
        
        # Get all text content for analysis
        all_text = self._extract_all_text(website_data, content_analysis).lower()
        url = website_data.get('url', '').lower()
        title = website_data.get('title', '').lower()
        
        # Website type scoring
        type_scores = {}
        
        # Tech Blog patterns
        tech_blog_patterns = [
            'programming', 'code', 'tutorial', 'development', 'ai', 'machine learning',
            'javascript', 'python', 'react', 'api', 'software', 'tech', 'algorithm',
            'hackathon', 'github', 'developer', 'coding', 'framework', 'database'
        ]
        type_scores[WebsiteType.TECH_BLOG] = self._calculate_pattern_score(all_text, tech_blog_patterns)
        
        # Tech Portfolio patterns
        tech_portfolio_patterns = [
            'portfolio', 'projects', 'work', 'built', 'developed', 'case study',
            'full-stack', 'front-end', 'back-end', 'skills', 'experience', 'developer',
            'engineer', 'programmer', 'freelance', 'consultant'
        ]
        type_scores[WebsiteType.TECH_PORTFOLIO] = self._calculate_pattern_score(all_text, tech_portfolio_patterns)
        
        # E-commerce patterns
        ecommerce_patterns = [
            'buy', 'shop', 'cart', 'checkout', 'product', 'price', 'sale', 'discount',
            'shipping', 'return', 'payment', 'order', 'store', 'inventory', 'catalog'
        ]
        type_scores[WebsiteType.ECOMMERCE] = self._calculate_pattern_score(all_text, ecommerce_patterns)
        
        # Corporate patterns
        corporate_patterns = [
            'company', 'business', 'services', 'solutions', 'enterprise', 'corporate',
            'team', 'about us', 'contact us', 'clients', 'partners', 'office', 'headquarters'
        ]
        type_scores[WebsiteType.CORPORATE] = self._calculate_pattern_score(all_text, corporate_patterns)
        
        # Blog patterns
        blog_patterns = [
            'blog', 'post', 'article', 'written', 'author', 'published', 'comments',
            'subscribe', 'newsletter', 'latest', 'archive', 'category', 'tags'
        ]
        type_scores[WebsiteType.PERSONAL_BLOG] = self._calculate_pattern_score(all_text, blog_patterns)
        
        # Educational patterns
        educational_patterns = [
            'learn', 'course', 'tutorial', 'lesson', 'education', 'student', 'teacher',
            'university', 'school', 'training', 'certification', 'degree', 'academic'
        ]
        type_scores[WebsiteType.EDUCATIONAL] = self._calculate_pattern_score(all_text, educational_patterns)
        
        # SaaS patterns
        saas_patterns = [
            'saas', 'software as a service', 'subscription', 'monthly', 'pricing',
            'plan', 'free trial', 'dashboard', 'api', 'integration', 'cloud', 'platform'
        ]
        type_scores[WebsiteType.SAAS] = self._calculate_pattern_score(all_text, saas_patterns)
        
        # Healthcare patterns
        healthcare_patterns = [
            'health', 'medical', 'doctor', 'patient', 'treatment', 'clinic', 'hospital',
            'medicine', 'diagnosis', 'therapy', 'wellness', 'care', 'healthcare'
        ]
        type_scores[WebsiteType.HEALTHCARE] = self._calculate_pattern_score(all_text, healthcare_patterns)
        
        # URL-based scoring adjustments
        if 'blog' in url:
            type_scores[WebsiteType.PERSONAL_BLOG] += 10
            type_scores[WebsiteType.TECH_BLOG] += 5
        if 'portfolio' in url:
            type_scores[WebsiteType.TECH_PORTFOLIO] += 15
            type_scores[WebsiteType.CREATIVE_PORTFOLIO] += 15
        if 'shop' in url or 'store' in url:
            type_scores[WebsiteType.ECOMMERCE] += 20
        
        # Special case for AI/tech blogs
        ai_tech_patterns = ['ai', 'artificial intelligence', 'machine learning', 'hackathon']
        ai_score = self._calculate_pattern_score(all_text, ai_tech_patterns)
        if ai_score > 5:
            type_scores[WebsiteType.TECH_BLOG] += ai_score * 2
        
        # Return the type with highest score
        if type_scores:
            detected_type = max(type_scores, key=type_scores.get)
            max_score = type_scores[detected_type]
            
            # Require minimum score threshold
            if max_score >= 3:
                return detected_type
        
        # Fallback based on content structure
        website_type_info = content_analysis.get('website_type_info', {})
        primary_type = website_type_info.get('primary_type', '')
        
        type_mapping = {
            'tech_blog': WebsiteType.TECH_BLOG,
            'tech_portfolio': WebsiteType.TECH_PORTFOLIO,
            'blog': WebsiteType.PERSONAL_BLOG,
            'portfolio': WebsiteType.CREATIVE_PORTFOLIO,
            'ecommerce': WebsiteType.ECOMMERCE,
            'corporate': WebsiteType.CORPORATE
        }
        
        return type_mapping.get(primary_type, WebsiteType.CORPORATE)
    
    def _detect_industry(self, website_data: Dict, content_analysis: Dict) -> Industry:
        """Detect industry using content analysis."""
        
        all_text = self._extract_all_text(website_data, content_analysis).lower()
        
        # Industry scoring based on keyword presence
        industry_scores = {}
        
        # Technology
        tech_patterns = [
            'software', 'technology', 'tech', 'ai', 'machine learning', 'programming',
            'development', 'code', 'digital', 'innovation', 'startup', 'saas'
        ]
        industry_scores[Industry.TECHNOLOGY] = self._calculate_pattern_score(all_text, tech_patterns)
        
        # Healthcare
        healthcare_patterns = [
            'health', 'medical', 'healthcare', 'medicine', 'doctor', 'patient',
            'treatment', 'therapy', 'wellness', 'clinic', 'hospital'
        ]
        industry_scores[Industry.HEALTHCARE] = self._calculate_pattern_score(all_text, healthcare_patterns)
        
        # Finance
        finance_patterns = [
            'finance', 'financial', 'investment', 'banking', 'money', 'loan',
            'insurance', 'trading', 'wealth', 'advisor', 'planning'
        ]
        industry_scores[Industry.FINANCE] = self._calculate_pattern_score(all_text, finance_patterns)
        
        # Education
        education_patterns = [
            'education', 'school', 'university', 'learning', 'course', 'training',
            'student', 'teacher', 'academic', 'degree', 'certification'
        ]
        industry_scores[Industry.EDUCATION] = self._calculate_pattern_score(all_text, education_patterns)
        
        # Marketing & Design
        marketing_patterns = [
            'marketing', 'advertising', 'brand', 'creative', 'design', 'agency',
            'campaign', 'social media', 'seo', 'digital marketing'
        ]
        industry_scores[Industry.MARKETING] = self._calculate_pattern_score(all_text, marketing_patterns)
        
        design_patterns = [
            'design', 'creative', 'art', 'visual', 'graphic', 'ui', 'ux',
            'branding', 'logo', 'illustration', 'portfolio'
        ]
        industry_scores[Industry.DESIGN] = self._calculate_pattern_score(all_text, design_patterns)
        
        # Legal
        legal_patterns = [
            'legal', 'law', 'attorney', 'lawyer', 'court', 'litigation',
            'contract', 'compliance', 'regulation', 'counsel'
        ]
        industry_scores[Industry.LEGAL] = self._calculate_pattern_score(all_text, legal_patterns)
        
        # Real Estate
        realestate_patterns = [
            'real estate', 'property', 'house', 'apartment', 'rent', 'buy',
            'sell', 'mortgage', 'realtor', 'listing', 'home'
        ]
        industry_scores[Industry.REAL_ESTATE] = self._calculate_pattern_score(all_text, realestate_patterns)
        
        # Return industry with highest score
        if industry_scores:
            detected_industry = max(industry_scores, key=industry_scores.get)
            max_score = industry_scores[detected_industry]
            
            if max_score >= 2:
                return detected_industry
        
        # Check content analysis for industry hint
        website_type_info = content_analysis.get('website_type_info', {})
        detected_industry_str = website_type_info.get('industry', '')
        
        industry_mapping = {
            'technology': Industry.TECHNOLOGY,
            'healthcare': Industry.HEALTHCARE,
            'finance': Industry.FINANCE,
            'education': Industry.EDUCATION,
            'marketing': Industry.MARKETING,
            'design': Industry.DESIGN,
            'legal': Industry.LEGAL
        }
        
        return industry_mapping.get(detected_industry_str, Industry.TECHNOLOGY)
    
    def _generate_target_keywords(self, website_type: WebsiteType, industry: Industry, content_analysis: Dict) -> List[str]:
        """Generate target keywords based on niche analysis."""
        
        keywords = []
        
        # Base keywords from content
        existing_keywords = self._extract_existing_keywords(content_analysis)
        keywords.extend(existing_keywords[:5])  # Top 5 existing
        
        # Industry-specific keywords
        industry_keywords = self.industry_keywords.get(industry.value, [])
        keywords.extend(industry_keywords[:10])
        
        # Website type specific keywords
        type_keywords = {
            WebsiteType.TECH_BLOG: [
                'programming tutorials', 'code examples', 'developer guide',
                'tech blog', 'software development', 'coding tips'
            ],
            WebsiteType.TECH_PORTFOLIO: [
                'full-stack developer', 'software engineer portfolio', 'web developer',
                'programming projects', 'developer skills', 'code portfolio'
            ],
            WebsiteType.ECOMMERCE: [
                'online store', 'buy online', 'best price', 'free shipping',
                'product reviews', 'shop now'
            ],
            WebsiteType.CORPORATE: [
                'business solutions', 'professional services', 'company services',
                'enterprise solutions', 'business consulting'
            ],
            WebsiteType.SAAS: [
                'software as a service', 'cloud platform', 'business software',
                'subscription software', 'enterprise tools'
            ]
        }
        
        type_specific = type_keywords.get(website_type, [])
        keywords.extend(type_specific)
        
        # Long-tail keyword generation
        long_tail = self._generate_long_tail_keywords(website_type, industry, content_analysis)
        keywords.extend(long_tail)
        
        # Remove duplicates and limit
        unique_keywords = list(dict.fromkeys(keywords))
        return unique_keywords[:20]  # Top 20 target keywords
    
    def _create_content_strategy(self, website_type: WebsiteType, industry: Industry, content_analysis: Dict) -> Dict[str, Any]:
        """Create niche-specific content strategy."""
        
        current_content_quality = content_analysis.get('content_quality', {})
        current_word_count = content_analysis.get('total_word_count', 0)
        
        strategy = {
            'current_analysis': {
                'word_count': current_word_count,
                'quality_score': current_content_quality.get('quality_score', 0),
                'content_depth': current_content_quality.get('content_depth_level', 'basic')
            }
        }
        
        # Website type specific strategies
        if website_type == WebsiteType.TECH_BLOG:
            strategy.update({
                'content_pillars': [
                    'Programming Tutorials', 'Code Examples', 'Tech Reviews',
                    'Industry News', 'Best Practices', 'Tool Comparisons'
                ],
                'recommended_content_types': [
                    'Step-by-step tutorials', 'Code walkthroughs', 'Project showcases',
                    'Technical deep-dives', 'Problem-solving guides'
                ],
                'posting_frequency': 'Weekly (2-3 posts)',
                'target_word_count': '1,500-3,000 words per post',
                'seo_focus': [
                    'Include code examples', 'Add table of contents',
                    'Use technical keywords naturally', 'Link to documentation',
                    'Add social proof and comments'
                ]
            })
            
        elif website_type == WebsiteType.TECH_PORTFOLIO:
            strategy.update({
                'content_pillars': [
                    'Project Case Studies', 'Technical Skills', 'Experience Highlights',
                    'Problem-Solving Approach', 'Technology Stack'
                ],
                'recommended_content_types': [
                    'Detailed project descriptions', 'Before/after comparisons',
                    'Technical challenges and solutions', 'Client testimonials',
                    'Skills demonstration'
                ],
                'target_word_count': '800-1,500 words per project',
                'seo_focus': [
                    'Use action verbs', 'Include metrics and results',
                    'Add technology keywords', 'Show problem-solving process',
                    'Include contact calls-to-action'
                ]
            })
            
        elif website_type == WebsiteType.ECOMMERCE:
            strategy.update({
                'content_pillars': [
                    'Product Guides', 'How-to Content', 'Industry News',
                    'Customer Stories', 'Brand Story'
                ],
                'recommended_content_types': [
                    'Product descriptions', 'Buying guides', 'Comparison articles',
                    'Customer reviews', 'FAQ pages'
                ],
                'posting_frequency': 'Multiple times per week',
                'target_word_count': '500-1,200 words per page',
                'seo_focus': [
                    'Product-focused keywords', 'Local SEO optimization',
                    'Customer review integration', 'Schema markup for products',
                    'Internal linking between related products'
                ]
            })
        
        # Industry-specific enhancements
        industry_strategies = self.content_strategies.get(industry.value, {})
        if industry_strategies:
            strategy['industry_specific'] = industry_strategies
        
        # Content gaps and opportunities
        strategy['content_opportunities'] = self._identify_content_gaps(
            website_type, industry, content_analysis
        )
        
        return strategy
    
    def _identify_technical_priorities(self, website_type: WebsiteType, industry: Industry, performance_data: Dict = None) -> List[str]:
        """Identify technical SEO priorities for the specific niche."""
        
        priorities = []
        
        # Base technical priorities
        base_priorities = [
            'Page loading speed optimization',
            'Mobile-first responsive design',
            'SSL certificate and HTTPS',
            'XML sitemap optimization',
            'Robots.txt configuration'
        ]
        
        # Website type specific priorities
        if website_type == WebsiteType.TECH_BLOG:
            priorities.extend([
                'Code syntax highlighting optimization',
                'Technical content structure (H1-H6)',
                'Internal linking between related posts',
                'Comment system implementation',
                'Social sharing optimization'
            ])
            
        elif website_type == WebsiteType.TECH_PORTFOLIO:
            priorities.extend([
                'Project showcase page optimization',
                'Skills section structured data',
                'Contact form optimization',
                'Portfolio image optimization',
                'Professional schema markup'
            ])
            
        elif website_type == WebsiteType.ECOMMERCE:
            priorities.extend([
                'Product schema markup',
                'Shopping cart optimization',
                'Product image optimization',
                'Checkout process streamlining',
                'Inventory management integration'
            ])
        
        # Industry specific priorities
        industry_priorities = self.technical_priorities.get(industry.value, [])
        priorities.extend(industry_priorities)
        
        # Performance-based priorities
        if performance_data:
            technical_score = performance_data.get('technical_score', {}).get('overall_score', 0)
            if technical_score < 70:
                priorities.insert(0, 'Critical: Overall technical performance improvement')
            
            core_vitals = performance_data.get('core_web_vitals', {})
            if core_vitals.get('overall_status') == 'poor':
                priorities.insert(1, 'Critical: Core Web Vitals optimization')
        
        # Remove duplicates and prioritize
        unique_priorities = list(dict.fromkeys(priorities))
        return unique_priorities[:15]  # Top 15 priorities
    
    def _analyze_competitive_landscape(self, website_type: WebsiteType, industry: Industry, website_data: Dict) -> Dict[str, Any]:
        """Analyze competitive landscape for the specific niche."""
        
        # This is a simplified competitive analysis
        # In a production environment, this would integrate with tools like:
        # - SEMrush API, Ahrefs API, SimilarWeb API
        # - Google Search Console API for competitor analysis
        # - Social media APIs for competitive social presence
        
        competitive_analysis = {
            'market_overview': self._get_market_overview(website_type, industry),
            'competitor_types': self._identify_competitor_types(website_type, industry),
            'competitive_advantages': self._identify_competitive_advantages(website_type, industry, website_data),
            'opportunity_gaps': self._identify_opportunity_gaps(website_type, industry),
            'competitive_keywords': self._suggest_competitive_keywords(website_type, industry),
            'benchmarking_metrics': self._get_benchmarking_metrics(website_type, industry)
        }
        
        return competitive_analysis
    
    def _create_optimization_roadmap(self, website_type: WebsiteType, industry: Industry, 
                                   content_analysis: Dict, performance_data: Dict = None) -> List[Dict[str, Any]]:
        """Create a detailed optimization roadmap for the niche."""
        
        roadmap = []
        
        # Phase 1: Foundation (0-30 days)
        phase1_tasks = [
            {
                'phase': 1,
                'timeframe': '0-30 days',
                'priority': 'critical',
                'category': 'technical_foundation',
                'tasks': [
                    'Fix critical technical SEO issues',
                    'Optimize page loading speed',
                    'Implement mobile-first design',
                    'Set up analytics and tracking'
                ]
            }
        ]
        
        # Phase 2: Content & Structure (30-60 days)
        phase2_tasks = [
            {
                'phase': 2,
                'timeframe': '30-60 days', 
                'priority': 'high',
                'category': 'content_optimization',
                'tasks': self._get_phase2_tasks(website_type, content_analysis)
            }
        ]
        
        # Phase 3: Growth & Authority (60-90 days)
        phase3_tasks = [
            {
                'phase': 3,
                'timeframe': '60-90 days',
                'priority': 'medium',
                'category': 'growth_authority',
                'tasks': self._get_phase3_tasks(website_type, industry)
            }
        ]
        
        roadmap.extend([phase1_tasks[0], phase2_tasks[0], phase3_tasks[0]])
        
        return roadmap
    
    def _define_success_metrics(self, website_type: WebsiteType, industry: Industry) -> List[str]:
        """Define success metrics for the specific niche."""
        
        # Base metrics for all sites
        base_metrics = [
            'Organic search traffic growth',
            'Search engine rankings improvement', 
            'Page loading speed (Core Web Vitals)',
            'Mobile usability score',
            'Overall SEO score improvement'
        ]
        
        # Website type specific metrics
        type_specific_metrics = {
            WebsiteType.TECH_BLOG: [
                'Blog post engagement (time on page)',
                'Tutorial completion rates',
                'Code snippet copy rates',
                'Technical keyword rankings',
                'Developer community engagement'
            ],
            WebsiteType.TECH_PORTFOLIO: [
                'Portfolio view duration',
                'Project detail page views', 
                'Contact form submissions',
                'Professional network connections',
                'Job inquiry conversions'
            ],
            WebsiteType.ECOMMERCE: [
                'Product page conversion rates',
                'Shopping cart abandonment reduction',
                'Average order value increase',
                'Product keyword rankings',
                'Customer lifetime value'
            ],
            WebsiteType.CORPORATE: [
                'Lead generation increase',
                'Service inquiry forms',
                'Brand keyword rankings',
                'Business listing visibility',
                'Client testimonial engagement'
            ]
        }
        
        niche_metrics = type_specific_metrics.get(website_type, [])
        
        # Industry specific metrics
        industry_metrics = self.success_metrics.get(industry.value, [])
        
        all_metrics = base_metrics + niche_metrics + industry_metrics
        unique_metrics = list(dict.fromkeys(all_metrics))
        
        return unique_metrics[:12]  # Top 12 metrics to track
    
    # Helper methods
    
    def _extract_all_text(self, website_data: Dict, content_analysis: Dict) -> str:
        """Extract all text content for analysis."""
        text_parts = []
        
        # From website data
        text_parts.append(website_data.get('title', ''))
        text_parts.append(website_data.get('description', ''))
        text_parts.append(website_data.get('url', ''))
        
        # From content analysis
        content_sections = content_analysis.get('content_sections', {})
        for section_data in content_sections.values():
            text_parts.append(section_data.get('text', ''))
        
        return ' '.join(text_parts)
    
    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> int:
        """Calculate score based on pattern matches in text."""
        score = 0
        for pattern in patterns:
            count = text.count(pattern.lower())
            score += count
        return score
    
    def _extract_existing_keywords(self, content_analysis: Dict) -> List[str]:
        """Extract existing keywords from content analysis."""
        # This would be enhanced with actual keyword extraction logic
        keywords = []
        
        # Get from content sections
        content_sections = content_analysis.get('content_sections', {})
        for section_name, section_data in content_sections.items():
            text = section_data.get('text', '').lower()
            
            # Simple keyword extraction (would use more sophisticated NLP)
            words = text.split()
            tech_keywords = [
                word for word in words 
                if len(word) > 3 and word in [
                    'programming', 'development', 'software', 'tech', 'code',
                    'web', 'mobile', 'api', 'database', 'framework'
                ]
            ]
            keywords.extend(tech_keywords[:3])
        
        return list(set(keywords))  # Remove duplicates
    
    def _generate_long_tail_keywords(self, website_type: WebsiteType, industry: Industry, content_analysis: Dict) -> List[str]:
        """Generate long-tail keywords for the niche."""
        
        long_tail = []
        
        if website_type == WebsiteType.TECH_BLOG:
            long_tail.extend([
                'how to code in python',
                'javascript tutorial for beginners',
                'best practices software development',
                'machine learning project ideas',
                'web development frameworks comparison'
            ])
        elif website_type == WebsiteType.TECH_PORTFOLIO:
            long_tail.extend([
                'full stack developer portfolio examples',
                'software engineer project showcase',
                'web developer skills demonstration',
                'programming portfolio best practices',
                'freelance developer case studies'
            ])
        
        return long_tail
    
    def _identify_content_gaps(self, website_type: WebsiteType, industry: Industry, content_analysis: Dict) -> List[str]:
        """Identify content gaps and opportunities."""
        
        gaps = []
        
        current_word_count = content_analysis.get('total_word_count', 0)
        content_sections = content_analysis.get('content_sections', {})
        
        if website_type == WebsiteType.TECH_BLOG:
            if 'projects' not in content_sections:
                gaps.append('Add project showcase section')
            if current_word_count < 1500:
                gaps.append('Expand content with detailed tutorials')
            if 'about' not in content_sections:
                gaps.append('Add author bio and expertise section')
                
        elif website_type == WebsiteType.TECH_PORTFOLIO:
            if 'projects' not in content_sections:
                gaps.append('Critical: Add detailed project descriptions')
            if 'about' not in content_sections:
                gaps.append('Add professional bio and skills section')
            if current_word_count < 1000:
                gaps.append('Expand project case studies with results')
        
        return gaps
    
    def _get_market_overview(self, website_type: WebsiteType, industry: Industry) -> Dict[str, Any]:
        """Get market overview for the niche."""
        
        # Simplified market data - would integrate with market research APIs
        market_data = {
            'market_size': 'Large',
            'competition_level': 'High',
            'growth_trend': 'Growing',
            'key_trends': [],
            'seasonal_factors': []
        }
        
        if website_type == WebsiteType.TECH_BLOG and industry == Industry.TECHNOLOGY:
            market_data.update({
                'market_size': 'Very Large',
                'competition_level': 'Very High',
                'key_trends': [
                    'AI and Machine Learning content in high demand',
                    'Developer tutorial content highly searched',
                    'Code examples and practical guides preferred'
                ],
                'opportunities': [
                    'Niche technical topics with less competition',
                    'Beginner-friendly explanations of complex topics',
                    'Real-world project tutorials'
                ]
            })
        
        return market_data
    
    def _identify_competitor_types(self, website_type: WebsiteType, industry: Industry) -> List[str]:
        """Identify types of competitors in the niche."""
        
        if website_type == WebsiteType.TECH_BLOG:
            return [
                'Established tech blogs (Medium, Dev.to)',
                'Individual developer blogs',
                'Company tech blogs',
                'Tutorial platforms (Codecademy, freeCodeCamp)',
                'Documentation sites'
            ]
        elif website_type == WebsiteType.TECH_PORTFOLIO:
            return [
                'Other developer portfolios',
                'Freelancing platforms',
                'Professional networking sites',
                'Design portfolio sites',
                'Agency websites'
            ]
        
        return ['Direct competitors', 'Indirect competitors', 'Industry leaders']
    
    def _identify_competitive_advantages(self, website_type: WebsiteType, industry: Industry, website_data: Dict) -> List[str]:
        """Identify potential competitive advantages."""
        
        advantages = []
        
        if website_type == WebsiteType.TECH_BLOG:
            advantages = [
                'Personal expertise and unique perspective',
                'Practical, hands-on tutorials',
                'Real project examples and case studies',
                'Regular posting schedule',
                'Community engagement and comments'
            ]
        elif website_type == WebsiteType.TECH_PORTFOLIO:
            advantages = [
                'Unique project combinations',
                'Demonstrated results and metrics',
                'Professional presentation',
                'Client testimonials',
                'Specialized skill sets'
            ]
        
        return advantages
    
    def _identify_opportunity_gaps(self, website_type: WebsiteType, industry: Industry) -> List[str]:
        """Identify market opportunity gaps."""
        
        if website_type == WebsiteType.TECH_BLOG:
            return [
                'Beginner-friendly AI tutorials',
                'No-code/low-code development content',
                'Practical DevOps for small teams',
                'Mobile app development guides',
                'Cybersecurity for developers'
            ]
        
        return ['Market gap analysis would be performed here']
    
    def _suggest_competitive_keywords(self, website_type: WebsiteType, industry: Industry) -> List[str]:
        """Suggest keywords to compete on."""
        
        if website_type == WebsiteType.TECH_BLOG:
            return [
                'python tutorial',
                'javascript guide',
                'web development tips',
                'coding best practices',
                'programming tutorial'
            ]
        
        return ['Competitive keyword analysis would be performed here']
    
    def _get_benchmarking_metrics(self, website_type: WebsiteType, industry: Industry) -> Dict[str, Any]:
        """Get benchmarking metrics for the niche."""
        
        # Industry benchmarks - would integrate with analytics APIs
        benchmarks = {
            'average_page_load_time': '2-3 seconds',
            'average_bounce_rate': '40-60%',
            'average_session_duration': '2-3 minutes',
            'mobile_traffic_percentage': '60-70%'
        }
        
        if website_type == WebsiteType.TECH_BLOG:
            benchmarks.update({
                'average_post_length': '1,500-2,500 words',
                'average_time_on_page': '3-5 minutes',
                'typical_publishing_frequency': 'Weekly',
                'engagement_rate': '2-5%'
            })
        
        return benchmarks
    
    def _get_phase2_tasks(self, website_type: WebsiteType, content_analysis: Dict) -> List[str]:
        """Get Phase 2 optimization tasks."""
        
        tasks = [
            'Optimize existing content for target keywords',
            'Improve internal linking structure',
            'Add schema markup for content type',
            'Optimize images and media'
        ]
        
        if website_type == WebsiteType.TECH_BLOG:
            tasks.extend([
                'Create content calendar for regular posting',
                'Add code syntax highlighting',
                'Implement comment system',
                'Create related posts suggestions'
            ])
        
        return tasks
    
    def _get_phase3_tasks(self, website_type: WebsiteType, industry: Industry) -> List[str]:
        """Get Phase 3 optimization tasks."""
        
        tasks = [
            'Build high-quality backlinks',
            'Expand content depth and breadth',
            'Implement advanced analytics tracking',
            'Create content upgrade offers'
        ]
        
        if website_type == WebsiteType.TECH_BLOG:
            tasks.extend([
                'Guest posting on relevant platforms',
                'Create downloadable resources',
                'Build email newsletter',
                'Engage with developer community'
            ])
        
        return tasks
    
    def _create_fallback_result(self) -> NicheAnalysisResult:
        """Create fallback analysis result."""
        
        return NicheAnalysisResult(
            website_type=WebsiteType.CORPORATE,
            industry=Industry.TECHNOLOGY,
            target_keywords=['seo', 'website optimization', 'digital marketing'],
            content_strategy={'status': 'fallback', 'recommendation': 'General SEO optimization'},
            technical_priorities=['Page speed optimization', 'Mobile responsiveness'],
            competitor_analysis={'status': 'basic', 'recommendation': 'Competitor research needed'},
            optimization_roadmap=[{
                'phase': 1,
                'timeframe': '0-30 days',
                'priority': 'high',
                'tasks': ['Basic SEO optimization']
            }],
            success_metrics=['Traffic growth', 'Ranking improvement']
        )
    
    # Data loading methods (would load from configuration files or database)
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keyword databases."""
        return {
            'technology': [
                'software development', 'programming', 'web development', 'mobile app',
                'ai', 'machine learning', 'data science', 'cloud computing', 'devops',
                'cybersecurity', 'blockchain', 'iot', 'automation'
            ],
            'healthcare': [
                'medical care', 'health services', 'patient care', 'medical treatment',
                'healthcare provider', 'medical practice', 'wellness', 'telemedicine'
            ],
            'finance': [
                'financial services', 'investment', 'banking', 'insurance', 'wealth management',
                'financial planning', 'retirement planning', 'loan services'
            ],
            'education': [
                'online learning', 'education services', 'training programs', 'courses',
                'certification', 'skill development', 'academic programs'
            ]
        }
    
    def _load_content_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load industry-specific content strategies."""
        return {
            'technology': {
                'content_types': ['tutorials', 'guides', 'case studies', 'reviews'],
                'posting_frequency': 'Weekly',
                'average_length': '1500-3000 words',
                'engagement_tactics': ['code examples', 'interactive demos', 'community discussions']
            },
            'healthcare': {
                'content_types': ['educational articles', 'patient guides', 'health tips'],
                'compliance_notes': ['HIPAA compliance required', 'Medical accuracy essential'],
                'trust_signals': ['credentials', 'certifications', 'testimonials']
            }
        }
    
    def _load_technical_priorities(self) -> Dict[str, List[str]]:
        """Load industry-specific technical priorities."""
        return {
            'technology': [
                'Code syntax highlighting',
                'Developer-friendly navigation',
                'API documentation structure',
                'GitHub integration'
            ],
            'healthcare': [
                'HIPAA compliance measures',
                'Patient portal integration',
                'Medical form optimization',
                'Accessibility compliance (ADA)'
            ],
            'finance': [
                'Security compliance',
                'SSL/TLS optimization',
                'Financial calculator integration',
                'Regulatory compliance pages'
            ]
        }
    
    def _load_success_metrics(self) -> Dict[str, List[str]]:
        """Load industry-specific success metrics."""
        return {
            'technology': [
                'Developer engagement metrics',
                'Code example usage',
                'Technical keyword rankings',
                'Community contributions'
            ],
            'healthcare': [
                'Patient inquiry forms',
                'Health content engagement',
                'Appointment booking rates',
                'Health resource downloads'
            ],
            'finance': [
                'Financial consultation requests',
                'Calculator usage rates',
                'Financial guide downloads',
                'Trust signal engagement'
            ]
        }


# Usage example and integration helper
def analyze_niche_specific_seo(website_data: Dict[str, Any], 
                              content_analysis: Dict[str, Any], 
                              performance_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main function to perform niche-specific SEO analysis.
    
    Usage:
    niche_analysis = analyze_niche_specific_seo(page_data, content_data, perf_data)
    """
    
    analyzer = NicheSpecificAnalyzer()
    
    try:
        result = analyzer.analyze_niche_optimization(
            website_data, content_analysis, performance_data
        )
        
        # Convert dataclass to dictionary for JSON serialization
        return {
            'website_type': result.website_type.value,
            'industry': result.industry.value,
            'target_keywords': result.target_keywords,
            'content_strategy': result.content_strategy,
            'technical_priorities': result.technical_priorities,
            'competitor_analysis': result.competitor_analysis,
            'optimization_roadmap': result.optimization_roadmap,
            'success_metrics': result.success_metrics,
            'analysis_timestamp': time.time(),
            'analysis_version': '1.0'
        }
        
    except Exception as e:
        logger.error(f"Niche-specific analysis failed: {e}")
        return {
            'error': str(e),
            'fallback_recommendations': [
                'Improve page loading speed',
                'Optimize content for target keywords',
                'Enhance mobile user experience',
                'Build high-quality backlinks'
            ]
        }


import time
# Make time available for the timestamp