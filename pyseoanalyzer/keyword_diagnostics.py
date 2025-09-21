"""
Keyword.com API Integration for Professional SEO Diagnostics.

This module integrates with Keyword.com (SerankTracker) API to provide
professional-grade keyword ranking diagnostics and SERP analysis.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class KeywordRankingData:
    """Represents keyword ranking data from Keyword.com API."""
    keyword_id: str
    keyword: str
    url: str
    current_rank: Optional[int] = None
    previous_rank: Optional[int] = None
    best_rank: Optional[int] = None
    rank_change_day: int = 0
    rank_change_week: int = 0
    rank_change_month: int = 0
    search_volume: Optional[int] = None
    cpc: Optional[float] = None
    competition: Optional[str] = None
    ctr: Optional[float] = None
    clicks: Optional[int] = None
    impressions: Optional[int] = None
    ranking_url: Optional[str] = None
    region: str = "google.com"
    language: str = "en"
    last_updated: Optional[str] = None


@dataclass
class ProjectData:
    """Represents project data from Keyword.com API."""
    project_id: str
    project_name: str
    auth_key: str
    keywords_count: int
    tags_count: int = 0
    last_updated: Optional[str] = None
    tags: List[Dict[str, Any]] = None


class KeywordComAPI:
    """Professional SEO diagnostics via Keyword.com API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Keyword.com API client.
        
        Args:
            api_key: Keyword.com API key, defaults to environment variable
        """
        self.api_key = api_key or os.getenv("KEYWORD_COM_API_KEY")
        if not self.api_key:
            logger.warning("Keyword.com API key not provided. Professional diagnostics will be limited.")
            self.api_key = None
        
        self.base_url = "https://app.keyword.com/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
            "User-Agent": "SEO-AutoPilot/1.0 Professional Diagnostics"
        })
    
    def get_all_projects(self) -> List[ProjectData]:
        """Get all active projects and groups.
        
        Returns:
            List of ProjectData objects representing projects and groups
        """
        if not self.api_key:
            logger.warning("No API key provided for Keyword.com")
            return []
        
        try:
            response = self.session.get(f"{self.base_url}/groups/active", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            projects = []
            for item in data.get("data", []):
                attrs = item.get("attributes", {})
                project = ProjectData(
                    project_id=str(attrs.get("project_id", "")),
                    project_name=attrs.get("name", ""),
                    auth_key=attrs.get("auth", ""),
                    keywords_count=attrs.get("keywords_count", {}).get("ACTIVE", 0),
                    tags_count=attrs.get("tags_count", 0),
                    last_updated=attrs.get("keywords_last_updated_at"),
                    tags=attrs.get("tags", [])
                )
                projects.append(project)
            
            logger.info(f"Retrieved {len(projects)} projects from Keyword.com")
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    def get_project_details(self, project_name: str) -> Optional[ProjectData]:
        """Get details for a specific project.
        
        Args:
            project_name: Name of the project to retrieve
            
        Returns:
            ProjectData object or None if not found
        """
        if not self.api_key:
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/groups/{project_name}", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            attrs = data.get("data", {}).get("attributes", {})
            return ProjectData(
                project_id=str(attrs.get("project_id", "")),
                project_name=attrs.get("name", ""),
                auth_key=attrs.get("auth", ""),
                keywords_count=attrs.get("keywords_count", {}).get("ACTIVE", 0),
                tags_count=attrs.get("tags_count", 0),
                last_updated=attrs.get("keywords_last_updated_at"),
                tags=attrs.get("tags", [])
            )
            
        except Exception as e:
            logger.error(f"Failed to get project details for {project_name}: {e}")
            return None
    
    def analyze_domain_keywords(self, domain: str, max_keywords: int = 50) -> Dict[str, Any]:
        """Analyze keywords for a specific domain across all projects.
        
        Args:
            domain: Domain to analyze (e.g., "example.com")
            max_keywords: Maximum number of keywords to analyze
            
        Returns:
            Comprehensive keyword analysis for the domain
        """
        if not self.api_key:
            return {"error": "No API key provided", "keywords": [], "analysis": {}}
        
        # Get all projects first
        projects = self.get_all_projects()
        
        domain_keywords = []
        total_analyzed = 0
        
        for project in projects[:5]:  # Limit to first 5 projects to avoid API limits
            if total_analyzed >= max_keywords:
                break
                
            # In a real implementation, you would get keywords for each project
            # For now, we'll create a placeholder structure
            project_analysis = {
                "project_name": project.project_name,
                "keywords_count": project.keywords_count,
                "tags_count": project.tags_count,
                "last_updated": project.last_updated
            }
            
            domain_keywords.append(project_analysis)
            total_analyzed += project.keywords_count
        
        # Analyze keyword opportunities
        analysis = self._analyze_keyword_opportunities(domain, domain_keywords)
        
        return {
            "domain": domain,
            "projects_analyzed": len(domain_keywords),
            "total_keywords": total_analyzed,
            "keywords": domain_keywords,
            "analysis": analysis,
            "recommendations": self._generate_keyword_recommendations(analysis)
        }
    
    def create_project_for_domain(self, domain: str, currency: str = "USD") -> Optional[str]:
        """Create a new project for domain analysis.
        
        Args:
            domain: Domain to create project for
            currency: Reporting currency (default: USD)
            
        Returns:
            Project ID if successful, None otherwise
        """
        if not self.api_key:
            logger.warning("Cannot create project without API key")
            return None
        
        project_name = domain.replace("https://", "").replace("http://", "").replace("www.", "")
        
        payload = {
            "data": {
                "type": "project",
                "attributes": {
                    "category": project_name,
                    "currency_code": currency
                }
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/groups", json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            project_id = data.get("data", {}).get("attributes", {}).get("project_id")
            logger.info(f"Created project {project_name} with ID: {project_id}")
            return str(project_id) if project_id else None
            
        except Exception as e:
            logger.error(f"Failed to create project for {domain}: {e}")
            return None
    
    def add_keywords_to_project(
        self, 
        project_name: str, 
        keywords: List[str], 
        domain: str,
        region: str = "google.com",
        language: str = "en"
    ) -> Dict[str, Any]:
        """Add keywords to a project for tracking.
        
        Args:
            project_name: Name of the project
            keywords: List of keywords to add
            domain: Domain to track rankings for
            region: Google region for tracking
            language: Language for tracking
            
        Returns:
            Results of keyword addition
        """
        if not self.api_key or not keywords:
            return {"error": "No API key or keywords provided", "added": 0}
        
        # Prepare keywords for bulk addition
        keyword_data = []
        for keyword in keywords[:20]:  # Limit to 20 keywords per request
            keyword_data.append({
                "type": "keyword",
                "attributes": {
                    "category": project_name,
                    "ignore_local": True,
                    "near": "",
                    "source": 1,  # API source
                    "gmb": "",
                    "url": domain,
                    "region": region,
                    "language": language,
                    "tags": [],
                    "type": "se",  # Desktop search
                    "url_tracking_method": "broad",
                    "ignore_sub_domains": False,
                    "kw": keyword
                }
            })
        
        payload = {"data": keyword_data}
        
        try:
            response = self.session.post(
                f"{self.base_url}/groups/{project_name}/keywords", 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            added_count = data.get("meta", {}).get("counts", {}).get("added", 0)
            duplicates = data.get("meta", {}).get("counts", {}).get("duplicates", 0)
            
            logger.info(f"Added {added_count} keywords to {project_name}, {duplicates} duplicates")
            
            return {
                "project_name": project_name,
                "keywords_requested": len(keywords),
                "keywords_added": added_count,
                "duplicates": duplicates,
                "keywords_data": data.get("data", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to add keywords to {project_name}: {e}")
            return {"error": str(e), "added": 0}
    
    def refresh_keywords(self, project_ids: List[str]) -> Dict[str, Any]:
        """Trigger on-demand refresh of keywords.
        
        Args:
            project_ids: List of project IDs to refresh
            
        Returns:
            Refresh status and remaining quota
        """
        if not self.api_key or not project_ids:
            return {"error": "No API key or project IDs provided"}
        
        payload = {
            "data": {
                "project_ids": project_ids,
                "include_sub_groups": True
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/keywords/refresh", json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            message = data.get("message", "")
            logger.info(f"Keyword refresh triggered: {message}")
            
            return {
                "status": "success",
                "message": message,
                "projects_refreshed": len(project_ids)
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh keywords: {e}")
            return {"error": str(e)}
    
    def _analyze_keyword_opportunities(self, domain: str, keywords_data: List[Dict]) -> Dict[str, Any]:
        """Analyze keyword opportunities based on existing data."""
        
        total_keywords = sum(kw.get("keywords_count", 0) for kw in keywords_data)
        
        analysis = {
            "keyword_coverage": {
                "total_tracked": total_keywords,
                "projects_with_keywords": len([kw for kw in keywords_data if kw.get("keywords_count", 0) > 0]),
                "average_per_project": total_keywords / max(len(keywords_data), 1)
            },
            "opportunity_score": self._calculate_opportunity_score(keywords_data),
            "tracking_health": self._assess_tracking_health(keywords_data),
            "expansion_potential": self._assess_expansion_potential(domain, keywords_data)
        }
        
        return analysis
    
    def _calculate_opportunity_score(self, keywords_data: List[Dict]) -> float:
        """Calculate opportunity score based on keyword data."""
        if not keywords_data:
            return 0.0
        
        # Basic scoring based on keyword count and recency
        score = 0.0
        for kw in keywords_data:
            keyword_count = kw.get("keywords_count", 0)
            if keyword_count > 0:
                score += min(keyword_count / 100, 0.3)  # Up to 0.3 for keyword count
                
                # Bonus for recent updates
                last_updated = kw.get("last_updated")
                if last_updated:
                    try:
                        updated_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        days_ago = (datetime.now() - updated_date.replace(tzinfo=None)).days
                        if days_ago <= 7:
                            score += 0.2  # Recent update bonus
                        elif days_ago <= 30:
                            score += 0.1  # Somewhat recent bonus
                    except:
                        pass
        
        return min(score, 1.0)
    
    def _assess_tracking_health(self, keywords_data: List[Dict]) -> Dict[str, Any]:
        """Assess the health of keyword tracking."""
        if not keywords_data:
            return {"status": "no_data", "issues": ["No tracking data available"]}
        
        total_projects = len(keywords_data)
        active_projects = len([kw for kw in keywords_data if kw.get("keywords_count", 0) > 0])
        
        health_score = active_projects / total_projects if total_projects > 0 else 0
        
        issues = []
        if health_score < 0.5:
            issues.append("Low keyword tracking coverage")
        if total_projects == 0:
            issues.append("No projects found for tracking")
        
        # Check for stale data
        stale_projects = 0
        for kw in keywords_data:
            last_updated = kw.get("last_updated")
            if last_updated:
                try:
                    updated_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - updated_date.replace(tzinfo=None)).days
                    if days_ago > 30:
                        stale_projects += 1
                except:
                    stale_projects += 1
        
        if stale_projects > 0:
            issues.append(f"{stale_projects} projects have stale data (>30 days)")
        
        status = "healthy" if health_score > 0.7 and not issues else "needs_attention"
        
        return {
            "status": status,
            "health_score": health_score,
            "active_projects": active_projects,
            "total_projects": total_projects,
            "issues": issues
        }
    
    def _assess_expansion_potential(self, domain: str, keywords_data: List[Dict]) -> Dict[str, Any]:
        """Assess potential for keyword tracking expansion."""
        
        total_keywords = sum(kw.get("keywords_count", 0) for kw in keywords_data)
        
        # Basic expansion recommendations
        recommendations = []
        
        if total_keywords < 50:
            recommendations.append("Consider adding more core keywords for comprehensive tracking")
        elif total_keywords < 200:
            recommendations.append("Good keyword base - consider expanding to long-tail variations")
        else:
            recommendations.append("Comprehensive keyword tracking - focus on optimization")
        
        # Check for tag usage
        total_tags = sum(kw.get("tags_count", 0) for kw in keywords_data)
        if total_tags == 0:
            recommendations.append("Add tags to organize keywords by topic or intent")
        
        expansion_score = min(total_keywords / 200, 1.0)  # 200 keywords = full score
        
        return {
            "expansion_score": expansion_score,
            "current_keyword_count": total_keywords,
            "recommended_target": max(200, total_keywords * 1.5),
            "recommendations": recommendations
        }
    
    def _generate_keyword_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable keyword recommendations."""
        
        recommendations = []
        
        # Coverage recommendations
        coverage = analysis.get("keyword_coverage", {})
        total_tracked = coverage.get("total_tracked", 0)
        
        if total_tracked < 50:
            recommendations.append({
                "priority": "high",
                "category": "keyword_expansion",
                "title": "Expand keyword tracking coverage",
                "description": f"Currently tracking {total_tracked} keywords. Increase to at least 50 core keywords.",
                "action": "Add more primary and secondary keywords related to your business"
            })
        
        # Health recommendations
        health = analysis.get("tracking_health", {})
        if health.get("status") == "needs_attention":
            for issue in health.get("issues", []):
                recommendations.append({
                    "priority": "medium",
                    "category": "tracking_health",
                    "title": "Fix tracking health issue",
                    "description": issue,
                    "action": "Review and update keyword tracking configuration"
                })
        
        # Expansion recommendations
        expansion = analysis.get("expansion_potential", {})
        for rec in expansion.get("recommendations", []):
            recommendations.append({
                "priority": "low",
                "category": "expansion",
                "title": "Keyword expansion opportunity",
                "description": rec,
                "action": "Implement suggested expansion strategy"
            })
        
        return recommendations


def example_usage():
    """Example of using the Keyword.com API integration."""
    
    # Initialize with API key
    keyword_api = KeywordComAPI()
    
    # Get all projects
    projects = keyword_api.get_all_projects()
    print(f"Found {len(projects)} projects")
    
    # Analyze domain keywords
    domain_analysis = keyword_api.analyze_domain_keywords("example.com")
    print(f"Domain analysis completed: {domain_analysis.get('total_keywords', 0)} keywords analyzed")
    
    # Print recommendations
    recommendations = domain_analysis.get("recommendations", [])
    print(f"Generated {len(recommendations)} recommendations")
    for rec in recommendations[:3]:  # Show first 3
        print(f"- {rec.get('title')}: {rec.get('description')}")


if __name__ == "__main__":
    example_usage()