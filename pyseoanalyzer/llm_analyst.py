from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

import asyncio
import json
import os
import logging
from .siliconflow_llm import SiliconFlowLLM

load_dotenv()
logger = logging.getLogger(__name__)


# Pydantic models for structured output
class EntityAnalysis(BaseModel):
    entity_assessment: str = Field(
        description="Detailed analysis of entity optimization"
    )
    knowledge_panel_readiness: int = Field(description="Score from 0-100")
    key_improvements: List[str] = Field(description="Top 3 improvements needed")


class CredibilityAnalysis(BaseModel):
    credibility_assessment: str = Field(description="Overall credibility analysis")
    neeat_scores: Dict[str, int] = Field(
        description="Individual N-E-E-A-T-T component scores"
    )
    trust_signals: List[str] = Field(description="Identified trust signals")


class ConversationAnalysis(BaseModel):
    conversation_readiness: str = Field(description="Overall assessment")
    query_patterns: List[str] = Field(description="Identified query patterns")
    engagement_score: int = Field(description="Score from 0-100")
    gaps: List[str] = Field(description="Identified conversational gaps")


class PlatformPresence(BaseModel):
    platform_coverage: Dict[str, str] = Field(
        description="Coverage analysis per platform"
    )
    visibility_scores: Dict[str, int] = Field(description="Scores per platform type")
    optimization_opportunities: List[str] = Field(description="List of opportunities")


class ProfessionalSEOAnalysis(BaseModel):
    """Enhanced SEO analysis using professional diagnostic data"""
    strategic_assessment: str = Field(description="High-level strategic analysis")
    technical_priorities: List[str] = Field(description="Top 5 technical optimization priorities")
    content_recommendations: List[str] = Field(description="Content optimization recommendations")
    competitive_insights: str = Field(description="Competitive positioning analysis")
    implementation_roadmap: Dict[str, str] = Field(description="Phased implementation recommendations")
    roi_estimation: str = Field(description="Expected ROI and impact analysis")
    risk_assessment: str = Field(description="Risk factors and mitigation strategies")


class SEORecommendations(BaseModel):
    strategic_recommendations: List[str] = Field(
        description="Major strategic recommendations"
    )
    quick_wins: List[str] = Field(description="Immediate action items")
    long_term_strategy: List[str] = Field(description="Long-term strategic goals")
    priority_matrix: Dict[str, str] = Field(
        description="Priority matrix by impact/effort"
    )


