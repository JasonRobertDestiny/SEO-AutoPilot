import pytest
from pyseoanalyzer.llm_analyst import LLMSEOEnhancer
from pyseoanalyzer.siliconflow_llm import SiliconFlowLLM
import json


@pytest.fixture
def seo_data():
    return {
        "title": "Test Title",
        "description": "Test Description",
        "keywords": ["test", "seo"],
        "content": "This is a test content.",
    }


def test_init():
    enhancer = LLMSEOEnhancer()
    assert isinstance(enhancer.siliconflow_llm, SiliconFlowLLM)
    assert enhancer.siliconflow_llm.model == "Qwen/Qwen2.5-VL-72B-Instruct"


@pytest.mark.asyncio
async def test_enhance_seo_analysis(seo_data):
    enhancer = LLMSEOEnhancer()
    result = await enhancer.enhance_seo_analysis(seo_data)

    assert "summary" in result or "llm_analysis" in result

    # Check for either successful analysis or error handling
    if "llm_analysis" in result:
        # Error case - should have error information
        assert "status" in result["llm_analysis"]
    else:
        # Success case - should have analysis structure
        assert "detailed_analysis" in result or "recommendations" in result


@pytest.mark.asyncio
async def test_enhanced_professional_analysis():
    enhancer = LLMSEOEnhancer()
    
    enhanced_context = {
        'professional_analysis': {
            'all_issues': [
                {'priority': 'critical', 'message': 'Test critical issue'},
                {'priority': 'high', 'message': 'Test high issue'}
            ],
            'overall_score': 77.6
        },
        'basic_content': {
            'title': 'Test Title',
            'keywords': ['test', 'seo']
        }
    }
    
    result = await enhancer.enhanced_professional_analysis(enhanced_context)
    
    # Should have either successful analysis or error handling
    assert result is not None
    assert isinstance(result, dict)
    
    # Check for metadata
    if 'professional_analysis_metadata' in result:
        assert 'provider' in result['professional_analysis_metadata']
        assert result['professional_analysis_metadata']['provider'] == 'siliconflow'