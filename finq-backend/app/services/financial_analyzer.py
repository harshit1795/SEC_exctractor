"""
FinancialAnalyzer Service
Migrated from Streamlit chatbot_tab.py

AI-powered financial analysis using Google Gemini
"""
import logging
import asyncio
import time
import json
import re
from typing import Dict, Any, Optional, List
# New google-genai SDK: per-instance Client (no global configure)
from google import genai as google_genai
# Legacy SDK still used for FINANCIAL_TOOLS type declarations
import google.generativeai as genai_legacy
from google.generativeai.types import content_types
from google.genai.types import HttpOptions, HttpRetryOptions
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
        Initialize FinancialAnalyzer with API key.
        Uses the new google-genai SDK (Client-per-instance) for BYOK isolation.
        """
        self.api_key = api_key or settings.gemini_api_key
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        key_preview = self.api_key[:8] + '...' if len(self.api_key) > 8 else '???'
        logger.info(f"FinancialAnalyzer init: api_key={key_preview}")

        # ── New per-instance Client (google-genai SDK) ──────────────────────
        # Fully isolated — no global configure() calls, no race conditions.
        # Every BYOK request gets its own Client pointing to its own quota.
        # attempts=1 prevents the SDK from auto-sleeping 60 s on 429.
        self._genai_client = google_genai.Client(
            api_key=self.api_key,
            http_options=HttpOptions(
                retry_options=HttpRetryOptions(attempts=1)
            )
        )

        # ── Legacy SDK model — created LAZILY, NOT here ─────────────────────
        # Previously we called genai_legacy.configure(api_key=...) in __init__,
        # which is a PROCESS-WIDE global.  Any code that creates a new
        # FinancialAnalyzer (e.g. health_scores.py with a BYOK key, or
        # data_source_manager.py) would immediately overwrite the global key for
        # ALL other instances still mid-flight — causing spurious 429s on the
        # chat endpoint.
        #
        # Solution: never call configure() in __init__.  Only call it inside the
        # private _get_legacy_model() helper right before the legacy SDK is used,
        # and only for the two methods that still rely on it.
        self._legacy_model: Optional[genai_legacy.GenerativeModel] = None

        # Initialize rate limiter (15 requests per minute, shared across processes)
        self.rate_limiter = get_rate_limiter(max_requests=15, window_seconds=60)
        self.cache = cache

    def _get_legacy_model(self) -> genai_legacy.GenerativeModel:
        """
        Lazily create the legacy generative model, configuring the SDK only
        at the point of first use (not in __init__).  This eliminates the
        risk of overwriting the global key for other concurrent instances.
        Note: the legacy SDK is still inherently global — prefer the new
        self._genai_client for new functionality whenever possible.
        """
        if self._legacy_model is None:
            genai_legacy.configure(api_key=self.api_key)
            # Used currently just for fallback counting where we absolutely need the legacy library
            self._legacy_model = genai_legacy.GenerativeModel('gemini-2.5-flash')
        return self._legacy_model

    
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
            
            response = self._get_legacy_model().generate_content(full_prompt)
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
            
            # Retry logic for rate limit errors (per-minute only — daily quota errors propagate immediately)
            max_retries = 3
            retry_delay = 2  # Start with 2 seconds
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = self._get_legacy_model().generate_content(full_prompt)
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e).lower()
                    is_daily_quota = '429' in error_str and (
                        'per day' in error_str or 'daily' in error_str or
                        'generate_content_free_tier_requests' in error_str or
                        'generate_content_free_tier_input_token_count' in error_str
                    )
                    is_per_minute_limit = ('429' in error_str or 'rate limit' in error_str) and not is_daily_quota
                    
                    if is_daily_quota:
                        # Don't retry — daily quota is exhausted, propagate immediately
                        # so the frontend can prompt for BYOK
                        raise
                    elif is_per_minute_limit and attempt < max_retries - 1:
                        # Exponential backoff for per-minute limits: 2s, 4s
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Per-minute rate limit hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        await self.rate_limiter.acquire()
                        continue
                    else:
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
        Agentic loop using the new google-genai SDK with a per-instance Client.
        This eliminates the global genai.configure() race condition entirely.
        BYOK key is bound to self._genai_client — cannot be overwritten by
        concurrent requests that use a different key.
        """
        try:
            system_msg = self._build_system_prompt()

            # Convert FINANCIAL_TOOLS to new SDK format
            # The new SDK accepts tool dicts directly
            tools_config = None
            if FINANCIAL_TOOLS:
                declarations = []
                for fn in FINANCIAL_TOOLS[0].function_declarations:
                    # Manually construct the parameter schema since legacy objects lack simple dict conversion
                    params = {"type": "OBJECT", "properties": {}, "required": []}
                    if hasattr(fn, 'parameters') and fn.parameters:
                        # Convert legacy Schema to dict
                        p = fn.parameters
                        params["type"] = p.type.name if hasattr(p.type, 'name') else "OBJECT"
                        
                        if hasattr(p, 'properties'):
                            for k, v in p.properties.items():
                                prop_dict = {"type": v.type.name if hasattr(v.type, 'name') else "STRING"}
                                if hasattr(v, 'description') and v.description:
                                    prop_dict["description"] = v.description
                                if hasattr(v, 'items') and v.items:
                                    item_type = v.items.type.name if hasattr(v.items.type, 'name') else "STRING"
                                    prop_dict["items"] = {"type": item_type}
                                params["properties"][k] = prop_dict
                        
                        if hasattr(p, 'required'):
                            params["required"] = list(p.required)
                    
                    declarations.append({
                        "name": fn.name,
                        "description": fn.description,
                        "parameters": params
                    })
                tools_config = [{"function_declarations": declarations}]

            # Format chat history for new SDK
            history_for_sdk = []
            for msg in chat_history:
                role = "user" if msg["role"] == "user" else "model"
                history_for_sdk.append(
                    google_genai.types.Content(
                        role=role,
                        parts=[google_genai.types.Part(text=msg["content"])]
                    )
                )

            await self.rate_limiter.acquire()
            logger.info(f"Starting agent tool loop. API key: {self.api_key[:8]}...")

            # Create chat session via per-instance client — BYOK-safe
            chat = self._genai_client.chats.create(
                model='gemini-2.5-flash',
                config=google_genai.types.GenerateContentConfig(
                    system_instruction=system_msg,
                    tools=tools_config,
                ),
                history=history_for_sdk,
            )

            # Retry logic for rate limit errors in the first turn
            max_retries = 4
            retry_delay = 2
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = chat.send_message(prompt)
                    break
                except google_genai.errors.ClientError as e:
                    error_str = str(e.message).lower() if hasattr(e, 'message') else str(e).lower()
                    is_daily_quota = getattr(e, 'code', 0) == 429 and (
                        'per day' in error_str or 'daily' in error_str or
                        'limit: 0' in error_str
                    )
                    is_per_minute = getattr(e, 'code', 0) == 429 and not is_daily_quota
                    
                    if is_daily_quota:
                        # Don't retry — daily quota is exhausted, propagate immediately
                        # so the frontend can prompt for BYOK
                        err = ValueError(f"Gemini API daily quota exceeded: {error_str}")
                        err.status_code = 429  # type: ignore[attr-defined]
                        raise err
                    elif is_per_minute and attempt < max_retries - 1:
                        # Attempt to parse Google's exact requested delay if it is larger
                        retry_match = re.search(r'retry in\s+([0-9.]+)\s*s', error_str)
                        if retry_match:
                            wait_time = float(retry_match.group(1)) + 1.0
                        else:
                            wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Per-minute rate limit hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        await self.rate_limiter.acquire()
                        continue
                    else:
                        raise
            
            if not response:
                raise ValueError("No response received from agent after retries.")

            # Agentic tool-call loop (max 3 iterations to save quota)
            iterations = 0
            while iterations < 3:
                # Check for function calls in new SDK response
                fc = None
                if response.candidates:
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            fc = part.function_call
                            break

                if fc:
                    logger.info(f"Agent requested tool call: {fc.name}")
                    tool_result = await execute_tool(data_manager, fc)
                    
                    # Truncate extremely large JSON responses (like SEC filings)
                    # to prevent immediately blowing up the Input Token quota
                    result_str = json.dumps(tool_result, default=str)
                    if len(result_str) > 4000:
                        logger.warning(f"Tool {fc.name} payload extremely large ({len(result_str)} chars). Truncating.")
                        truncated_str = result_str[:4000] + "... [DATA TRUNCATED: THIS PAYLOAD WAS TOO LARGE FOR THE MODEL CONTEXT WINDOW. RELY ON WHAT IS PROVIDED.]"
                        tool_result = {"truncated_response": truncated_str}

                    await self.rate_limiter.acquire()
                    
                    # Retry logic for tool response transmission
                    max_tool_retries = 4
                    tool_retry_delay = 2
                    tool_response_success = False

                    for attempt in range(max_tool_retries):
                        try:
                            response = chat.send_message(
                                google_genai.types.Part(
                                    function_response=google_genai.types.FunctionResponse(
                                        name=fc.name,
                                        response=tool_result,
                                    )
                                )
                            )
                            tool_response_success = True
                            break
                        except google_genai.errors.ClientError as e:
                            error_str = str(e.message).lower() if hasattr(e, 'message') else str(e).lower()
                            is_daily_quota = getattr(e, 'code', 0) == 429 and (
                                'per day' in error_str or 'daily' in error_str or 'limit: 0' in error_str
                            )
                            if is_daily_quota:
                                err = ValueError(f"Gemini API daily quota exceeded: {error_str}")
                                err.status_code = 429  # type: ignore[attr-defined]
                                raise err
                            elif getattr(e, 'code', 0) == 429 and attempt < max_tool_retries - 1:
                                retry_match = re.search(r'retry in\s+([0-9.]+)\s*s', error_str)
                                if retry_match:
                                    wait_time = float(retry_match.group(1)) + 1.0
                                else:
                                    wait_time = tool_retry_delay * (2 ** attempt)
                                logger.warning(f"Per-minute rate limit hit during tool execution {fc.name} (attempt {attempt + 1}/{max_tool_retries}). Waiting {wait_time}s...")
                                await asyncio.sleep(wait_time)
                                await self.rate_limiter.acquire()
                                continue
                            else:
                                raise

                    if not tool_response_success:
                        raise ValueError(f"Failed to send tool response for {fc.name} after retries.")

                    iterations += 1
                else:
                    break

            final_text = response.text if hasattr(response, 'text') else ''
            if not final_text and response.candidates:
                final_text = response.candidates[0].content.parts[0].text or ''

            if not final_text:
                raise ValueError("Agent failed to return a final text response.")

            return final_text

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
                    response = self._get_legacy_model().generate_content(prompt)
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

    async def analyze_standard(self, prompt: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Standard single-turn LLM generation for FinQ Chat.
        Uses the per-instance self._genai_client (new google-genai SDK) — fully
        isolated from concurrent BYOK requests that would otherwise overwrite the
        global genai_legacy.configure() key and trigger quota errors here.
        No tools are enabled to keep it fast and quota-friendly.
        """
        try:
            await self.rate_limiter.acquire()

            # Format chat history for the new SDK (Content/Part objects).
            history_for_sdk: List[google_genai.types.Content] = []
            if chat_history:
                for msg in chat_history[-10:]:  # keep last 10 messages
                    role = "user" if msg["role"] == "user" else "model"
                    history_for_sdk.append(
                        google_genai.types.Content(
                            role=role,
                            parts=[google_genai.types.Part(text=msg["content"])],
                        )
                    )

            # Create a chat session WITHOUT tools — standard mode stays cheap.
            chat = self._genai_client.chats.create(
                model="gemini-2.5-flash",
                config=google_genai.types.GenerateContentConfig(
                    system_instruction=self._build_system_prompt(),
                    # Explicitly no tools — keep this lean
                ),
                history=history_for_sdk,
            )

            # Retry on transient per-minute limits; bail immediately on daily quota.
            max_retries = 4
            retry_delay = 2
            response = None

            for attempt in range(max_retries):
                try:
                    response = chat.send_message(prompt)
                    break
                except google_genai.errors.ClientError as e:
                    error_str = str(e.message).lower() if hasattr(e, "message") else str(e).lower()
                    is_daily_quota = getattr(e, "code", 0) == 429 and (
                        "per day" in error_str
                        or "daily" in error_str
                        or "limit: 0" in error_str
                    )
                    is_per_minute = getattr(e, "code", 0) == 429 and not is_daily_quota

                    if is_daily_quota:
                        err = ValueError(f"Gemini API daily quota exceeded: {error_str}")
                        err.status_code = 429  # type: ignore[attr-defined]
                        raise err
                    elif is_per_minute and attempt < max_retries - 1:
                        retry_match = re.search(r'retry in\s+([0-9.]+)\s*s', error_str)
                        if retry_match:
                            wait_time = float(retry_match.group(1)) + 1.0
                        else:
                            wait_time = retry_delay * (2 ** attempt)
                        logger.warning(
                            f"Standard mode: per-minute rate limit hit "
                            f"(attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                        await self.rate_limiter.acquire()
                        continue
                    else:
                        logger.error("Standard mode max retries exceeded or unknown ClientError occurred.")
                        raise ValueError("No response received from standard generation after retries.")

            if not response:
                raise ValueError("No response received from standard generation after retries.")

            # Extract text safely.
            final_text = response.text if hasattr(response, "text") else ""
            if not final_text and response.candidates:
                final_text = response.candidates[0].content.parts[0].text or ""

            if not final_text:
                raise ValueError("Standard generation returned an empty response.")

            return final_text

        except Exception as e:
            logger.error(f"Error in standard chat workflow: {e}", exc_info=True)
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

