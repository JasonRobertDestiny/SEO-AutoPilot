"""
Enhanced Content Analysis Module

This module provides advanced content extraction and analysis capabilities
for accurate SEO analysis, including comprehensive word count, content
section detection, and website type identification.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class AdvancedContentAnalyzer:
    """Enhanced content analysis with accurate extraction and categorization."""
    
    def __init__(self):
        self.content_sections = {}
        self.website_type = None
        self.content_quality_score = 0
        
    def extract_comprehensive_content(self, html: str, url: str = "") -> Dict[str, Any]:
        """
        Extract comprehensive content from HTML with accurate word counting.
        
        Args:
            html: Raw HTML content
            url: Website URL for context
            
        Returns:
            Dictionary containing comprehensive content analysis
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 
                               'header', 'menu', 'form', 'button', 'noscript']):
                element.decompose()
            
            # Extract main content sections
            content_sections = self._extract_content_sections(soup)
            
            # Calculate comprehensive word count
            total_word_count = self._calculate_accurate_word_count(content_sections)
            
            # Analyze content structure and quality
            content_structure = self._analyze_content_structure(soup)
            
            # Detect website type
            website_type = self._detect_website_type(soup, url, content_sections)
            
            # Extract metadata and semantic information
            semantic_info = self._extract_semantic_information(soup)
            
            # Analyze content depth and quality
            content_quality = self._assess_content_quality(content_sections, total_word_count)
            
            return {
                'content_sections': content_sections,
                'total_word_count': total_word_count,
                'content_structure': content_structure,
                'website_type': website_type,
                'semantic_info': semantic_info,
                'content_quality': content_quality,
                'extraction_method': 'enhanced_comprehensive'
            }
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            # Fallback to basic extraction
            return self._fallback_content_extraction(html)
    
    def _extract_content_sections(self, soup: BeautifulSoup) -> Dict[str, Dict[str, Any]]:
        """Extract and categorize different content sections."""
        sections = {}
        
        # Main content area detection
        main_content = self._extract_main_content(soup)
        if main_content:
            sections['main_content'] = {
                'text': main_content['text'],
                'word_count': main_content['word_count'],
                'paragraph_count': main_content['paragraph_count'],
                'importance_weight': 1.0
            }
        
        # Navigation content
        nav_content = self._extract_navigation_content(soup)
        if nav_content:
            sections['navigation'] = {
                'text': nav_content['text'],
                'word_count': nav_content['word_count'],
                'link_count': nav_content['link_count'],
                'importance_weight': 0.3
            }
        
        # Project/portfolio sections (for portfolio sites)
        project_content = self._extract_project_content(soup)
        if project_content:
            sections['projects'] = {
                'text': project_content['text'],
                'word_count': project_content['word_count'],
                'project_count': project_content['project_count'],
                'importance_weight': 0.8
            }
        
        # About/bio sections
        about_content = self._extract_about_content(soup)
        if about_content:
            sections['about'] = {
                'text': about_content['text'],
                'word_count': about_content['word_count'],
                'importance_weight': 0.7
            }
        
        # Blog/article content
        article_content = self._extract_article_content(soup)
        if article_content:
            sections['articles'] = {
                'text': article_content['text'],
                'word_count': article_content['word_count'],
                'article_count': article_content['article_count'],
                'importance_weight': 0.9
            }
        
        # Service/product descriptions
        service_content = self._extract_service_content(soup)
        if service_content:
            sections['services'] = {
                'text': service_content['text'],
                'word_count': service_content['word_count'],
                'service_count': service_content['service_count'],
                'importance_weight': 0.8
            }
        
        return sections
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract main content using multiple strategies."""
        # Strategy 1: Look for main, article, or content containers
        main_selectors = [
            'main', 'article', '[role="main"]', '.main-content', '#main-content',
            '.content', '#content', '.post-content', '.entry-content'
        ]
        
        main_element = None
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                main_element = element
                break
        
        # Strategy 2: Find largest text block if no semantic main found
        if not main_element:
            text_blocks = []
            for element in soup.find_all(['div', 'section', 'article']):
                text = element.get_text(strip=True)
                if len(text) > 100:  # Minimum threshold
                    text_blocks.append((element, len(text)))
            
            if text_blocks:
                text_blocks.sort(key=lambda x: x[1], reverse=True)
                main_element = text_blocks[0][0]
        
        if main_element:
            text_content = main_element.get_text(separator=' ', strip=True)
            paragraphs = main_element.find_all(['p', 'div'])
            
            return {
                'text': text_content,
                'word_count': len(text_content.split()),
                'paragraph_count': len([p for p in paragraphs if p.get_text(strip=True)])
            }
        
        return None
    
    def _extract_navigation_content(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract navigation menu content."""
        nav_elements = soup.find_all(['nav', '.navbar', '.menu', '.navigation', '#menu'])
        
        if not nav_elements:
            return None
        
        nav_text = []
        link_count = 0
        
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                link_text = link.get_text(strip=True)
                if link_text and len(link_text) < 50:  # Reasonable nav item length
                    nav_text.append(link_text)
                    link_count += 1
        
        if nav_text:
            combined_text = ' '.join(nav_text)
            return {
                'text': combined_text,
                'word_count': len(combined_text.split()),
                'link_count': link_count
            }
        
        return None
    
    def _extract_project_content(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract project/portfolio content."""
        project_selectors = [
            '.project', '.portfolio-item', '.work-item', '.case-study',
            '[class*="project"]', '[class*="portfolio"]', '[id*="project"]'
        ]
        
        projects = []
        for selector in project_selectors:
            elements = soup.select(selector)
            projects.extend(elements)
        
        # Also look for project indicators in text
        project_keywords = ['project', 'portfolio', 'case study', 'work', 'built', 'developed']
        text_blocks = soup.find_all(['div', 'section'])
        for block in text_blocks:
            text = block.get_text().lower()
            if any(keyword in text for keyword in project_keywords) and len(text) > 50:
                projects.append(block)
        
        if projects:
            project_texts = []
            for project in projects[:10]:  # Limit to avoid duplicates
                text = project.get_text(separator=' ', strip=True)
                if text and len(text) > 20:
                    project_texts.append(text)
            
            combined_text = ' '.join(project_texts)
            return {
                'text': combined_text,
                'word_count': len(combined_text.split()),
                'project_count': len(project_texts)
            }
        
        return None
    
    def _extract_about_content(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract about/bio content."""
        about_selectors = [
            '.about', '#about', '.bio', '.biography', '.intro', '.introduction',
            '[class*="about"]', '[id*="about"]'
        ]
        
        about_elements = []
        for selector in about_selectors:
            elements = soup.select(selector)
            about_elements.extend(elements)
        
        # Look for about keywords in headings
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            if any(word in heading.get_text().lower() for word in ['about', 'bio', 'who i am']):
                # Get content after this heading
                next_elements = heading.find_next_siblings(['p', 'div'])
                about_elements.extend(next_elements)
        
        if about_elements:
            about_texts = []
            for element in about_elements:
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 20:
                    about_texts.append(text)
            
            combined_text = ' '.join(about_texts)
            return {
                'text': combined_text,
                'word_count': len(combined_text.split())
            }
        
        return None
    
    def _extract_article_content(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract blog/article content."""
        article_selectors = [
            'article', '.post', '.blog-post', '.entry', '.article',
            '[class*="post"]', '[class*="article"]'
        ]
        
        articles = []
        for selector in article_selectors:
            elements = soup.select(selector)
            articles.extend(elements)
        
        if articles:
            article_texts = []
            for article in articles:
                text = article.get_text(separator=' ', strip=True)
                if text and len(text) > 100:  # Minimum article length
                    article_texts.append(text)
            
            combined_text = ' '.join(article_texts)
            return {
                'text': combined_text,
                'word_count': len(combined_text.split()),
                'article_count': len(article_texts)
            }
        
        return None
    
    def _extract_service_content(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract service/product content."""
        service_selectors = [
            '.service', '.product', '.offering', '.feature',
            '[class*="service"]', '[class*="product"]'
        ]
        
        services = []
        for selector in service_selectors:
            elements = soup.select(selector)
            services.extend(elements)
        
        if services:
            service_texts = []
            for service in services:
                text = service.get_text(separator=' ', strip=True)
                if text and len(text) > 20:
                    service_texts.append(text)
            
            combined_text = ' '.join(service_texts)
            return {
                'text': combined_text,
                'word_count': len(combined_text.split()),
                'service_count': len(service_texts)
            }
        
        return None
    
    def _calculate_accurate_word_count(self, content_sections: Dict[str, Dict[str, Any]]) -> int:
        """Calculate weighted word count from all content sections."""
        total_weighted_words = 0
        
        for section_name, section_data in content_sections.items():
            word_count = section_data.get('word_count', 0)
            weight = section_data.get('importance_weight', 1.0)
            
            # Apply weight to word count
            weighted_words = int(word_count * weight)
            total_weighted_words += weighted_words
            
            logger.debug(f"Section '{section_name}': {word_count} words (weight: {weight}) = {weighted_words} weighted words")
        
        return total_weighted_words
    
    def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the overall content structure and organization."""
        return {
            'heading_levels': self._analyze_heading_structure(soup),
            'paragraph_distribution': self._analyze_paragraph_distribution(soup),
            'list_usage': self._analyze_list_usage(soup),
            'media_elements': self._analyze_media_elements(soup),
            'structural_score': self._calculate_structural_score(soup)
        }
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze heading tag usage."""
        heading_counts = {}
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            heading_counts[f'h{level}'] = len(headings)
        return heading_counts
    
    def _analyze_paragraph_distribution(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze paragraph usage and distribution."""
        paragraphs = soup.find_all('p')
        if not paragraphs:
            return {'total': 0, 'average_length': 0, 'short': 0, 'medium': 0, 'long': 0}
        
        lengths = [len(p.get_text(strip=True).split()) for p in paragraphs]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        short = len([l for l in lengths if l < 20])
        medium = len([l for l in lengths if 20 <= l <= 50])
        long = len([l for l in lengths if l > 50])
        
        return {
            'total': len(paragraphs),
            'average_length': round(avg_length, 1),
            'short': short,
            'medium': medium,
            'long': long
        }
    
    def _analyze_list_usage(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze list usage for content organization."""
        return {
            'ordered_lists': len(soup.find_all('ol')),
            'unordered_lists': len(soup.find_all('ul')),
            'definition_lists': len(soup.find_all('dl')),
            'total_list_items': len(soup.find_all('li'))
        }
    
    def _analyze_media_elements(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze media element usage."""
        return {
            'images': len(soup.find_all('img')),
            'videos': len(soup.find_all(['video', 'iframe[src*="youtube"]', 'iframe[src*="vimeo"]'])),
            'audio': len(soup.find_all('audio')),
            'figures': len(soup.find_all('figure'))
        }
    
    def _calculate_structural_score(self, soup: BeautifulSoup) -> float:
        """Calculate a structural quality score (0-100)."""
        score = 0
        max_score = 100
        
        # Heading structure (20 points)
        h1_count = len(soup.find_all('h1'))
        if h1_count == 1:
            score += 20
        elif h1_count == 0:
            score += 5
        else:
            score += 10
        
        # Content organization (30 points)
        paragraphs = len(soup.find_all('p'))
        if paragraphs > 0:
            score += min(30, paragraphs * 3)  # 3 points per paragraph, max 30
        
        # List usage (20 points)
        lists = len(soup.find_all(['ul', 'ol']))
        if lists > 0:
            score += min(20, lists * 5)  # 5 points per list, max 20
        
        # Media elements (15 points)
        media = len(soup.find_all(['img', 'video', 'audio']))
        if media > 0:
            score += min(15, media * 2)  # 2 points per media element, max 15
        
        # Semantic elements (15 points)
        semantic = len(soup.find_all(['section', 'article', 'header', 'footer', 'nav', 'main']))
        if semantic > 0:
            score += min(15, semantic * 3)  # 3 points per semantic element, max 15
        
        return min(max_score, score)
    
    def _detect_website_type(self, soup: BeautifulSoup, url: str, content_sections: Dict) -> str:
        """Detect the type of website based on content and structure analysis."""
        
        # Analyze URL patterns
        url_indicators = {
            'blog': ['blog', 'news', 'posts'],
            'portfolio': ['portfolio', 'work', 'projects'],
            'ecommerce': ['shop', 'store', 'buy', 'cart'],
            'corporate': ['company', 'business', 'corporate'],
            'personal': ['about', 'me', 'personal']
        }
        
        url_lower = url.lower()
        url_type_scores = {}
        
        for website_type, keywords in url_indicators.items():
            score = sum(1 for keyword in keywords if keyword in url_lower)
            if score > 0:
                url_type_scores[website_type] = score
        
        # Analyze content patterns
        content_indicators = {
            'blog': ['post', 'article', 'blog', 'published', 'author', 'date'],
            'portfolio': ['project', 'work', 'portfolio', 'case study', 'built', 'developed'],
            'ecommerce': ['product', 'price', 'buy', 'cart', 'shop', 'order'],
            'corporate': ['service', 'business', 'company', 'client', 'solution'],
            'personal': ['about me', 'my', 'i am', 'bio', 'personal'],
            'tech': ['ai', 'machine learning', 'programming', 'developer', 'code', 'technology'],
            'educational': ['tutorial', 'learn', 'guide', 'course', 'education', 'teach']
        }
        
        all_text = ' '.join([
            section_data.get('text', '') 
            for section_data in content_sections.values()
        ]).lower()
        
        content_type_scores = {}
        for website_type, keywords in content_indicators.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                content_type_scores[website_type] = score
        
        # Analyze HTML structure patterns
        structure_indicators = {
            'blog': soup.find_all(['article', '.post', '.blog-post']),
            'portfolio': soup.find_all(['.project', '.portfolio-item', '.work']),
            'ecommerce': soup.find_all(['.product', '.cart', '.shop']),
            'corporate': soup.find_all(['.service', '.solution', '.client'])
        }
        
        structure_type_scores = {}
        for website_type, elements in structure_indicators.items():
            if elements:
                structure_type_scores[website_type] = len(elements)
        
        # Combine scores with weights
        final_scores = {}
        for website_type in set(url_type_scores.keys()) | set(content_type_scores.keys()) | set(structure_type_scores.keys()):
            score = (
                url_type_scores.get(website_type, 0) * 3 +      # URL patterns weight 3
                content_type_scores.get(website_type, 0) * 2 +  # Content patterns weight 2  
                structure_type_scores.get(website_type, 0) * 1  # Structure patterns weight 1
            )
            if score > 0:
                final_scores[website_type] = score
        
        # Determine website type
        if final_scores:
            detected_type = max(final_scores, key=final_scores.get)
            confidence = final_scores[detected_type]
            
            # Special handling for tech/AI sites
            tech_keywords = ['ai', 'machine learning', 'programming', 'developer', 'hackathon']
            tech_score = sum(all_text.count(keyword) for keyword in tech_keywords)
            
            if tech_score > 5:  # Strong tech indicators
                if detected_type == 'blog':
                    return 'tech_blog'
                elif detected_type == 'portfolio':
                    return 'tech_portfolio'
                else:
                    return 'tech_website'
            
            return detected_type
        
        return 'general_website'
    
    def _extract_semantic_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract semantic and structured data information."""
        return {
            'schema_markup': self._extract_schema_markup(soup),
            'open_graph': self._extract_open_graph(soup),
            'twitter_cards': self._extract_twitter_cards(soup),
            'meta_robots': self._extract_meta_robots(soup)
        }
    
    def _extract_schema_markup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Schema.org structured data."""
        schemas = []
        
        # JSON-LD structured data
        json_lds = soup.find_all('script', type='application/ld+json')
        for script in json_lds:
            try:
                data = json.loads(script.string)
                schemas.append({'type': 'json-ld', 'data': data})
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Microdata
        microdata_elements = soup.find_all(attrs={'itemtype': True})
        for element in microdata_elements:
            itemtype = element.get('itemtype', '')
            schemas.append({'type': 'microdata', 'itemtype': itemtype})
        
        return schemas
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph metadata."""
        og_data = {}
        og_metas = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        for meta in og_metas:
            property_name = meta.get('property', '').replace('og:', '')
            content = meta.get('content', '')
            if property_name and content:
                og_data[property_name] = content
        
        return og_data
    
    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card metadata."""
        twitter_data = {}
        twitter_metas = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        for meta in twitter_metas:
            name = meta.get('name', '').replace('twitter:', '')
            content = meta.get('content', '')
            if name and content:
                twitter_data[name] = content
        
        return twitter_data
    
    def _extract_meta_robots(self, soup: BeautifulSoup) -> str:
        """Extract robots meta directive."""
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta:
            return robots_meta.get('content', '')
        return ''
    
    def _assess_content_quality(self, content_sections: Dict, word_count: int) -> Dict[str, Any]:
        """Assess overall content quality and provide recommendations."""
        quality_score = 0
        max_score = 100
        quality_issues = []
        quality_strengths = []
        
        # Word count assessment (30 points)
        if word_count >= 1000:
            quality_score += 30
            quality_strengths.append("Comprehensive content length")
        elif word_count >= 500:
            quality_score += 20
            quality_strengths.append("Good content length")
        elif word_count >= 300:
            quality_score += 10
            quality_issues.append("Content could be more comprehensive")
        else:
            quality_issues.append("Content is too thin - consider expanding")
        
        # Content diversity (25 points)
        section_count = len(content_sections)
        if section_count >= 4:
            quality_score += 25
            quality_strengths.append("Diverse content sections")
        elif section_count >= 2:
            quality_score += 15
        else:
            quality_score += 5
            quality_issues.append("Content lacks structural diversity")
        
        # Content depth (25 points)
        main_content = content_sections.get('main_content', {})
        if main_content.get('word_count', 0) >= 500:
            quality_score += 25
            quality_strengths.append("Deep main content")
        elif main_content.get('word_count', 0) >= 200:
            quality_score += 15
        else:
            quality_issues.append("Main content needs expansion")
        
        # Specialized content (20 points)
        specialized_sections = ['projects', 'articles', 'services', 'about']
        specialized_count = sum(1 for section in specialized_sections if section in content_sections)
        quality_score += min(20, specialized_count * 5)
        
        if specialized_count >= 2:
            quality_strengths.append("Good specialized content variety")
        
        return {
            'quality_score': min(max_score, quality_score),
            'issues': quality_issues,
            'strengths': quality_strengths,
            'word_count_assessment': self._get_word_count_assessment(word_count),
            'content_depth_level': self._get_content_depth_level(word_count, section_count)
        }
    
    def _get_word_count_assessment(self, word_count: int) -> str:
        """Get word count assessment category."""
        if word_count >= 1500:
            return "comprehensive"
        elif word_count >= 800:
            return "substantial"
        elif word_count >= 400:
            return "adequate"
        elif word_count >= 200:
            return "minimal"
        else:
            return "insufficient"
    
    def _get_content_depth_level(self, word_count: int, section_count: int) -> str:
        """Determine content depth level based on multiple factors."""
        depth_score = (word_count / 100) + (section_count * 5)
        
        if depth_score >= 50:
            return "deep"
        elif depth_score >= 30:
            return "moderate"
        elif depth_score >= 15:
            return "basic"
        else:
            return "shallow"
    
    def _fallback_content_extraction(self, html: str) -> Dict[str, Any]:
        """Fallback content extraction method."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove non-content elements
            for element in soup(['script', 'style', 'nav', 'footer']):
                element.decompose()
            
            # Get all text
            text_content = soup.get_text(separator=' ', strip=True)
            word_count = len(text_content.split())
            
            return {
                'content_sections': {
                    'main_content': {
                        'text': text_content,
                        'word_count': word_count,
                        'importance_weight': 1.0
                    }
                },
                'total_word_count': word_count,
                'website_type': 'general_website',
                'extraction_method': 'fallback_basic',
                'content_quality': {
                    'quality_score': 50,
                    'issues': ['Used fallback extraction - may not be fully accurate'],
                    'strengths': [],
                    'word_count_assessment': self._get_word_count_assessment(word_count),
                    'content_depth_level': 'basic'
                }
            }
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return {
                'content_sections': {},
                'total_word_count': 0,
                'website_type': 'unknown',
                'extraction_method': 'failed',
                'content_quality': {
                    'quality_score': 0,
                    'issues': ['Content extraction failed'],
                    'strengths': [],
                    'word_count_assessment': 'insufficient',
                    'content_depth_level': 'none'
                }
            }


class WebsiteTypeDetector:
    """Advanced website type detection and categorization."""
    
    @staticmethod
    def detect_website_type_advanced(content_analysis: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Advanced website type detection with confidence scoring.
        
        Returns detailed website type analysis including:
        - Primary type
        - Secondary types
        - Confidence scores
        - Industry classification
        - Target audience
        """
        detector = AdvancedContentAnalyzer()
        
        # Use existing detection logic but add more sophisticated analysis
        website_type = content_analysis.get('website_type', 'general_website')
        
        # Industry classification
        industry = WebsiteTypeDetector._classify_industry(content_analysis, url)
        
        # Target audience detection
        audience = WebsiteTypeDetector._detect_target_audience(content_analysis)
        
        # Business model detection
        business_model = WebsiteTypeDetector._detect_business_model(content_analysis)
        
        return {
            'primary_type': website_type,
            'industry': industry,
            'target_audience': audience,
            'business_model': business_model,
            'confidence_score': WebsiteTypeDetector._calculate_confidence(content_analysis),
            'optimization_focus': WebsiteTypeDetector._get_optimization_focus(website_type, industry)
        }
    
    @staticmethod
    def _classify_industry(content_analysis: Dict[str, Any], url: str) -> str:
        """Classify the industry/niche of the website."""
        
        # Extract all text content for analysis
        all_text = ""
        for section_data in content_analysis.get('content_sections', {}).values():
            all_text += section_data.get('text', '') + " "
        
        all_text = all_text.lower()
        
        industry_keywords = {
            'technology': ['ai', 'artificial intelligence', 'machine learning', 'programming', 'software', 'developer', 'tech', 'code', 'algorithm', 'data science'],
            'healthcare': ['health', 'medical', 'doctor', 'patient', 'treatment', 'medicine', 'therapy', 'hospital', 'clinic'],
            'finance': ['finance', 'financial', 'investment', 'banking', 'money', 'loan', 'insurance', 'trading', 'wealth'],
            'education': ['education', 'learning', 'course', 'tutorial', 'teaching', 'student', 'school', 'university', 'training'],
            'ecommerce': ['shop', 'store', 'buy', 'sell', 'product', 'price', 'cart', 'order', 'payment', 'shipping'],
            'marketing': ['marketing', 'advertising', 'seo', 'social media', 'campaign', 'brand', 'promotion', 'digital marketing'],
            'design': ['design', 'creative', 'graphic', 'ui', 'ux', 'visual', 'art', 'portfolio', 'branding'],
            'consulting': ['consulting', 'consultant', 'advisory', 'expertise', 'strategy', 'solutions', 'professional services'],
            'real_estate': ['real estate', 'property', 'house', 'apartment', 'rent', 'buy', 'sell', 'mortgage', 'realtor'],
            'food': ['food', 'restaurant', 'recipe', 'cooking', 'chef', 'cuisine', 'dining', 'menu', 'catering']
        }
        
        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        
        return 'general'
    
    @staticmethod
    def _detect_target_audience(content_analysis: Dict[str, Any]) -> str:
        """Detect the target audience of the website."""
        
        all_text = ""
        for section_data in content_analysis.get('content_sections', {}).values():
            all_text += section_data.get('text', '') + " "
        
        all_text = all_text.lower()
        
        audience_indicators = {
            'b2b': ['business', 'enterprise', 'company', 'corporate', 'professional', 'industry', 'client', 'partnership'],
            'b2c': ['customer', 'consumer', 'individual', 'personal', 'family', 'home', 'lifestyle', 'you'],
            'developers': ['developer', 'programmer', 'code', 'api', 'github', 'technical', 'documentation', 'sdk'],
            'students': ['student', 'learn', 'beginner', 'tutorial', 'course', 'education', 'study'],
            'professionals': ['professional', 'career', 'expert', 'specialist', 'advanced', 'industry', 'certification']
        }
        
        audience_scores = {}
        for audience, keywords in audience_indicators.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                audience_scores[audience] = score
        
        if audience_scores:
            return max(audience_scores, key=audience_scores.get)
        
        return 'general'
    
    @staticmethod
    def _detect_business_model(content_analysis: Dict[str, Any]) -> str:
        """Detect the business model of the website."""
        
        all_text = ""
        for section_data in content_analysis.get('content_sections', {}).values():
            all_text += section_data.get('text', '') + " "
        
        all_text = all_text.lower()
        
        business_model_indicators = {
            'saas': ['subscription', 'monthly', 'yearly', 'plan', 'pricing', 'tier', 'free trial', 'software as a service'],
            'ecommerce': ['buy', 'shop', 'cart', 'checkout', 'product', 'shipping', 'return policy'],
            'service': ['service', 'consultation', 'hire', 'contact', 'quote', 'proposal'],
            'content': ['blog', 'article', 'content', 'newsletter', 'subscribe', 'read more'],
            'portfolio': ['portfolio', 'work', 'project', 'case study', 'gallery'],
            'lead_generation': ['contact', 'form', 'inquiry', 'get started', 'free quote', 'consultation']
        }
        
        model_scores = {}
        for model, keywords in business_model_indicators.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                model_scores[model] = score
        
        if model_scores:
            return max(model_scores, key=model_scores.get)
        
        return 'informational'
    
    @staticmethod
    def _calculate_confidence(content_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for website type detection."""
        
        factors = []
        
        # Content volume factor
        word_count = content_analysis.get('total_word_count', 0)
        if word_count >= 1000:
            factors.append(0.9)
        elif word_count >= 500:
            factors.append(0.7)
        elif word_count >= 200:
            factors.append(0.5)
        else:
            factors.append(0.3)
        
        # Content diversity factor
        section_count = len(content_analysis.get('content_sections', {}))
        if section_count >= 4:
            factors.append(0.9)
        elif section_count >= 2:
            factors.append(0.7)
        else:
            factors.append(0.4)
        
        # Extraction method factor
        extraction_method = content_analysis.get('extraction_method', 'fallback_basic')
        if extraction_method == 'enhanced_comprehensive':
            factors.append(0.9)
        elif extraction_method == 'fallback_basic':
            factors.append(0.6)
        else:
            factors.append(0.3)
        
        # Calculate average confidence
        if factors:
            return round(sum(factors) / len(factors), 2)
        
        return 0.5
    
    @staticmethod
    def _get_optimization_focus(website_type: str, industry: str) -> List[str]:
        """Get SEO optimization focus areas based on website type and industry."""
        
        optimization_strategies = {
            'tech_blog': ['technical_content', 'code_examples', 'tutorial_structure', 'developer_keywords'],
            'tech_portfolio': ['project_showcasing', 'skill_demonstration', 'case_studies', 'professional_branding'],
            'blog': ['content_freshness', 'topic_clusters', 'internal_linking', 'author_authority'],
            'portfolio': ['visual_optimization', 'project_descriptions', 'skill_keywords', 'contact_optimization'],
            'ecommerce': ['product_optimization', 'category_structure', 'review_management', 'local_seo'],
            'corporate': ['service_descriptions', 'trust_signals', 'local_seo', 'industry_authority'],
            'personal': ['personal_branding', 'about_optimization', 'contact_information', 'social_proof']
        }
        
        base_focus = optimization_strategies.get(website_type, ['general_seo', 'content_quality', 'technical_optimization'])
        
        # Add industry-specific focus areas
        industry_focus = {
            'technology': ['technical_keywords', 'innovation_content', 'developer_audience'],
            'healthcare': ['trust_signals', 'professional_credentials', 'patient_focus'],
            'finance': ['security_emphasis', 'regulatory_compliance', 'trust_building'],
            'education': ['learning_outcomes', 'educational_structure', 'accessibility']
        }
        
        if industry in industry_focus:
            base_focus.extend(industry_focus[industry])
        
        return list(set(base_focus))  # Remove duplicates