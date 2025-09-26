"""
Competitive Intelligence and Market Analysis System

This module provides comprehensive competitive analysis, market positioning,
and strategic insights for SEO optimization. It integrates with the niche-specific
analyzer to provide contextual competitive intelligence.
"""

import json
import asyncio
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from urllib.parse import urlparse, urljoin
from collections import Counter
import re

logger = logging.getLogger(__name__)

class CompetitiveAdvantage(Enum):
    """Types of competitive advantages."""
    CONTENT_DEPTH = "content_depth"
    TECHNICAL_PERFORMANCE = "technical_performance"
    USER_EXPERIENCE = "user_experience"
    BRAND_AUTHORITY = "brand_authority"
    NICHE_EXPERTISE = "niche_expertise"
    INNOVATION = "innovation"
    LOCAL_PRESENCE = "local_presence"

class MarketPosition(Enum):
    """Market positioning categories."""
    MARKET_LEADER = "market_leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE_PLAYER = "niche_player"
    NEWCOMER = "newcomer"

@dataclass
class CompetitorProfile:
    """Profile of a competitor."""
    domain: str
    estimated_authority: int
    content_volume: int
    technical_score: int
    niche_relevance: float
    competitive_advantages: List[CompetitiveAdvantage]
    market_position: MarketPosition
    strengths: List[str]
    weaknesses: List[str]
    opportunity_gaps: List[str]

@dataclass
class CompetitiveAnalysisResult:
    """Result of competitive analysis."""
    market_overview: Dict[str, Any]
    competitor_profiles: List[CompetitorProfile]
    market_positioning: Dict[str, Any]
    competitive_gaps: List[Dict[str, Any]]
    strategic_recommendations: List[Dict[str, Any]]
    keyword_opportunities: List[str]
    content_opportunities: List[str]
    technical_opportunities: List[str]
    market_trends: List[str]

