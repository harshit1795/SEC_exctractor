"""
FinancialAnalyzer Service
Migrated from Streamlit chatbot_tab.py

AI-powered financial analysis using Google Gemini
"""
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """AI-powered financial analysis engine"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FinancialAnalyzer with API key
        
        Args:
            api_key: Google Generative AI API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.gemini_api_key
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-flash-latest')
    
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
        
        try:
            logger.info(f"Generating AI response for prompt length: {len(user_prompt)}")
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            logger.debug(f"Full prompt length: {len(full_prompt)}")
            
            response = self.model.generate_content(full_prompt)
            
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
            return response.text
        except ValueError as e:
            # Re-raise ValueError as-is (these are our custom errors)
            raise
        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            # Re-raise to let the API handle it properly
            raise
    
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

