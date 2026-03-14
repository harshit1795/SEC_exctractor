"""
FinancialAnalyzer Service
Migrated from Streamlit chatbot_tab.py

AI-powered financial analysis using Google Gemini
"""
import logging
import asyncio
import time
import json
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from google.generativeai.types import content_types
from app.config import settings
from app.services.rate_limiter import get_rate_limiter
from app.services.agent_tools import FINANCIAL_TOOLS, execute_tool
import hashlib

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """AI-powered financial analysis engine"""
    
    # Version of the prompts. Update this to invalidate all cached summaries.
    PROMPT_VERSION = "v1"
    
    def __init__(self, api_key: Optional[str] = None, cache: Any = None):
        """
        Initialize FinancialAnalyzer with API key
        
        Args:
            api_key: Google Generative AI API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.gemini_api_key
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        # Initialize rate limiter (15 requests per minute - conservative limit)
        self.rate_limiter = get_rate_limiter(max_requests=15, window_seconds=60)
        self.cache = cache
    
    
    async def summarize_sec_comparison(
        self,
        section_name: str,
        ticker_texts: Dict[str, str]
    ) -> str:
        """
        Generate a comparative AI summary of the same SEC section across multiple tickers.
        
        Args:
            section_name: Name of the section (e.g., 'Business Overview')
            ticker_texts: Dictionary mapping ticker to the section text
            
        Returns:
            AI-generated comparative analysis
        """
        if not ticker_texts:
            return "No data provided for comparison."

        # Truncate texts to avoid context window issues
        formatted_comparison = ""
        for ticker, text in ticker_texts.items():
            content = text[:6000] if text else "Not found."
            formatted_comparison += f"COMPANY: {ticker}\nTEXT:\n{content}\n\n---\n\n"

        system_prompt = (
            "You are an expert financial analyst. Your task is to compare and contrast the provided "
            "SEC filing sections for multiple companies. Identify key similarities, unique competitive "
            "advantages, differing risk profiles, and contrasting strategic directions. "
            "Provide a high-level executive synthesis."
        )
        user_prompt = (
            f"Comparing Section: {section_name}\n\n"
            f"Data for Companies:\n{formatted_comparison}\n"
            "Please provide a comparative summary (max 500 words). "
            "Start with a 'Key Comparisons' bullet list, followed by a deeper synthesis. "
            "Highlight which company appears better positioned based purely on these disclosures."
        )

        try:
            full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            
            # Check cache
            cache_key = None
            if self.cache:
                cache_key = self._generate_cache_key(full_prompt, prefix="ai_comp")
                cached_res = self.cache.get(cache_key)
                if cached_res:
                    logger.info(f"Cache hit for section comparison: {section_name}")
                    return cached_res

            await self.rate_limiter.acquire()
            logger.info(f"Generating comparative summary for section: {section_name}")
            
            response = self.model.generate_content(full_prompt)
            if response and hasattr(response, 'text') and response.text:
                summary = response.text.strip()
                if self.cache and cache_key:
                    # Cache for 30 days
                    self.cache.set(cache_key, summary, expire=86400 * 30)
                return summary
            
            return "Comparative summary generation failed."
        except Exception as e:
            logger.error(f"Error comparing section {section_name}: {e}")
            return f"Comparison unavailable: {str(e)}"

    async def analyze_financial_data(
        self, 
        user_question: str, 
        context_data: Dict[str, Any]
    ) -> str:
        """
        Generate comprehensive financial analysis
        
        Args:
            user_question: User's question/prompt
            context_data: Dictionary with available financial data
        
        Returns:
            AI-generated analysis text
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_question, context_data)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Check cache if available
            cache_key = None
            if self.cache:
                cache_key = self._generate_cache_key(full_prompt, prefix="ai_analysis")
                cached_res = self.cache.get(cache_key)
                if cached_res:
                    logger.info("Cache hit for general financial analysis")
                    return cached_res

            # Acquire rate limit permission before making request
            await self.rate_limiter.acquire()
            
            logger.info(f"Generating AI response for prompt length: {len(user_prompt)}")
            logger.debug(f"Full prompt length: {len(full_prompt)}")
            
            # Retry logic for rate limit errors
            max_retries = 3
            retry_delay = 2  # Start with 2 seconds
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(full_prompt)
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e).lower()
                    is_rate_limit = '429' in error_str or 'rate limit' in error_str or 'quota' in error_str or 'quota exceeded' in error_str
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        # Exponential backoff: 2s, 4s, 8s
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        # Also wait for rate limiter window
                        await self.rate_limiter.acquire()
                        continue
                    else:
                        # Not a rate limit error, or out of retries - re-raise
                        raise
            
            if not response:
                logger.warning("No response object returned from Gemini API")
                raise ValueError("No response received from Gemini API")
            
            # Check for blocked content or errors
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if response.prompt_feedback.block_reason:
                    logger.error(f"Content blocked: {response.prompt_feedback.block_reason}")
                    raise ValueError(f"Content was blocked: {response.prompt_feedback.block_reason}")
            
            if not hasattr(response, 'text') or not response.text:
                logger.warning("Empty response.text from Gemini API")
                # Try to get error details
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason != 'STOP':
                        logger.error(f"Response finished with reason: {candidate.finish_reason}")
                        raise ValueError(f"Response generation stopped: {candidate.finish_reason}")
                raise ValueError("Empty response received from Gemini API")
            
            logger.info(f"Successfully generated response of length: {len(response.text)}")
            result = response.text
            
            # Store in cache if available
            if self.cache and cache_key:
                # Use default TTL for general analysis as data may change more frequently
                self.cache.set(cache_key, result, expire=settings.cache_ttl)
                
            return result
        except ValueError as e:
            # Re-raise ValueError as-is (these are our custom errors)
            raise
        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            # Re-raise to let the API handle it properly
            raise

    async def analyze_with_agent(
        self,
        prompt: str,
        chat_history: List[Dict[str, Any]],
        data_manager: Any
    ) -> str:
        """
        Agentic loop that uses Gemini function calling to autonomously fetch
        financial data via the DataSourceManager before responding.
        
        Args:
            prompt: the user's latest message (which may include injected widget context)
            chat_history: list of dicts with 'role' ('user' or 'model') and 'parts'
            data_manager: instance of DataSourceManager
        """
        try:
            # Format history into genai primitives
            formatted_history = []
            
            # Start with the system prompt as a model message or combine it with the first user message
            system_msg = self._build_system_prompt()
            # In gemini, system instructions are set on model init or pass as system_instruction
            
            # Build the model with tools and system instruction
            model_with_tools = genai.GenerativeModel(
                model_name='gemini-2.0-flash', # Use latest stable flash model
                tools=FINANCIAL_TOOLS,
                system_instruction=system_msg
            )
            
            for msg in chat_history:
                # msg format: {"role": "user"|"model", "content": "..."}
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append(
                    content_types.ContentDict.from_dict({
                        "role": role,
                        "parts": [msg["content"]]
                    })
                )
                
            # Start chat session
            chat = model_with_tools.start_chat(history=formatted_history)
            
            await self.rate_limiter.acquire()
            logger.info(f"Starting agent tool loop for prompt length: {len(prompt)}")
            
            # First turn: send the prompt
            response = chat.send_message(prompt)
            
            # Loop for function calling (max 5 iterations to prevent infinite loops)
            iterations = 0
            while iterations < 5:
                # Check if the model wants to call a function
                if response.function_call:
                    fc = response.function_call
                    logger.info(f"Agent requested tool call: {fc.name}")
                    
                    # Execute tool
                    tool_result = await execute_tool(data_manager, fc)
                    
                    # Send result back to model
                    await self.rate_limiter.acquire()
                    response = chat.send_message(
                        content_types.ContentDict(
                            role="function",
                            parts=[
                                genai.types.FunctionResponseDict(
                                    name=fc.name,
                                    response=tool_result
                                )
                            ]
                        )
                    )
                    iterations += 1
                else:
                    # No function call, model returned text
                    break
                    
            if not response.text:
                raise ValueError("Agent failed to return a final text response.")
                
            return response.text
            
        except Exception as e:
            logger.error(f"Error in agent workflow: {e}", exc_info=True)
            raise

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text from a raw prompt without contextual wrapping.
        Used by health report generation.
        """
        try:
            await self.rate_limiter.acquire()
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    break
                except Exception as e:
                    error_str = str(e).lower()
                    is_rate_limit = '429' in error_str or 'rate limit' in error_str or 'quota' in error_str
                    if is_rate_limit and attempt < max_retries - 1:
                        await asyncio.sleep(2 ** (attempt + 1))
                        await self.rate_limiter.acquire()
                        continue
                    raise

            if not response or not hasattr(response, 'text') or not response.text:
                raise ValueError("Empty response from Gemini API")

            return response.text
        except Exception as e:
            logger.error(f"Error in generate_text: {e}", exc_info=True)
            raise


    def _generate_cache_key(self, prompt: str, prefix: str = "ai") -> str:
        """Generates a deterministic cache key for a prompt."""
        hash_val = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        return f"{prefix}_{self.PROMPT_VERSION}_{hash_val}"

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for financial analysis"""
        return '''You are FinQ, an expert financial analyst AI assistant with deep knowledge of:
- Financial statement analysis (Income Statement, Balance Sheet, Cash Flow)
- Market analysis and stock valuation
- Economic indicators and macroeconomic trends
- SEC filings and regulatory compliance
- Risk assessment and financial modeling

Your capabilities:
1. Analyze financial data from multiple sources (Yahoo Finance, FRED, SEC filings)
2. Provide insights on trends, ratios, and financial health
3. Compare companies and sectors
4. Identify risks and opportunities
5. Explain complex financial concepts in simple terms
6. Make data-driven recommendations

Guidelines:
- Always base your analysis on the provided data
- Be specific with numbers and metrics when available
- Highlight trends and patterns
- Identify potential risks or concerns
- Provide actionable insights
- Use professional financial terminology appropriately
- If data is insufficient, clearly state what additional information would be helpful
- Format responses with clear sections and bullet points when appropriate'''
    
    def _build_user_prompt(self, user_question: str, context_data: Dict[str, Any]) -> str:
        """Build user prompt with context data"""
        
        prompt_parts = [f"User Question: {user_question}\n"]
        
        # Add available data sources
        if context_data.get('available_tickers'):
            prompt_parts.append(f"Available Companies: {', '.join(context_data['available_tickers'])}\n")
        
        # Add specific company data if available
        if context_data.get('selected_tickers'):
            tickers = context_data['selected_tickers']
            prompt_parts.append(f"Selected Companies: {', '.join(tickers)}\n")
            
            # Add selected metric categories
            if context_data.get('metric_categories'):
                prompt_parts.append(f"Selected Metrics: {', '.join(context_data['metric_categories'])}\n")
            
            # Add Yahoo Finance data for all companies
            if context_data.get('yahoo_data'):
                yf_data = context_data['yahoo_data']
                for ticker, data in yf_data.items():
                    if isinstance(data, dict) and data.get('info'):
                        company_name = data['info'].get('longName', ticker)
                        sector = data['info'].get('sector', 'N/A')
                        prompt_parts.append(f"Company {ticker} ({company_name}): {sector}\n")
                        
                        if data['info'].get('longBusinessSummary'):
                            summary = data['info']['longBusinessSummary']
                            prompt_parts.append(f"  Business: {summary[:200]}...\n")
        
        # Add economic data if available
        if context_data.get('economic_data') is not None:
            prompt_parts.append("Economic Data Available: FRED economic indicators\n")
        
        # Add fundamentals data if available
        if context_data.get('fundamentals_data') is not None:
            prompt_parts.append("Fundamentals Data Available: Historical financial metrics\n")

        # Add 10-K data if available
        if context_data.get('10k_data'):
            prompt_parts.append("10-K Filing Data Available:\n")
            for ticker, data in context_data['10k_data'].items():
                prompt_parts.append(f"  Company: {ticker}\n")
                if isinstance(data, dict):
                    for section, text in data.items():
                        if text and "not found" not in str(text).lower():
                            prompt_parts.append(f"    - {section}: {str(text)[:4000]}...\n")

        # Add 10-Q data if available
        if context_data.get('10q_data'):
            prompt_parts.append("10-Q Filing Data Available:\n")
            for ticker, data in context_data['10q_data'].items():
                prompt_parts.append(f"  Company: {ticker}\n")
                if isinstance(data, dict):
                    for section, text in data.items():
                        if text and "not found" not in str(text).lower():
                            prompt_parts.append(f"    - {section}: {str(text)[:4000]}...\n")
        
        prompt_parts.append("\nPlease provide a comprehensive analysis based on the available data.")
        
        return "\n".join(prompt_parts)