class CompetitiveIntelligenceSystem:
    """Advanced competitive intelligence and market analysis system."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SEO-AutoPilot-Competitive-Intelligence/1.0'
        })
        
        # Market intelligence databases
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.competitive_keywords = self._load_competitive_keywords()
        self.market_trends = self._load_market_trends()
    
    async def analyze_competitive_landscape(self, 
                                          website_data: Dict[str, Any],
                                          niche_analysis: Dict[str, Any],
                                          content_analysis: Dict[str, Any],
                                          technical_analysis: Dict[str, Any] = None) -> CompetitiveAnalysisResult:
        """
        Perform comprehensive competitive landscape analysis.
        
        Args:
            website_data: Basic website information
            niche_analysis: Results from niche-specific analyzer
            content_analysis: Enhanced content analysis results
            technical_analysis: Technical performance analysis
            
        Returns:
            CompetitiveAnalysisResult with comprehensive competitive intelligence
        """
        try:
            # 1. Identify competitive landscape
            market_overview = await self._analyze_market_overview(niche_analysis, website_data)
            
            # 2. Discover and profile competitors
            competitor_profiles = await self._discover_and_profile_competitors(
                website_data, niche_analysis, content_analysis
            )
            
            # 3. Analyze market positioning
            market_positioning = await self._analyze_market_positioning(
                website_data, competitor_profiles, niche_analysis
            )
            
            # 4. Identify competitive gaps and opportunities
            competitive_gaps = await self._identify_competitive_gaps(
                website_data, competitor_profiles, content_analysis, technical_analysis
            )
            
            # 5. Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                market_positioning, competitive_gaps, niche_analysis
            )
            
            # 6. Identify keyword opportunities
            keyword_opportunities = await self._identify_keyword_opportunities(
                niche_analysis, competitor_profiles, content_analysis
            )
            
            # 7. Analyze content opportunities
            content_opportunities = await self._analyze_content_opportunities(
                competitor_profiles, content_analysis, niche_analysis
            )
            
            # 8. Identify technical opportunities
            technical_opportunities = await self._identify_technical_opportunities(
                competitor_profiles, technical_analysis
            )
            
            # 9. Analyze market trends
            market_trends = await self._analyze_market_trends(niche_analysis, competitor_profiles)
            
            return CompetitiveAnalysisResult(
                market_overview=market_overview,
                competitor_profiles=competitor_profiles,
                market_positioning=market_positioning,
                competitive_gaps=competitive_gaps,
                strategic_recommendations=strategic_recommendations,
                keyword_opportunities=keyword_opportunities,
                content_opportunities=content_opportunities,
                technical_opportunities=technical_opportunities,
                market_trends=market_trends
            )
            
        except Exception as e:
            logger.error(f"Competitive analysis failed: {e}")
            return self._create_fallback_competitive_analysis()
    
    async def _analyze_market_overview(self, niche_analysis: Dict, website_data: Dict) -> Dict[str, Any]:
        """Analyze overall market landscape and characteristics."""
        
        website_type = niche_analysis.get('website_type', 'corporate')
        industry = niche_analysis.get('industry', 'technology')
        
        # Market size and competition assessment
        market_characteristics = {
            'market_size': self._assess_market_size(industry, website_type),
            'competition_level': self._assess_competition_level(industry, website_type),
            'market_maturity': self._assess_market_maturity(industry),
            'growth_stage': self._assess_growth_stage(industry, website_type),
            'barrier_to_entry': self._assess_barriers_to_entry(industry, website_type),
            'key_success_factors': self._identify_success_factors(industry, website_type),
            'market_dynamics': self._analyze_market_dynamics(industry),
            'seasonal_patterns': self._identify_seasonal_patterns(industry)
        }
        
        return market_characteristics
    
    async def _discover_and_profile_competitors(self, 
                                              website_data: Dict, 
                                              niche_analysis: Dict, 
                                              content_analysis: Dict) -> List[CompetitorProfile]:
        """Discover and create detailed profiles of competitors."""
        
        competitors = []
        
        # Strategy 1: Industry-based competitor discovery
        industry_competitors = self._discover_industry_competitors(
            niche_analysis.get('industry', 'technology'),
            niche_analysis.get('website_type', 'corporate')
        )
        
        # Strategy 2: Keyword-based competitor discovery
        target_keywords = niche_analysis.get('target_keywords', [])
        keyword_competitors = self._discover_keyword_competitors(target_keywords[:5])
        
        # Strategy 3: Content-based competitor discovery
        content_competitors = self._discover_content_competitors(
            content_analysis, niche_analysis
        )
        
        # Combine and deduplicate competitors
        all_competitors = list(set(
            industry_competitors + keyword_competitors + content_competitors
        ))
        
        # Profile each competitor
        for competitor_domain in all_competitors[:10]:  # Limit to top 10
            try:
                profile = await self._create_competitor_profile(
                    competitor_domain, niche_analysis, website_data
                )
                if profile:
                    competitors.append(profile)
            except Exception as e:
                logger.warning(f"Failed to profile competitor {competitor_domain}: {e}")
                continue
        
        return competitors
    
    async def _create_competitor_profile(self, 
                                       domain: str, 
                                       niche_analysis: Dict, 
                                       website_data: Dict) -> Optional[CompetitorProfile]:
        """Create detailed profile for a competitor."""
        
        try:
            # Estimate domain authority and metrics
            authority_score = self._estimate_domain_authority(domain)
            content_volume = self._estimate_content_volume(domain)
            technical_score = self._estimate_technical_score(domain)
            niche_relevance = self._calculate_niche_relevance(domain, niche_analysis)
            
            # Analyze competitive advantages
            competitive_advantages = self._identify_competitive_advantages(
                domain, niche_analysis, authority_score, technical_score
            )
            
            # Determine market position
            market_position = self._determine_market_position(
                authority_score, content_volume, niche_relevance
            )
            
            # Analyze strengths and weaknesses
            strengths, weaknesses = self._analyze_strengths_weaknesses(
                domain, competitive_advantages, technical_score
            )
            
            # Identify opportunity gaps
            opportunity_gaps = self._identify_opportunity_gaps_for_competitor(
                domain, niche_analysis, strengths, weaknesses
            )
            
            return CompetitorProfile(
                domain=domain,
                estimated_authority=authority_score,
                content_volume=content_volume,
                technical_score=technical_score,
                niche_relevance=niche_relevance,
                competitive_advantages=competitive_advantages,
                market_position=market_position,
                strengths=strengths,
                weaknesses=weaknesses,
                opportunity_gaps=opportunity_gaps
            )
            
        except Exception as e:
            logger.error(f"Failed to create profile for {domain}: {e}")
            return None
    
    async def _analyze_market_positioning(self, 
                                        website_data: Dict, 
                                        competitor_profiles: List[CompetitorProfile], 
                                        niche_analysis: Dict) -> Dict[str, Any]:
        """Analyze market positioning relative to competitors."""
        
        current_domain = urlparse(website_data.get('url', '')).netloc
        
        # Calculate current site's estimated metrics
        current_authority = self._estimate_current_site_authority(website_data, niche_analysis)
        current_content_volume = self._estimate_current_content_volume(website_data, niche_analysis)
        current_technical_score = self._estimate_current_technical_score(website_data)
        
        # Position analysis
        authority_percentile = self._calculate_percentile(
            current_authority, [c.estimated_authority for c in competitor_profiles]
        )
        
        content_percentile = self._calculate_percentile(
            current_content_volume, [c.content_volume for c in competitor_profiles]
        )
        
        technical_percentile = self._calculate_percentile(
            current_technical_score, [c.technical_score for c in competitor_profiles]
        )
        
        # Overall market position
        overall_score = (authority_percentile + content_percentile + technical_percentile) / 3
        market_position = self._determine_market_position(
            current_authority, current_content_volume, 1.0  # Perfect niche relevance for own site
        )
        
        return {
            'current_position': market_position.value,
            'authority_percentile': authority_percentile,
            'content_percentile': content_percentile,
            'technical_percentile': technical_percentile,
            'overall_score': overall_score,
            'positioning_strategy': self._recommend_positioning_strategy(
                market_position, authority_percentile, content_percentile, technical_percentile
            ),
            'competitive_threats': self._identify_competitive_threats(competitor_profiles),
            'market_opportunities': self._identify_market_opportunities(
                competitor_profiles, niche_analysis
            )
        }
    
    async def _identify_competitive_gaps(self, 
                                       website_data: Dict, 
                                       competitor_profiles: List[CompetitorProfile], 
                                       content_analysis: Dict, 
                                       technical_analysis: Dict = None) -> List[Dict[str, Any]]:
        """Identify gaps in competitive landscape that can be exploited."""
        
        gaps = []
        
        # Content gaps
        content_gaps = self._identify_content_gaps(competitor_profiles, content_analysis)
        gaps.extend([{'type': 'content', **gap} for gap in content_gaps])
        
        # Technical gaps
        if technical_analysis:
            technical_gaps = self._identify_technical_gaps(competitor_profiles, technical_analysis)
            gaps.extend([{'type': 'technical', **gap} for gap in technical_gaps])
        
        # Keyword gaps
        keyword_gaps = self._identify_keyword_gaps(competitor_profiles, content_analysis)
        gaps.extend([{'type': 'keyword', **gap} for gap in keyword_gaps])
        
        # User experience gaps
        ux_gaps = self._identify_ux_gaps(competitor_profiles)
        gaps.extend([{'type': 'user_experience', **gap} for gap in ux_gaps])
        
        # Innovation gaps
        innovation_gaps = self._identify_innovation_gaps(competitor_profiles, content_analysis)
        gaps.extend([{'type': 'innovation', **gap} for gap in innovation_gaps])
        
        return gaps[:15]  # Return top 15 opportunities
    
    async def _generate_strategic_recommendations(self, 
                                                market_positioning: Dict, 
                                                competitive_gaps: List[Dict], 
                                                niche_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on competitive analysis."""
        
        recommendations = []
        
        # Positioning-based recommendations
        current_position = market_positioning.get('current_position', 'follower')
        
        if current_position == 'newcomer':
            recommendations.extend(self._get_newcomer_strategies(competitive_gaps, niche_analysis))
        elif current_position == 'niche_player':
            recommendations.extend(self._get_niche_player_strategies(competitive_gaps, niche_analysis))
        elif current_position == 'follower':
            recommendations.extend(self._get_follower_strategies(competitive_gaps, market_positioning))
        elif current_position == 'challenger':
            recommendations.extend(self._get_challenger_strategies(competitive_gaps, market_positioning))
        
        # Gap-based recommendations
        for gap in competitive_gaps[:10]:  # Top 10 gaps
            recommendations.append(self._create_gap_recommendation(gap, niche_analysis))
        
        # Prioritize recommendations
        prioritized_recommendations = self._prioritize_recommendations(
            recommendations, market_positioning, niche_analysis
        )
        
        return prioritized_recommendations[:20]  # Top 20 strategic recommendations
    
    # Helper methods for competitive discovery
    
    def _discover_industry_competitors(self, industry: str, website_type: str) -> List[str]:
        """Discover competitors based on industry classification."""
        
        # Simulated competitor discovery - in production, this would integrate with:
        # - SimilarWeb API, SEMrush API, Ahrefs API
        # - Industry databases and directories
        # - Google search results analysis
        
        industry_competitors = {
            'technology': {
                'tech_blog': ['techcrunch.com', 'hackernoon.com', 'dev.to', 'medium.com'],
                'tech_portfolio': ['github.com', 'dribbble.com', 'behance.net'],
                'saas': ['producthunt.com', 'g2.com', 'capterra.com'],
                'corporate': ['microsoft.com', 'google.com', 'apple.com']
            },
            'healthcare': {
                'corporate': ['mayo.edu', 'webmd.com', 'healthline.com'],
                'blog': ['medicalnewstoday.com', 'healthline.com']
            },
            'finance': {
                'corporate': ['jpmorgan.com', 'bankofamerica.com', 'wellsfargo.com'],
                'blog': ['investopedia.com', 'fool.com']
            },
            'education': {
                'educational': ['coursera.org', 'udemy.com', 'khanacademy.org'],
                'blog': ['edutopia.org', 'teachhub.com']
            }
        }
        
        return industry_competitors.get(industry, {}).get(website_type, [])
    
    def _discover_keyword_competitors(self, target_keywords: List[str]) -> List[str]:
        """Discover competitors based on target keywords."""
        
        # Simulated keyword-based competitor discovery
        # In production, this would analyze search results for target keywords
        
        keyword_competitors = []
        
        for keyword in target_keywords[:3]:  # Analyze top 3 keywords
            if 'ai' in keyword.lower() or 'machine learning' in keyword.lower():
                keyword_competitors.extend(['openai.com', 'huggingface.co', 'kaggle.com'])
            elif 'web development' in keyword.lower() or 'programming' in keyword.lower():
                keyword_competitors.extend(['stackoverflow.com', 'freecodecamp.org', 'w3schools.com'])
            elif 'seo' in keyword.lower():
                keyword_competitors.extend(['moz.com', 'semrush.com', 'ahrefs.com'])
        
        return list(set(keyword_competitors))
    
    def _discover_content_competitors(self, content_analysis: Dict, niche_analysis: Dict) -> List[str]:
        """Discover competitors based on content characteristics."""
        
        content_competitors = []
        
        # Analyze content type and find similar sites
        total_word_count = content_analysis.get('total_word_count', 0)
        website_type = niche_analysis.get('website_type', 'corporate')
        
        if total_word_count > 2000 and 'blog' in website_type:
            content_competitors.extend(['medium.com', 'substack.com', 'ghost.org'])
        elif 'portfolio' in website_type:
            content_competitors.extend(['dribbble.com', 'behance.net', 'awwwards.com'])
        elif 'tech' in website_type:
            content_competitors.extend(['github.com', 'gitlab.com', 'stackoverflow.com'])
        
        return content_competitors
    
    # Helper methods for competitor analysis
    
    def _estimate_domain_authority(self, domain: str) -> int:
        """Estimate domain authority score (0-100)."""
        
        # Simplified domain authority estimation
        # In production, this would integrate with Moz API, Ahrefs API, etc.
        
        domain_scores = {
            'google.com': 95, 'microsoft.com': 92, 'apple.com': 90,
            'github.com': 88, 'stackoverflow.com': 85, 'medium.com': 82,
            'techcrunch.com': 78, 'hackernoon.com': 65, 'dev.to': 70
        }
        
        # Default scoring based on domain characteristics
        base_score = domain_scores.get(domain, 40)
        
        # Adjust based on TLD and domain length
        if domain.endswith('.edu'):
            base_score += 15
        elif domain.endswith('.gov'):
            base_score += 20
        elif domain.endswith('.org'):
            base_score += 5
        
        return min(100, base_score)
    
    def _estimate_content_volume(self, domain: str) -> int:
        """Estimate content volume (pages/articles)."""
        
        # Simplified content volume estimation
        # In production, this would crawl sitemaps or use search operators
        
        volume_estimates = {
            'medium.com': 10000000, 'github.com': 5000000, 'stackoverflow.com': 2000000,
            'techcrunch.com': 100000, 'hackernoon.com': 50000, 'dev.to': 200000
        }
        
        return volume_estimates.get(domain, 1000)
    
    def _estimate_technical_score(self, domain: str) -> int:
        """Estimate technical performance score (0-100)."""
        
        # Simplified technical scoring
        # In production, this would use PageSpeed Insights API
        
        tech_scores = {
            'google.com': 95, 'microsoft.com': 90, 'apple.com': 88,
            'github.com': 85, 'stackoverflow.com': 82, 'medium.com': 78
        }
        
        return tech_scores.get(domain, 75)
    
    def _calculate_niche_relevance(self, domain: str, niche_analysis: Dict) -> float:
        """Calculate how relevant the competitor is to the current niche (0-1)."""
        
        website_type = niche_analysis.get('website_type', 'corporate')
        industry = niche_analysis.get('industry', 'technology')
        
        # Domain-specific relevance scoring
        relevance_scores = {
            ('tech_blog', 'technology'): {
                'techcrunch.com': 0.9, 'hackernoon.com': 0.8, 'dev.to': 0.85,
                'medium.com': 0.7, 'github.com': 0.6
            },
            ('tech_portfolio', 'technology'): {
                'github.com': 0.95, 'dribbble.com': 0.8, 'behance.net': 0.75
            }
        }
        
        key = (website_type, industry)
        if key in relevance_scores:
            return relevance_scores[key].get(domain, 0.5)
        
        return 0.5  # Default moderate relevance
    
    def _identify_competitive_advantages(self, 
                                       domain: str, 
                                       niche_analysis: Dict, 
                                       authority_score: int, 
                                       technical_score: int) -> List[CompetitiveAdvantage]:
        """Identify competitive advantages of a competitor."""
        
        advantages = []
        
        if authority_score > 80:
            advantages.append(CompetitiveAdvantage.BRAND_AUTHORITY)
        
        if technical_score > 85:
            advantages.append(CompetitiveAdvantage.TECHNICAL_PERFORMANCE)
        
        # Domain-specific advantages
        domain_advantages = {
            'github.com': [CompetitiveAdvantage.NICHE_EXPERTISE, CompetitiveAdvantage.INNOVATION],
            'stackoverflow.com': [CompetitiveAdvantage.CONTENT_DEPTH, CompetitiveAdvantage.NICHE_EXPERTISE],
            'medium.com': [CompetitiveAdvantage.CONTENT_DEPTH, CompetitiveAdvantage.USER_EXPERIENCE]
        }
        
        advantages.extend(domain_advantages.get(domain, []))
        
        return list(set(advantages))  # Remove duplicates
    
    def _determine_market_position(self, authority: int, content_volume: int, niche_relevance: float) -> MarketPosition:
        """Determine market position based on metrics."""
        
        # Calculate composite score
        composite_score = (authority * 0.4) + (min(100, content_volume / 10000) * 0.3) + (niche_relevance * 100 * 0.3)
        
        if composite_score >= 85:
            return MarketPosition.MARKET_LEADER
        elif composite_score >= 70:
            return MarketPosition.CHALLENGER
        elif composite_score >= 50:
            return MarketPosition.FOLLOWER
        elif niche_relevance > 0.8:
            return MarketPosition.NICHE_PLAYER
        else:
            return MarketPosition.NEWCOMER
    
    def _analyze_strengths_weaknesses(self, 
                                    domain: str, 
                                    competitive_advantages: List[CompetitiveAdvantage], 
                                    technical_score: int) -> Tuple[List[str], List[str]]:
        """Analyze strengths and weaknesses of a competitor."""
        
        strengths = []
        weaknesses = []
        
        # Convert competitive advantages to readable strengths
        advantage_map = {
            CompetitiveAdvantage.BRAND_AUTHORITY: "Strong brand recognition and trust",
            CompetitiveAdvantage.CONTENT_DEPTH: "Comprehensive and detailed content",
            CompetitiveAdvantage.TECHNICAL_PERFORMANCE: "Excellent site speed and performance",
            CompetitiveAdvantage.NICHE_EXPERTISE: "Deep expertise in target niche",
            CompetitiveAdvantage.INNOVATION: "Innovation and cutting-edge content",
            CompetitiveAdvantage.USER_EXPERIENCE: "Superior user experience design"
        }
        
        for advantage in competitive_advantages:
            strengths.append(advantage_map.get(advantage, advantage.value))
        
        # Identify potential weaknesses based on missing advantages
        if CompetitiveAdvantage.TECHNICAL_PERFORMANCE not in competitive_advantages:
            weaknesses.append("Potential technical performance issues")
        
        if len(competitive_advantages) < 2:
            weaknesses.append("Limited competitive differentiation")
        
        # Domain-specific analysis
        if 'medium.com' in domain:
            weaknesses.append("High competition for visibility")
        
        return strengths[:5], weaknesses[:3]
    
    # Market analysis methods
    
    def _assess_market_size(self, industry: str, website_type: str) -> str:
        """Assess market size for the industry/type combination."""
        
        market_sizes = {
            ('technology', 'tech_blog'): 'Very Large',
            ('technology', 'tech_portfolio'): 'Large', 
            ('technology', 'saas'): 'Very Large',
            ('healthcare', 'corporate'): 'Large',
            ('finance', 'corporate'): 'Large',
            ('education', 'educational'): 'Very Large'
        }
        
        return market_sizes.get((industry, website_type), 'Medium')
    
    def _assess_competition_level(self, industry: str, website_type: str) -> str:
        """Assess competition level in the market."""
        
        competition_levels = {
            ('technology', 'tech_blog'): 'Very High',
            ('technology', 'tech_portfolio'): 'High',
            ('technology', 'saas'): 'Very High',
            ('healthcare', 'corporate'): 'High',
            ('finance', 'corporate'): 'Very High'
        }
        
        return competition_levels.get((industry, website_type), 'Medium')
    
    def _assess_market_maturity(self, industry: str) -> str:
        """Assess market maturity stage."""
        
        maturity_levels = {
            'technology': 'Rapidly Evolving',
            'healthcare': 'Mature with Innovation',
            'finance': 'Mature',
            'education': 'Transitioning to Digital',
            'ecommerce': 'Mature with Continuous Innovation'
        }
        
        return maturity_levels.get(industry, 'Developing')
    
    # Data loading methods
    
    def _load_industry_benchmarks(self) -> Dict[str, Any]:
        """Load industry benchmark data."""
        return {
            'technology': {
                'avg_page_speed': 2.3,
                'avg_word_count': 1200,
                'avg_bounce_rate': 0.45,
                'mobile_traffic': 0.65
            },
            'healthcare': {
                'avg_page_speed': 3.1,
                'avg_word_count': 800,
                'avg_bounce_rate': 0.55,
                'mobile_traffic': 0.70
            }
        }
    
    def _load_competitive_keywords(self) -> Dict[str, List[str]]:
        """Load competitive keyword databases."""
        return {
            'technology': [
                'software development', 'programming', 'web development',
                'mobile app', 'ai', 'machine learning', 'data science'
            ],
            'healthcare': [
                'medical care', 'health services', 'patient care',
                'medical treatment', 'healthcare provider'
            ]
        }
    
    def _load_market_trends(self) -> Dict[str, List[str]]:
        """Load market trend data."""
        return {
            'technology': [
                'AI and Machine Learning Integration',
                'No-Code/Low-Code Development',
                'Edge Computing Adoption',
                'Cybersecurity Focus',
                'Remote Work Technologies'
            ],
            'healthcare': [
                'Telemedicine Expansion',
                'AI-Powered Diagnostics',
                'Personalized Medicine',
                'Digital Health Records',
                'Preventive Care Focus'
            ]
        }
    
    # Utility methods
    
    def _calculate_percentile(self, value: float, comparison_values: List[float]) -> float:
        """Calculate percentile ranking of a value."""
        if not comparison_values:
            return 50.0
        
        lower_count = sum(1 for v in comparison_values if v < value)
        return (lower_count / len(comparison_values)) * 100
    
    def _create_fallback_competitive_analysis(self) -> CompetitiveAnalysisResult:
        """Create fallback competitive analysis result."""
        
        return CompetitiveAnalysisResult(
            market_overview={'status': 'analysis_unavailable'},
            competitor_profiles=[],
            market_positioning={'current_position': 'follower'},
            competitive_gaps=[],
            strategic_recommendations=[
                {
                    'category': 'general',
                    'priority': 'high',
                    'title': 'Improve Content Quality',
                    'description': 'Focus on creating high-quality, comprehensive content',
                    'expected_impact': 'medium',
                    'timeframe': '1-3 months'
                }
            ],
            keyword_opportunities=['seo optimization', 'content marketing'],
            content_opportunities=['blog content', 'case studies'],
            technical_opportunities=['page speed', 'mobile optimization'],
            market_trends=['digital transformation', 'user experience focus']
        )
    
    # Additional helper methods for gap analysis and recommendations would continue here...
    # (Implementation abbreviated for space - full implementation would include all methods)

