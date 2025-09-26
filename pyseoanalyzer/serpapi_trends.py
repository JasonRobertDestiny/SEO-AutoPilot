"""
SerpAPI Google Trends Integration for SEO Analysis.

This module integrates Google Trends data via SerpAPI to provide
keyword trend analysis and content strategy insights.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    """Represents Google Trends data for a keyword."""
    keyword: str
    region: str = "US"
    timeframe: str = "today 12-m"
    interest_over_time: List[Dict[str, Any]] = None
    related_topics: List[Dict[str, Any]] = None
    related_queries: List[Dict[str, Any]] = None
    rising_queries: List[Dict[str, Any]] = None
    average_interest: float = 0.0
    trend_direction: str = "stable"  # rising, falling, stable
    peak_periods: List[Dict[str, Any]] = None


class SerpAPITrends:
    """Google Trends integration via SerpAPI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize SerpAPI Trends client.
        
        Args:
            api_key: SerpAPI key, defaults to environment variable
        """
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERPAPI_KEY environment variable.")
        
        self.base_url = "https://serpapi.com/search"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SEO-AutoPilot/1.0 Trends Analyzer"
        })
    
    def get_keyword_trends(
        self, 
        keywords: List[str], 
        region: str = "US",
        timeframe: str = "today 12-m"
    ) -> Dict[str, TrendData]:
        """Get Google Trends data for multiple keywords.
        
        Args:
            keywords: List of keywords to analyze
            region: Geographic region (US, GB, DE, etc.)
            timeframe: Time period (today 12-m, today 5-y, etc.)
            
        Returns:
            Dictionary mapping keywords to TrendData objects
        """
        trends_data = {}
        
        for keyword in keywords:
            try:
                trend_data = self._fetch_single_keyword_trend(keyword, region, timeframe)
                trends_data[keyword] = trend_data
                logger.info(f"Retrieved trends data for keyword: {keyword}")
            except Exception as e:
                logger.warning(f"Failed to get trends for {keyword}: {e}")
                # Create empty trend data for failed requests
                trends_data[keyword] = TrendData(
                    keyword=keyword,
                    region=region,
                    timeframe=timeframe,
                    interest_over_time=[],
                    related_topics=[],
                    related_queries=[],
                    rising_queries=[]
                )
        
        return trends_data
    
    def _fetch_single_keyword_trend(
        self, 
        keyword: str, 
        region: str, 
        timeframe: str
    ) -> TrendData:
        """Fetch trends data for a single keyword."""
        
        params = {
            "engine": "google_trends",
            "q": keyword,
            "geo": region,
            "date": timeframe,
            "api_key": self.api_key
        }
        
        try:
            # Debug log the actual URL being requested
            logger.debug(f"🌐 Making SerpAPI request with params: {params}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            logger.debug(f"🌐 Full URL: {response.url}")
            response.raise_for_status()
            data = response.json()
            
            # Parse the response and create TrendData
            return self._parse_trends_response(data, keyword, region, timeframe)
            
        except requests.RequestException as e:
            logger.error(f"API request failed for {keyword}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {keyword}: {e}")
            raise
    
    def _parse_trends_response(
        self, 
        data: Dict[str, Any], 
        keyword: str, 
        region: str, 
        timeframe: str
    ) -> TrendData:
        """Parse SerpAPI response into TrendData object."""
        
        # Extract interest over time data
        interest_over_time = data.get("interest_over_time", {}).get("timeline_data", [])
        
        # Extract related topics
        related_topics = []
        if "related_topics" in data:
            topics_data = data["related_topics"]
            if "top" in topics_data:
                related_topics.extend(topics_data["top"])
            if "rising" in topics_data:
                related_topics.extend(topics_data["rising"])
        
        # Extract related queries
        related_queries = []
        rising_queries = []
        if "related_queries" in data:
            queries_data = data["related_queries"]
            if "top" in queries_data:
                related_queries = queries_data["top"]
            if "rising" in queries_data:
                rising_queries = queries_data["rising"]
        
        # Calculate average interest and trend direction
        average_interest = 0.0
        trend_direction = "stable"
        peak_periods = []
        
        if interest_over_time:
            values = [item.get("value", 0) for item in interest_over_time if item.get("value") is not None]
            if values:
                average_interest = sum(values) / len(values)
                
                # Determine trend direction
                if len(values) >= 2:
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)
                    
                    if second_avg > first_avg * 1.1:
                        trend_direction = "rising"
                    elif second_avg < first_avg * 0.9:
                        trend_direction = "falling"
                
                # Find peak periods (values > 80% of max)
                max_value = max(values)
                if max_value > 0:
                    threshold = max_value * 0.8
                    for i, item in enumerate(interest_over_time):
                        if item.get("value", 0) >= threshold:
                            peak_periods.append({
                                "date": item.get("date"),
                                "value": item.get("value"),
                                "index": i
                            })
        
        return TrendData(
            keyword=keyword,
            region=region,
            timeframe=timeframe,
            interest_over_time=interest_over_time,
            related_topics=related_topics,
            related_queries=related_queries,
            rising_queries=rising_queries,
            average_interest=average_interest,
            trend_direction=trend_direction,
            peak_periods=peak_periods
        )
    
    def get_trending_keywords(
        self, 
        category: Optional[str] = None,
        region: str = "US"
    ) -> List[Dict[str, Any]]:
        """Get currently trending keywords/topics.
        
        Args:
            category: Specific category to focus on
            region: Geographic region
            
        Returns:
            List of trending keywords with metadata
        """
        # Try different approaches for getting trending data
        trending_approaches = [
            # Approach 1: Use realtime trends
            {
                "engine": "google_trends",
                "data_type": "REALTIME",
                "geo": region,
                "api_key": self.api_key
            },
            # Approach 2: Use trending searches (older format)
            {
                "engine": "google_trends_trending_now", 
                "geo": region,
                "api_key": self.api_key
            },
            # Approach 3: Fallback to popular searches
            {
                "engine": "google_trends",
                "data_type": "POPULAR",
                "geo": region, 
                "api_key": self.api_key
            }
        ]
        
        for i, params in enumerate(trending_approaches):
            try:
                if category:
                    params["cat"] = category
                
                logger.info(f"🔍 Trying trending approach {i+1}: {params.get('data_type', params.get('engine'))}")
                logger.debug(f"🌐 Full params for trending: {params}")
                response = self.session.get(self.base_url, params=params, timeout=15)
                logger.debug(f"🌐 Full trending URL: {response.url}")
                response.raise_for_status()
                data = response.json()
                
                # Try different response structures
                trending_searches = (
                    data.get("trending_searches", []) or
                    data.get("realtime_trends", []) or
                    data.get("popular_searches", []) or
                    data.get("results", [])
                )
                
                if trending_searches:
                    logger.info(f"✅ Successfully got {len(trending_searches)} trending keywords")
                    return trending_searches[:10]  # Limit to top 10
                    
            except Exception as e:
                logger.warning(f"⚠️ Trending approach {i+1} failed: {e}")
                continue
        
        # If all approaches fail, return empty list
        logger.warning("⚠️ All trending approaches failed, returning empty list")
        return []
    
    def analyze_content_opportunities(
        self, 
        primary_keywords: List[str],
        region: str = "US"
    ) -> Dict[str, Any]:
        """Analyze trends data to identify content opportunities.
        
        Args:
            primary_keywords: Main keywords from website analysis
            region: Geographic region for trends
            
        Returns:
            Content opportunity analysis with recommendations
        """
        trends_data = self.get_keyword_trends(primary_keywords, region)
        trending_keywords = self.get_trending_keywords(region=region)
        
        opportunities = {
            "keyword_analysis": {},
            "content_suggestions": [],
            "seasonal_insights": [],
            "trending_opportunities": [],
            "optimization_priorities": []
        }
        
        # Analyze each keyword's trend data
        for keyword, trend_data in trends_data.items():
            analysis = {
                "keyword": keyword,
                "average_interest": trend_data.average_interest,
                "trend_direction": trend_data.trend_direction,
                "peak_periods": len(trend_data.peak_periods),
                "related_topics_count": len(trend_data.related_topics),
                "rising_queries_count": len(trend_data.rising_queries),
                "content_potential": self._calculate_content_potential(trend_data)
            }
            
            opportunities["keyword_analysis"][keyword] = analysis
            
            # Generate content suggestions based on related queries
            if trend_data.rising_queries:
                for query in trend_data.rising_queries[:3]:  # Top 3 rising queries
                    opportunities["content_suggestions"].append({
                        "base_keyword": keyword,
                        "suggested_topic": query.get("query", ""),
                        "search_value": query.get("value", 0),
                        "reason": f"Rising query related to {keyword}"
                    })
            
            # Identify seasonal patterns
            if trend_data.peak_periods:
                opportunities["seasonal_insights"].append({
                    "keyword": keyword,
                    "peak_count": len(trend_data.peak_periods),
                    "peak_periods": trend_data.peak_periods,
                    "recommendation": self._generate_seasonal_recommendation(trend_data)
                })
        
        # Find trending opportunities
        for trend in trending_keywords[:5]:  # Top 5 trending
            title = trend.get("title", "")
            opportunities["trending_opportunities"].append({
                "trending_topic": title,
                "relevance_score": self._calculate_relevance_score(title, primary_keywords),
                "suggestion": f"Consider creating content around: {title}"
            })
        
        # Generate optimization priorities
        priorities = []
        for keyword, analysis in opportunities["keyword_analysis"].items():
            priority_score = (
                analysis["content_potential"] * 0.4 +
                (1.0 if analysis["trend_direction"] == "rising" else 0.5) * 0.3 +
                min(analysis["rising_queries_count"] / 10, 1.0) * 0.3
            )
            
            priorities.append({
                "keyword": keyword,
                "priority_score": priority_score,
                "action": self._recommend_action(analysis)
            })
        
        # Sort by priority score
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        opportunities["optimization_priorities"] = priorities[:10]  # Top 10
        
        return opportunities
    
    def _calculate_content_potential(self, trend_data: TrendData) -> float:
        """Calculate content potential score (0-1) based on trends data."""
        score = 0.0
        
        # Base score from average interest
        if trend_data.average_interest > 0:
            score += min(trend_data.average_interest / 100, 0.4)
        
        # Bonus for rising trend
        if trend_data.trend_direction == "rising":
            score += 0.3
        elif trend_data.trend_direction == "stable":
            score += 0.1
        
        # Bonus for related content opportunities
        related_bonus = min(len(trend_data.related_queries) / 20, 0.2)
        score += related_bonus
        
        # Rising queries bonus
        rising_bonus = min(len(trend_data.rising_queries) / 10, 0.1)
        score += rising_bonus
        
        return min(score, 1.0)
    
    def _generate_seasonal_recommendation(self, trend_data: TrendData) -> str:
        """Generate seasonal content recommendation."""
        peak_count = len(trend_data.peak_periods)
        
        if peak_count >= 3:
            return f"Strong seasonal pattern detected. Plan content calendar around peak periods."
        elif peak_count >= 1:
            return f"Some seasonal variation detected. Consider timing content for peak periods."
        else:
            return f"Consistent interest throughout the period. Suitable for evergreen content."
    
    def _calculate_relevance_score(self, trending_topic: str, primary_keywords: List[str]) -> float:
        """Calculate how relevant a trending topic is to primary keywords."""
        trending_words = set(trending_topic.lower().split())
        primary_words = set(" ".join(primary_keywords).lower().split())
        
        if not trending_words or not primary_words:
            return 0.0
        
        intersection = trending_words & primary_words
        union = trending_words | primary_words
        
        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0
    
    def _recommend_action(self, analysis: Dict[str, Any]) -> str:
        """Recommend action based on keyword analysis."""
        keyword = analysis["keyword"]
        trend = analysis["trend_direction"]
        potential = analysis["content_potential"]
        
        if trend == "rising" and potential > 0.7:
            return f"High priority: Create comprehensive content for '{keyword}' to capture rising interest"
        elif trend == "rising" and potential > 0.4:
            return f"Medium priority: Optimize existing content for '{keyword}' or create targeted pieces"
        elif trend == "stable" and potential > 0.6:
            return f"Evergreen opportunity: Develop authoritative content for '{keyword}'"
        elif trend == "falling":
            return f"Low priority: Monitor '{keyword}' for potential comeback or pivot to related terms"
        else:
            return f"Research needed: Investigate '{keyword}' further before content investment"


def example_usage():
    """Example of using the SerpAPI Trends integration."""
    
    # Initialize with API key
    trends_analyzer = SerpAPITrends()
    
    # Example keywords from website analysis
    keywords = ["python seo", "seo tools", "keyword research"]
    
    # Get trends data
    trends_data = trends_analyzer.get_keyword_trends(keywords)
    
    # Print results
    for keyword, data in trends_data.items():
        print(f"\nKeyword: {keyword}")
        print(f"Average Interest: {data.average_interest:.1f}")
        print(f"Trend Direction: {data.trend_direction}")
        print(f"Related Queries: {len(data.related_queries)}")
        print(f"Rising Queries: {len(data.rising_queries)}")
    
    # Get content opportunities
    opportunities = trends_analyzer.analyze_content_opportunities(keywords)
    print(f"\nContent Opportunities Found: {len(opportunities['content_suggestions'])}")
    print(f"Optimization Priorities: {len(opportunities['optimization_priorities'])}")


if __name__ == "__main__":
    example_usage()