class LLMSEOEnhancer:
    """Enhanced SEO analyzer using Claude or Silicon Flow for intelligent insights."""
    
    def __init__(self, api_key: Optional[str] = None, use_siliconflow: bool = False, siliconflow_api_key: Optional[str] = None, siliconflow_model: Optional[str] = None):
        """
        Initialize the LLM SEO enhancer.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            use_siliconflow: Whether to use Silicon Flow API instead of Anthropic
            siliconflow_api_key: Silicon Flow API key (defaults to SILICONFLOW_API_KEY env var)
            siliconflow_model: Silicon Flow model to use (defaults to SILICONFLOW_MODEL env var or Qwen/Qwen2.5-VL-72B-Instruct)
        """
        self.use_siliconflow = use_siliconflow or bool(os.getenv("SILICONFLOW_API_KEY"))
        
        if self.use_siliconflow:
            # Get model from parameter, env var, or default
            model = siliconflow_model or os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
            self.siliconflow_llm = SiliconFlowLLM(siliconflow_api_key, model)
            self.llm = None
        else:
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
            
            self.llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                anthropic_api_key=self.api_key,
                temperature=0,
                timeout=30,
                max_retries=3,
            )
            self.siliconflow_llm = None
        
        if not self.use_siliconflow:
            self._setup_chains()

    def _setup_chains(self):
        """Setup modern LangChain runnable sequences using pipe syntax"""
        # Entity Analysis Chain
        entity_parser = PydanticOutputParser(pydantic_object=EntityAnalysis)

        entity_prompt = PromptTemplate.from_template(
            """Analyze these SEO elements for entity optimization:
            1. Entity understanding (Knowledge Panel readiness)
            2. Brand credibility signals (N-E-E-A-T-T principles)
            3. Entity relationships and mentions
            4. Topic entity connections
            5. Schema markup effectiveness
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.entity_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: entity_parser.get_format_instructions(),
            }
            | entity_prompt
            | self.llm
            | entity_parser
        )

        # Credibility Analysis Chain
        credibility_parser = PydanticOutputParser(pydantic_object=CredibilityAnalysis)

        credibility_prompt = PromptTemplate.from_template(
            """Evaluate these credibility aspects:
            1. N-E-E-A-T-T signals
            2. Entity understanding and validation
            3. Content creator credentials
            4. Publisher authority
            5. Topic expertise signals
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.credibility_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: credibility_parser.get_format_instructions(),
            }
            | credibility_prompt
            | self.llm
            | credibility_parser
        )

        # Conversation Analysis Chain
        conversation_parser = PydanticOutputParser(pydantic_object=ConversationAnalysis)

        conversation_prompt = PromptTemplate.from_template(
            """Analyze content for conversational search readiness:
            1. Query pattern matching
            2. Intent coverage across funnel
            3. Natural language understanding
            4. Follow-up content availability
            5. Conversational triggers
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.conversation_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: conversation_parser.get_format_instructions(),
            }
            | conversation_prompt
            | self.llm
            | conversation_parser
        )

        # Platform Presence Chain
        platform_parser = PydanticOutputParser(pydantic_object=PlatformPresence)

        platform_prompt = PromptTemplate.from_template(
            """Analyze presence across different platforms:
            1. Search engines (Google, Bing)
            2. Knowledge graphs
            3. AI platforms (ChatGPT, Bard)
            4. Social platforms
            5. Industry-specific platforms
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.platform_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: platform_parser.get_format_instructions(),
            }
            | platform_prompt
            | self.llm
            | platform_parser
        )

        # Recommendations Chain
        recommendations_parser = PydanticOutputParser(
            pydantic_object=SEORecommendations
        )

        recommendations_prompt = PromptTemplate.from_template(
            """Based on this complete analysis, provide strategic recommendations:
            1. Entity optimization strategy
            2. Content strategy across platforms
            3. Credibility building actions
            4. Conversational optimization
            5. Cross-platform presence improvement
            
            Analysis results:
            {analysis_results}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.recommendations_chain = (
            {
                "analysis_results": RunnablePassthrough(),
                "format_instructions": lambda _: recommendations_parser.get_format_instructions(),
            }
            | recommendations_prompt
            | self.llm
            | recommendations_parser
        )

    async def enhance_seo_analysis(self, seo_data: Dict) -> Dict:
        """
        Enhanced SEO analysis using modern LangChain patterns with timing and progress tracking
        """
        import time
        start_time = time.time()
        logger.info("🚀 Starting LLM SEO analysis...")
        
        try:
            if self.use_siliconflow:
                # Use Silicon Flow API for analysis
                logger.info("📡 Using SiliconFlow API for comprehensive analysis")
                analysis_start = time.time()
                result = await self.siliconflow_llm.analyze_seo_data(seo_data, "comprehensive")
                analysis_time = time.time() - analysis_start
                logger.info(f"✅ SiliconFlow analysis completed in {analysis_time:.2f}s")
                return result
            else:
                # Use Anthropic Claude for analysis with detailed timing
                logger.info("🤖 Using Anthropic Claude for detailed analysis")
                
                # Convert seo_data to string for prompt insertion
                seo_data_str = json.dumps(seo_data, indent=2)
                logger.info(f"📊 Prepared {len(seo_data_str)} chars of SEO data for analysis")

                # Run analysis chains in parallel with timing
                logger.info("⚡ Running 4 parallel analysis chains...")
                parallel_start = time.time()
                
                try:
                    entity_results, credibility_results, conversation_results, platform_results = (
                        await asyncio.wait_for(
                            asyncio.gather(
                                self.entity_chain.ainvoke(seo_data_str),
                                self.credibility_chain.ainvoke(seo_data_str),
                                self.conversation_chain.ainvoke(seo_data_str),
                                self.platform_chain.ainvoke(seo_data_str),
                                return_exceptions=True
                            ),
                            timeout=90.0  # 90 second timeout for parallel analysis
                        )
                    )
                    parallel_time = time.time() - parallel_start
                    logger.info(f"✅ Parallel analysis completed in {parallel_time:.2f}s")
                    
                    # Check for exceptions in results
                    results = [entity_results, credibility_results, conversation_results, platform_results]
                    failed_analyses = []
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            analysis_names = ["entity", "credibility", "conversation", "platform"]
                            failed_analyses.append(analysis_names[i])
                            logger.warning(f"❌ {analysis_names[i]} analysis failed: {result}")
                    
                    if failed_analyses:
                        logger.warning(f"⚠️ {len(failed_analyses)} analysis chains failed: {failed_analyses}")
                    
                    # Use successful results only
                    if not isinstance(entity_results, Exception):
                        entity_dict = entity_results.model_dump()
                    else:
                        entity_dict = {"entity_assessment": "Analysis failed", "knowledge_panel_readiness": 0, "key_improvements": []}
                        
                    if not isinstance(credibility_results, Exception):
                        credibility_dict = credibility_results.model_dump()
                    else:
                        credibility_dict = {"credibility_assessment": "Analysis failed", "neeat_scores": {}, "trust_signals": []}
                        
                    if not isinstance(conversation_results, Exception):
                        conversation_dict = conversation_results.model_dump()
                    else:
                        conversation_dict = {"conversation_readiness": "Analysis failed", "query_patterns": [], "engagement_score": 0, "gaps": []}
                        
                    if not isinstance(platform_results, Exception):
                        platform_dict = platform_results.model_dump()
                    else:
                        platform_dict = {"platform_coverage": {}, "visibility_scores": {}, "optimization_opportunities": []}

                except asyncio.TimeoutError:
                    logger.error("⏰ LLM analysis timed out after 90 seconds")
                    # Return basic fallback analysis
                    return {
                        **seo_data,
                        "llm_analysis": {
                            "status": "timeout",
                            "message": "Analysis timed out - server may be under heavy load",
                            "execution_time": time.time() - start_time,
                            "recommendations": ["Try again later when server load is lower"]
                        }
                    }

                # Combine analyses
                logger.info("🔄 Combining analysis results...")
                combined_analysis = {
                    "entity_analysis": entity_dict,
                    "credibility_analysis": credibility_dict,
                    "conversation_analysis": conversation_dict,
                    "cross_platform_presence": platform_dict,
                }

                # Generate final recommendations with timeout
                logger.info("💡 Generating final recommendations...")
                recommendations_start = time.time()
                try:
                    recommendations = await asyncio.wait_for(
                        self.recommendations_chain.ainvoke(
                            json.dumps(combined_analysis, indent=2)
                        ),
                        timeout=30.0  # 30 second timeout for recommendations
                    )
                    recommendations_time = time.time() - recommendations_start
                    logger.info(f"✅ Recommendations generated in {recommendations_time:.2f}s")
                    recommendations_dict = recommendations.model_dump()
                except asyncio.TimeoutError:
                    logger.warning("⏰ Recommendations generation timed out")
                    recommendations_dict = {
                        "strategic_recommendations": ["Analysis completed but recommendations timed out"],
                        "priority_actions": ["Review basic SEO fundamentals"],
                        "expected_impact": "medium"
                    }
                except Exception as e:
                    logger.error(f"❌ Recommendations generation failed: {e}")
                    recommendations_dict = {
                        "strategic_recommendations": ["Basic SEO analysis completed"],
                        "priority_actions": ["Review SEO fundamentals"],
                        "expected_impact": "medium"
                    }

                # Combine all results
                final_results = {
                    **seo_data,
                    **combined_analysis,
                    "recommendations": recommendations_dict,
                }

                total_time = time.time() - start_time
                logger.info(f"🎉 Complete LLM analysis finished in {total_time:.2f}s")
                
                # Add timing metadata
                final_results["llm_analysis_metadata"] = {
                    "total_execution_time": total_time,
                    "parallel_analysis_time": parallel_time if 'parallel_time' in locals() else 0,
                    "recommendations_time": recommendations_time if 'recommendations_time' in locals() else 0,
                    "provider": "anthropic_claude",
                    "failed_analyses": failed_analyses if 'failed_analyses' in locals() else [],
                    "status": "completed"
                }

                return self._format_output(final_results)
                
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"💥 Critical error in LLM analysis after {total_time:.2f}s: {e}")
            # Return original data with error information
            return {
                **seo_data,
                "llm_analysis": {
                    "status": "error",
                    "error_message": str(e),
                    "execution_time": total_time,
                    "recommendations": ["Unable to complete LLM analysis - check API keys and network connectivity"]
                }
            }

    def _format_output(self, raw_analysis: Dict) -> Dict:
        """Format analysis results into a clean, structured output"""
        return {
            "summary": {
                "entity_score": raw_analysis["entity_analysis"][
                    "knowledge_panel_readiness"
                ],
                "credibility_score": sum(
                    raw_analysis["credibility_analysis"]["neeat_scores"].values()
                )
                / 6,
                "conversation_score": raw_analysis["conversation_analysis"][
                    "engagement_score"
                ],
                "platform_score": sum(
                    raw_analysis["cross_platform_presence"][
                        "visibility_scores"
                    ].values()
                )
                / len(raw_analysis["cross_platform_presence"]["visibility_scores"]),
            },
            "detailed_analysis": raw_analysis,
            "quick_wins": raw_analysis["recommendations"]["quick_wins"],
            "strategic_recommendations": raw_analysis["recommendations"][
                "strategic_recommendations"
            ],
        }

    async def enhanced_professional_analysis(self, enhanced_context: Dict) -> Dict:
        """
        Enhanced LLM analysis using professional diagnostic data
        
        Args:
            enhanced_context: Comprehensive context including professional diagnostics,
                            basic content, metadata, and traditional warnings
        
        Returns:
            Professional-level SEO analysis and recommendations
        """
        try:
            if self.use_siliconflow:
                # Use Silicon Flow for professional analysis
                return await self.siliconflow_llm.analyze_seo_data(enhanced_context, "professional")
            else:
                # For now, fall back to regular analysis with enhanced context
                # TODO: Implement full professional chain
                return await self.enhance_seo_analysis(enhanced_context.get('basic_content', enhanced_context))
                
        except Exception as e:
            logger.error(f"Error in enhanced professional analysis: {e}")
            # Fallback to basic analysis
            return await self.enhance_seo_analysis(enhanced_context.get('basic_content', {}))


# Example usage with async support
async def enhanced_modern_analyze(
    site: str, sitemap: Optional[str] = None, api_key: str = None, **kwargs
):
    """
    Enhanced analysis incorporating modern SEO principles using LangChain
    """
    from pyseoanalyzer import analyze

    # Run original analysis
    original_results = analyze(site, sitemap, **kwargs)

    # Enhance with modern SEO analysis if API key provided
    if api_key:
        enhancer = LLMSEOEnhancer()
        enhanced_results = await enhancer.enhance_seo_analysis(original_results)
        return enhancer._format_output(enhanced_results)

    return original_results