# Integration helper function
async def analyze_competitive_intelligence(website_data: Dict[str, Any],
                                         niche_analysis: Dict[str, Any],
                                         content_analysis: Dict[str, Any],
                                         technical_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main function to perform competitive intelligence analysis.
    
    Usage:
    competitive_intel = await analyze_competitive_intelligence(
        website_data, niche_analysis, content_analysis, technical_analysis
    )
    """
    
    intelligence_system = CompetitiveIntelligenceSystem()
    
    try:
        result = await intelligence_system.analyze_competitive_landscape(
            website_data, niche_analysis, content_analysis, technical_analysis
        )
        
        # Convert dataclass to dictionary for JSON serialization
        return {
            'market_overview': result.market_overview,
            'competitor_profiles': [
                {
                    'domain': profile.domain,
                    'estimated_authority': profile.estimated_authority,
                    'content_volume': profile.content_volume,
                    'technical_score': profile.technical_score,
                    'niche_relevance': profile.niche_relevance,
                    'competitive_advantages': [adv.value for adv in profile.competitive_advantages],
                    'market_position': profile.market_position.value,
                    'strengths': profile.strengths,
                    'weaknesses': profile.weaknesses,
                    'opportunity_gaps': profile.opportunity_gaps
                }
                for profile in result.competitor_profiles
            ],
            'market_positioning': result.market_positioning,
            'competitive_gaps': result.competitive_gaps,
            'strategic_recommendations': result.strategic_recommendations,
            'keyword_opportunities': result.keyword_opportunities,
            'content_opportunities': result.content_opportunities,
            'technical_opportunities': result.technical_opportunities,
            'market_trends': result.market_trends,
            'analysis_timestamp': time.time(),
            'analysis_version': '1.0'
        }
        
    except Exception as e:
        logger.error(f"Competitive intelligence analysis failed: {e}")
        return {
            'error': str(e),
            'status': 'analysis_failed',
            'fallback_recommendations': [
                'Conduct manual competitor research',
                'Analyze top-ranking competitors in your niche',
                'Identify content gaps and opportunities',
                'Monitor competitor social media and content strategy'
            ]
        }