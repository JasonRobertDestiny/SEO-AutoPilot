#!/usr/bin/env python3
"""
Sitemap Generator Module

Generates XML sitemaps from website crawl data for SEO optimization.
This module creates standards-compliant XML sitemaps that can be submitted
to search engines to improve website indexing.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import re


class SitemapGenerator:
    """
    Generates XML sitemaps from crawled website data.
    
    Creates standards-compliant sitemaps following the sitemaps.org protocol
    with proper URL prioritization based on SEO analysis results.
    """
    
    def __init__(self):
        """Initialize the sitemap generator."""
        self.namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        
        # Priority scoring based on page characteristics
        self.priority_rules = {
            'homepage': 1.0,
            'main_pages': 0.8,
            'content_pages': 0.6,
            'deep_pages': 0.4,
            'default': 0.5
        }
        
        # Change frequency patterns
        self.changefreq_patterns = {
            'homepage': 'daily',
            'blog': 'weekly',
            'news': 'daily',
            'products': 'monthly',
            'static': 'yearly',
            'default': 'monthly'
        }
    
    def generate_sitemap(self, crawl_results: Dict[str, Any], base_url: str) -> str:
        """
        Generate XML sitemap from crawl results.
        
        Args:
            crawl_results: Results from website analysis containing page data
            base_url: Base URL of the website
            
        Returns:
            str: XML sitemap content
        """
        # Create root element with namespace
        urlset = ET.Element("urlset")
        urlset.set("xmlns", self.namespace)
        
        # Extract URLs from crawl results
        urls = self._extract_urls_from_results(crawl_results, base_url)
        
        # Process each URL
        for url_data in urls:
            url_element = self._create_url_element(url_data)
            if url_element is not None:
                urlset.append(url_element)
        
        # Create XML tree and return as string
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)
        
        # Convert to string with XML declaration
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += ET.tostring(urlset, encoding='unicode', method='xml')
        
        return xml_str
    
    def _extract_urls_from_results(self, crawl_results: Dict[str, Any], base_url: str) -> List[Dict[str, Any]]:
        """
        Extract and process URLs from crawl results.
        
        Args:
            crawl_results: Website analysis results
            base_url: Base URL of the website
            
        Returns:
            List[Dict]: Processed URL data with metadata
        """
        urls = []
        base_domain = urlparse(base_url).netloc
        
        # Add homepage first
        urls.append({
            'url': base_url.rstrip('/') + '/',
            'priority': self.priority_rules['homepage'],
            'changefreq': self.changefreq_patterns['homepage'],
            'lastmod': datetime.now(timezone.utc).isoformat(),
            'is_homepage': True
        })
        
        # Process pages from crawl results
        if 'page_results' in crawl_results:
            for page_result in crawl_results['page_results']:
                if page_result.get('url'):
                    url = page_result['url']
                    
                    # Skip if not from same domain
                    if not self._is_same_domain(url, base_domain):
                        continue
                    
                    # Skip if already added (homepage)
                    if any(existing['url'] == url for existing in urls):
                        continue
                    
                    url_data = self._analyze_url_characteristics(url, page_result)
                    urls.append(url_data)
        
        # If no page_results, try to extract from other sources
        elif 'results' in crawl_results and 'pages' in crawl_results['results']:
            for page_url in crawl_results['results']['pages']:
                if not self._is_same_domain(page_url, base_domain):
                    continue
                    
                if any(existing['url'] == page_url for existing in urls):
                    continue
                
                url_data = self._analyze_url_characteristics(page_url, {})
                urls.append(url_data)
        
        return urls
    
    def _create_url_element(self, url_data: Dict[str, Any]) -> Optional[ET.Element]:
        """
        Create XML element for a single URL.
        
        Args:
            url_data: URL data with metadata
            
        Returns:
            ET.Element: XML url element or None if invalid
        """
        try:
            url_element = ET.Element("url")
            
            # Required: loc element
            loc = ET.SubElement(url_element, "loc")
            loc.text = url_data['url']
            
            # Optional: lastmod
            if url_data.get('lastmod'):
                lastmod = ET.SubElement(url_element, "lastmod")
                lastmod.text = url_data['lastmod']
            
            # Optional: changefreq
            if url_data.get('changefreq'):
                changefreq = ET.SubElement(url_element, "changefreq")
                changefreq.text = url_data['changefreq']
            
            # Optional: priority
            if url_data.get('priority') is not None:
                priority = ET.SubElement(url_element, "priority")
                priority.text = f"{url_data['priority']:.1f}"
            
            return url_element
            
        except Exception as e:
            print(f"Error creating URL element for {url_data.get('url', 'unknown')}: {e}")
            return None
    
    def _analyze_url_characteristics(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze URL characteristics to determine priority and change frequency.
        
        Args:
            url: The URL to analyze
            page_data: Page analysis data
            
        Returns:
            Dict: URL data with calculated metadata
        """
        url_lower = url.lower()
        path = urlparse(url).path.lower()
        
        # Determine URL type and priority
        priority = self.priority_rules['default']
        changefreq = self.changefreq_patterns['default']
        
        # Homepage detection
        if path in ['/', '']:
            priority = self.priority_rules['homepage']
            changefreq = self.changefreq_patterns['homepage']
        
        # Main sections (higher priority)
        elif any(section in path for section in ['/about', '/contact', '/services', '/products']):
            priority = self.priority_rules['main_pages']
            changefreq = self.changefreq_patterns['static']
        
        # Blog/news content
        elif any(pattern in path for pattern in ['/blog', '/news', '/article']):
            priority = self.priority_rules['content_pages']
            changefreq = self.changefreq_patterns['blog']
        
        # Product pages
        elif any(pattern in path for pattern in ['/product', '/item', '/shop']):
            priority = self.priority_rules['content_pages']
            changefreq = self.changefreq_patterns['products']
        
        # Deep pages (lower priority)
        elif path.count('/') > 3:
            priority = self.priority_rules['deep_pages']
        
        # Adjust priority based on page analysis if available
        if page_data:
            priority = self._adjust_priority_by_analysis(priority, page_data)
        
        return {
            'url': url,
            'priority': min(1.0, max(0.1, priority)),  # Clamp between 0.1 and 1.0
            'changefreq': changefreq,
            'lastmod': datetime.now(timezone.utc).isoformat(),
            'is_homepage': path in ['/', '']
        }
    
    def _adjust_priority_by_analysis(self, base_priority: float, page_data: Dict[str, Any]) -> float:
        """
        Adjust URL priority based on page analysis results.
        
        Args:
            base_priority: Base priority score
            page_data: Page analysis data
            
        Returns:
            float: Adjusted priority score
        """
        priority = base_priority
        
        # Boost priority for pages with good SEO characteristics
        if page_data.get('title') and len(page_data['title']) > 10:
            priority += 0.1
        
        if page_data.get('description') and len(page_data['description']) > 50:
            priority += 0.1
        
        if page_data.get('headings') and len(page_data['headings']) > 0:
            priority += 0.1
        
        # Reduce priority for pages with issues
        if page_data.get('issues'):
            issues_count = len(page_data['issues'])
            priority -= min(0.3, issues_count * 0.05)
        
        return priority
    
    def _is_same_domain(self, url: str, base_domain: str) -> bool:
        """
        Check if URL belongs to the same domain.
        
        Args:
            url: URL to check
            base_domain: Base domain to compare against
            
        Returns:
            bool: True if same domain
        """
        try:
            url_domain = urlparse(url).netloc
            return url_domain.lower() == base_domain.lower()
        except:
            return False
    
    def validate_sitemap(self, sitemap_xml: str) -> Dict[str, Any]:
        """
        Validate generated sitemap XML.
        
        Args:
            sitemap_xml: XML sitemap content
            
        Returns:
            Dict: Validation results
        """
        try:
            root = ET.fromstring(sitemap_xml)
            
            # Check namespace
            if root.tag != f"{{{self.namespace}}}urlset":
                return {
                    'valid': False,
                    'error': 'Invalid root element or namespace'
                }
            
            urls = root.findall(f"{{{self.namespace}}}url")
            url_count = len(urls)
            
            # Check URL count limit (50,000 per sitemap)
            if url_count > 50000:
                return {
                    'valid': False,
                    'error': f'Too many URLs ({url_count}). Maximum is 50,000.'
                }
            
            # Validate each URL
            for url_elem in urls:
                loc_elem = url_elem.find(f"{{{self.namespace}}}loc")
                if loc_elem is None or not loc_elem.text:
                    return {
                        'valid': False,
                        'error': 'URL missing required loc element'
                    }
            
            return {
                'valid': True,
                'url_count': url_count,
                'size_bytes': len(sitemap_xml.encode('utf-8'))
            }
            
        except ET.ParseError as e:
            return {
                'valid': False,
                'error': f'XML parsing error: {str(e)}'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }


def generate_sitemap_from_analysis(website_url: str, analysis_results: Dict[str, Any]) -> str:
    """
    Convenience function to generate sitemap from analysis results.
    
    Args:
        website_url: Base URL of the website
        analysis_results: Results from website analysis
        
    Returns:
        str: XML sitemap content
    """
    generator = SitemapGenerator()
    return generator.generate_sitemap(analysis_results, website_url)