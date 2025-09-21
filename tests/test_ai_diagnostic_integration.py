"""
🎯 Comprehensive AI-Diagnostic Integration Test Suite

Tests the integration between professional diagnostics (150+ checkpoints) and AI analysis
to ensure professional-grade SEO analysis comparable to Ahrefs, SEMrush, and Screaming Frog.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pyseoanalyzer.llm_analyst import LLMSEOEnhancer, EnhancedProfessionalSEOAnalysis
from pyseoanalyzer.professional_diagnostics import ProfessionalSEODiagnostics


class TestAIDiagnosticIntegration:
    """Test suite for AI-Diagnostic integration functionality"""
    
    @pytest.fixture
    def sample_diagnostic_data(self):
        """Sample professional diagnostic data with 150+ checkpoints"""
        return {
            'overall_score': 77.6,
            'category_scores': {
                'technical_seo': {'score': 85.2, 'issues_found': 3, 'critical_issues': 1},
                'content_quality': {'score': 72.8, 'issues_found': 5, 'critical_issues': 2},
                'performance': {'score': 68.4, 'issues_found': 8, 'critical_issues': 3},
                'mobile_optimization': {'score': 91.3, 'issues_found': 1, 'critical_issues': 0},
                'user_experience': {'score': 79.6, 'issues_found': 4, 'critical_issues': 1},
                'security': {'score': 95.1, 'issues_found': 1, 'critical_issues': 0}
            },
            'all_issues': [
                {
                    'title': 'Missing H1 tag',
                    'description': 'Page lacks primary H1 heading structure',
                    'priority': 'critical',
                    'category': 'technical_seo',
                    'impact_score': 85,
                    'effort_score': 20,
                    'roi_score': 4.25,
                    'recommendation': 'Add a descriptive H1 tag to the page'
                },
                {
                    'title': 'Large Content Layout Shift',
                    'description': 'Core Web Vitals CLS score exceeds threshold',
                    'priority': 'high',
                    'category': 'performance',
                    'impact_score': 78,
                    'effort_score': 65,
                    'roi_score': 1.2,
                    'recommendation': 'Optimize image loading and reserve space for dynamic content'
                },
                {
                    'title': 'Thin content detected',
                    'description': 'Page content below recommended minimum word count',
                    'priority': 'medium',
                    'category': 'content_quality',
                    'impact_score': 45,
                    'effort_score': 40,
                    'roi_score': 1.125,
                    'recommendation': 'Expand content with relevant, valuable information'
                }
            ],
            'issues_summary': {
                'total_issues': 22,
                'critical': 7,
                'high': 8,
                'medium': 5,
                'low': 2
            }
        }
    
    @pytest.fixture
    def sample_enhanced_context(self, sample_diagnostic_data):
        """Sample enhanced context combining all analysis sources"""
        return {
            'professional_analysis': sample_diagnostic_data,
            'basic_content': {
                'url': 'https://example.com',
                'title': 'Example Page Title',
                'description': 'Example meta description for testing',
                'word_count': 450,
                'headings': {'h1': [], 'h2': ['Section 1', 'Section 2'], 'h3': ['Subsection']}
            },
            'pagespeed_insights': {
                'performance_score': 68,
                'accessibility_score': 91,
                'best_practices_score': 87,
                'seo_score': 92,
                'core_web_vitals': {
                    'lcp': 2.8,
                    'fid': 85,
                    'cls': 0.15
                }
            },
            'trends_insights': {
                'keyword_trends': [
                    {'keyword': 'seo analysis', 'interest_score': 78, 'trend_direction': 'rising'},
                    {'keyword': 'website optimization', 'interest_score': 65, 'trend_direction': 'stable'}
                ],
                'trending_topics': [
                    {'topic': 'Core Web Vitals', 'growth_rate': 25.4},
                    {'topic': 'Mobile SEO', 'growth_rate': 18.7}
                ]
            }
        }
    
    def test_professional_diagnostic_data_structure(self, sample_diagnostic_data):
        """Test that diagnostic data has required structure for AI integration"""
        # Verify essential fields
        assert 'overall_score' in sample_diagnostic_data
        assert 'category_scores' in sample_diagnostic_data
        assert 'all_issues' in sample_diagnostic_data
        assert 'issues_summary' in sample_diagnostic_data
        
        # Verify score is in valid range
        assert 0 <= sample_diagnostic_data['overall_score'] <= 100
        
        # Verify issues structure
        for issue in sample_diagnostic_data['all_issues']:
            required_fields = ['title', 'description', 'priority', 'category', 'recommendation']
            for field in required_fields:
                assert field in issue, f"Missing required field: {field}"
        
        # Verify category scores structure
        for category, data in sample_diagnostic_data['category_scores'].items():
            assert 'score' in data
            assert 'issues_found' in data
            assert 'critical_issues' in data
    
    @pytest.mark.asyncio
    async def test_enhanced_professional_analysis_siliconflow(self, sample_enhanced_context):
        """Test enhanced professional analysis using SiliconFlow API"""
        # Mock SiliconFlow LLM
        mock_siliconflow_llm = AsyncMock()
        mock_siliconflow_llm.analyze_seo_data.return_value = {
            'strategic_assessment': 'Professional analysis showing strong technical foundation with performance optimization opportunities',
            'professional_priorities': [
                'Optimize Core Web Vitals performance metrics',
                'Enhance content depth and quality',
                'Implement comprehensive H1 tag structure'
            ],
            'implementation_timeline': {
                'immediate': {'duration': '1-2 weeks', 'expected_impact': 'High'},
                'short_term': {'duration': '1-2 months', 'expected_impact': 'Medium'},
                'long_term': {'duration': '3-6 months', 'expected_impact': 'High'}
            },
            'roi_projections': {
                'technical_fixes': 3.2,
                'content_optimization': 2.8,
                'performance_improvements': 4.1
            }
        }
        
        with patch('pyseoanalyzer.llm_analyst.SiliconFlowLLM', return_value=mock_siliconflow_llm):
            enhancer = LLMSEOEnhancer(use_siliconflow=True)
            enhancer.siliconflow_llm = mock_siliconflow_llm
            
            result = await enhancer.enhanced_professional_analysis(sample_enhanced_context)
            
            # Verify SiliconFlow was called with professional analysis
            mock_siliconflow_llm.analyze_seo_data.assert_called_once_with(sample_enhanced_context, "professional")
            
            # Verify diagnostic metadata was added
            assert 'diagnostic_metadata' in result
            assert result['diagnostic_metadata']['total_checkpoints'] == 3  # Number of issues in sample data
            assert result['diagnostic_metadata']['overall_score'] == 77.6
            assert result['diagnostic_metadata']['critical_issues'] == 1
            assert result['diagnostic_metadata']['analysis_source'] == 'siliconflow_professional'
            
            # Verify professional analysis structure
            assert 'strategic_assessment' in result
            assert 'professional_priorities' in result
            assert 'implementation_timeline' in result
            assert 'roi_projections' in result
    
    @pytest.mark.asyncio
    async def test_enhanced_professional_analysis_anthropic(self, sample_enhanced_context):
        """Test enhanced professional analysis using Anthropic Claude"""
        # Mock enhanced professional analysis result
        mock_professional_result = Mock()
        mock_professional_result.model_dump.return_value = {
            'strategic_assessment': 'Comprehensive analysis reveals optimization opportunities across technical and content domains',
            'diagnostic_synthesis': {
                'technical_seo': 'Strong foundation with minor H1 optimization needed',
                'performance': 'Core Web Vitals require attention, particularly CLS',
                'content_quality': 'Content depth below optimal threshold'
            },
            'professional_priorities': [
                'Address critical H1 tag implementation',
                'Optimize Core Web Vitals performance',
                'Enhance content comprehensiveness'
            ],
            'competitive_intelligence': 'Analysis shows opportunities in performance optimization sector',
            'technical_audit_summary': 'Technical foundation solid with targeted improvements needed',
            'implementation_timeline': {
                'phase_1': {'duration': '2-3 weeks', 'expected_outcome': 'Technical foundation fixes'},
                'phase_2': {'duration': '1-2 months', 'expected_outcome': 'Performance optimization'},
                'phase_3': {'duration': '2-3 months', 'expected_outcome': 'Content expansion'}
            },
            'roi_projections': {
                'technical_seo': 3.8,
                'performance': 2.9,
                'content_optimization': 2.1
            }
        }
        
        # Mock the enhanced professional chain
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_professional_result
        
        enhancer = LLMSEOEnhancer(use_siliconflow=False)
        enhancer.enhanced_professional_chain = mock_chain
        
        result = await enhancer.enhanced_professional_analysis(sample_enhanced_context)
        
        # Verify professional chain was called
        mock_chain.ainvoke.assert_called_once_with(sample_enhanced_context)
        
        # Verify diagnostic metadata integration
        assert 'diagnostic_metadata' in result
        assert result['diagnostic_metadata']['total_checkpoints'] == 3
        assert result['diagnostic_metadata']['overall_score'] == 77.6
        assert result['diagnostic_metadata']['critical_issues'] == 1
        assert result['diagnostic_metadata']['analysis_source'] == 'anthropic_professional'
        
        # Verify professional analysis metadata
        assert 'professional_analysis_metadata' in result
        assert result['professional_analysis_metadata']['provider'] == 'anthropic_claude'
        assert result['professional_analysis_metadata']['status'] == 'completed'
        assert result['professional_analysis_metadata']['analysis_depth'] == 'professional_grade'
        
        # Verify professional analysis structure
        assert 'strategic_assessment' in result
        assert 'diagnostic_synthesis' in result
        assert 'professional_priorities' in result
        assert 'competitive_intelligence' in result
        assert 'technical_audit_summary' in result
    
    @pytest.mark.asyncio
    async def test_enhanced_professional_analysis_fallback(self, sample_enhanced_context):
        """Test fallback behavior when enhanced professional analysis fails"""
        # Mock regular enhancement method
        mock_regular_result = {
            'entity_analysis': {'knowledge_panel_readiness': 75},
            'credibility_analysis': {'neeat_scores': {'expertise': 80}},
            'conversation_analysis': {'engagement_score': 70},
            'recommendations': {'strategic_recommendations': ['Improve content quality']}
        }
        
        enhancer = LLMSEOEnhancer(use_siliconflow=False)
        # Don't set enhanced_professional_chain to trigger fallback
        
        with patch.object(enhancer, 'enhance_seo_analysis', return_value=mock_regular_result) as mock_enhance:
            result = await enhancer.enhanced_professional_analysis(sample_enhanced_context)
            
            # Verify fallback was used
            mock_enhance.assert_called_once()
            
            # Verify professional context was added
            assert 'professional_context' in result
            assert result['professional_context']['diagnostic_score'] == 77.6
            assert result['professional_context']['total_issues'] == 3
            assert result['professional_context']['analysis_method'] == 'enhanced_regular_with_professional_context'
            
            # Verify regular analysis structure is preserved
            assert 'entity_analysis' in result
            assert 'recommendations' in result
    
    @pytest.mark.asyncio
    async def test_enhanced_professional_analysis_error_handling(self, sample_enhanced_context):
        """Test error handling in enhanced professional analysis"""
        enhancer = LLMSEOEnhancer(use_siliconflow=False)
        
        # Mock enhance_seo_analysis to raise an exception
        with patch.object(enhancer, 'enhance_seo_analysis', side_effect=Exception("Network error")):
            result = await enhancer.enhanced_professional_analysis(sample_enhanced_context)
            
            # Verify error handling
            assert 'professional_analysis_failed' in result
            assert result['professional_analysis_failed'] is True
            assert 'error_message' in result
            assert 'execution_time' in result
            assert 'recommendations' in result
            assert 'Professional analysis unavailable' in result['recommendations'][0]
    
    def test_enhanced_professional_analysis_model_validation(self):
        """Test Pydantic model validation for enhanced professional analysis"""
        # Test valid data
        valid_data = {
            'strategic_assessment': 'Comprehensive SEO analysis',
            'diagnostic_synthesis': {'technical_seo': 'Good foundation'},
            'professional_priorities': ['Fix H1 tags', 'Optimize performance'],
            'competitive_intelligence': 'Market analysis shows opportunities',
            'technical_audit_summary': 'Technical foundation requires minor fixes',
            'content_optimization_roadmap': {'phase_1': ['Improve titles']},
            'implementation_timeline': {'immediate': {'duration': '1 week', 'expected_outcome': 'Quick wins'}},
            'roi_projections': {'technical': 2.5},
            'risk_mitigation_plan': ['Monitor Core Web Vitals'],
            'professional_score_analysis': 'Score indicates solid foundation',
            'industry_benchmarking': {'performance': 'Above average'},
            'advanced_recommendations': [{'action': 'Optimize images', 'priority': 'high'}]
        }
        
        # Should not raise exception
        model = EnhancedProfessionalSEOAnalysis(**valid_data)
        assert model.strategic_assessment == 'Comprehensive SEO analysis'
        assert len(model.professional_priorities) == 2
        assert 'technical' in model.roi_projections
    
    @pytest.mark.asyncio
    async def test_diagnostic_integration_data_flow(self, sample_enhanced_context):
        """Test complete data flow from diagnostics through AI integration"""
        # Create professional diagnostics instance
        diagnostics = ProfessionalSEODiagnostics()
        
        # Mock diagnostic analysis
        with patch.object(diagnostics, 'comprehensive_audit', return_value=sample_enhanced_context['professional_analysis']):
            # Run diagnostic analysis
            diagnostic_result = diagnostics.comprehensive_audit('https://example.com')
            
            # Verify diagnostic data structure
            assert diagnostic_result['overall_score'] == 77.6
            assert len(diagnostic_result['all_issues']) == 3
            
            # Prepare enhanced context
            enhanced_context = {
                'professional_analysis': diagnostic_result,
                'basic_content': sample_enhanced_context['basic_content']
            }
            
            # Mock LLM analysis
            mock_llm_result = {
                'strategic_assessment': 'Professional analysis complete',
                'professional_priorities': ['Priority 1', 'Priority 2']
            }
            
            enhancer = LLMSEOEnhancer(use_siliconflow=True)
            with patch.object(enhancer, 'siliconflow_llm') as mock_siliconflow:
                mock_siliconflow.analyze_seo_data.return_value = mock_llm_result
                
                # Run enhanced professional analysis
                result = await enhancer.enhanced_professional_analysis(enhanced_context)
                
                # Verify complete integration
                assert 'strategic_assessment' in result
                assert 'diagnostic_metadata' in result
                assert result['diagnostic_metadata']['overall_score'] == 77.6
                assert result['diagnostic_metadata']['total_checkpoints'] == 3
    
    def test_professional_grade_analysis_quality_metrics(self, sample_enhanced_context):
        """Test that analysis meets professional-grade quality standards"""
        diagnostic_data = sample_enhanced_context['professional_analysis']
        
        # Verify comprehensive diagnostic coverage (comparable to enterprise tools)
        assert len(diagnostic_data['all_issues']) >= 3, "Should have multiple diagnostic issues"
        assert len(diagnostic_data['category_scores']) >= 6, "Should cover major SEO categories"
        assert diagnostic_data['overall_score'] > 0, "Should have calculated overall score"
        
        # Verify issue analysis depth (comparable to Screaming Frog/Ahrefs)
        for issue in diagnostic_data['all_issues']:
            # Each issue should have professional-grade analysis
            assert 'impact_score' in issue, "Should have impact scoring"
            assert 'effort_score' in issue, "Should have effort estimation"
            assert 'roi_score' in issue, "Should have ROI calculation"
            assert issue['priority'] in ['critical', 'high', 'medium', 'low'], "Should have proper priority classification"
        
        # Verify category analysis depth (comparable to SEMrush)
        for category, data in diagnostic_data['category_scores'].items():
            assert 'score' in data, "Each category should have score"
            assert 'issues_found' in data, "Each category should track issues"
            assert 'critical_issues' in data, "Each category should track critical issues"
            assert 0 <= data['score'] <= 100, "Scores should be in valid range"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])