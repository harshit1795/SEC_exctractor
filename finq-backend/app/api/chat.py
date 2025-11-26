"""
Chat and AI analysis API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.data_source_manager import DataSourceManager
from app.models.insight import Insight
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Global instances
_analyzer: Optional[FinancialAnalyzer] = None
_data_manager: Optional[DataSourceManager] = None


def get_analyzer() -> FinancialAnalyzer:
    """Get or create FinancialAnalyzer instance"""
    global _analyzer
    if _analyzer is None:
        try:
            _analyzer = FinancialAnalyzer()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI service not available: {str(e)}"
            )
    return _analyzer


def get_data_manager() -> DataSourceManager:
    """Get or create DataSourceManager instance"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataSourceManager()
    return _data_manager


def _clean_dict_for_storage(d: dict) -> dict:
    """Helper to clean a single dict, handling Timestamp keys and pandas objects"""
    import pandas as pd
    from datetime import datetime
    
    clean = {}
    for k, v in d.items():
        # Convert key if it's a Timestamp
        if isinstance(k, (pd.Timestamp, datetime)):
            clean_key = k.isoformat() if hasattr(k, 'isoformat') else str(k)
        elif isinstance(k, (int, float, str, bool, type(None))):
            clean_key = k
        else:
            clean_key = str(k)
        
        # Convert value - handle pandas objects first
        if isinstance(v, pd.DataFrame):
            # Reset index if it contains Timestamps, then convert to records
            if isinstance(v.index, pd.DatetimeIndex):
                v = v.reset_index()
            clean[clean_key] = v.to_dict(orient='records')
        elif isinstance(v, pd.Series):
            # Convert Series, handling Timestamp index
            if isinstance(v.index, pd.DatetimeIndex):
                clean[clean_key] = {str(idx): _clean_value(val) for idx, val in v.items()}
            else:
                clean[clean_key] = {str(k): _clean_value(v) for k, v in v.to_dict().items()}
        elif isinstance(v, dict):
            clean[clean_key] = _clean_dict_for_storage(v)
        elif isinstance(v, (pd.Timestamp, datetime)):
            clean[clean_key] = v.isoformat() if hasattr(v, 'isoformat') else str(v)
        elif isinstance(v, list):
            clean[clean_key] = [_clean_value(item) for item in v]
        else:
            clean[clean_key] = _clean_value(v)
    return clean


def _clean_value(val):
    """Clean a single value, handling nested structures"""
    import pandas as pd
    from datetime import datetime
    
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.isoformat() if hasattr(val, 'isoformat') else str(val)
    elif isinstance(val, pd.DataFrame):
        if isinstance(val.index, pd.DatetimeIndex):
            val = val.reset_index()
        return val.to_dict(orient='records')
    elif isinstance(val, pd.Series):
        if isinstance(val.index, pd.DatetimeIndex):
            return {str(idx): _clean_value(v) for idx, v in val.items()}
        return {str(k): _clean_value(v) for k, v in val.to_dict().items()}
    elif isinstance(val, dict):
        return _clean_dict_for_storage(val)
    elif isinstance(val, list):
        return [_clean_value(item) for item in val]
    elif isinstance(val, (int, float, str, bool, type(None))):
        return val
    else:
        # Try to serialize, fallback to string
        try:
            import json
            json.dumps(val)
            return val
        except (TypeError, ValueError):
            return str(val)


def _clean_context_for_storage(context: dict) -> dict:
    """
    Clean context data for JSON storage (remove non-serializable types)
    Handles Timestamps as keys, values, and in nested structures
    """
    import pandas as pd
    from datetime import datetime
    import json
    
    def convert_value(val):
        """Recursively convert non-serializable values"""
        if isinstance(val, (pd.Timestamp, datetime)):
            return val.isoformat() if hasattr(val, 'isoformat') else str(val)
        elif isinstance(val, pd.DataFrame):
            # Convert DataFrame to list of dicts, ensuring all values are serializable
            records = val.to_dict(orient='records')
            return [_clean_dict(item) for item in records]
        elif isinstance(val, pd.Series):
            # Convert Series to dict, ensuring all values are serializable
            return _clean_dict(val.to_dict())
        elif isinstance(val, dict):
            return _clean_dict(val)
        elif isinstance(val, list):
            return [convert_value(item) for item in val]
        elif isinstance(val, (int, float, str, bool, type(None))):
            return val
        else:
            # Try to serialize, fallback to string
            try:
                json.dumps(val)
                return val
            except (TypeError, ValueError):
                return str(val)
    
    def _clean_dict(d):
        """Clean a dictionary, handling Timestamp keys"""
        clean = {}
        for k, v in d.items():
            # Convert key if it's a Timestamp
            if isinstance(k, (pd.Timestamp, datetime)):
                clean_key = k.isoformat() if hasattr(k, 'isoformat') else str(k)
            elif isinstance(k, (int, float, str, bool, type(None))):
                clean_key = k
            else:
                clean_key = str(k)
            
            # Convert value
            clean[clean_key] = convert_value(v)
        return clean
    
    return _clean_dict(context)


async def _gather_context_data(context_data: dict, data_manager: DataSourceManager) -> dict:
    """
    Gather all available context data for analysis
    Similar to Streamlit version's _gather_context_data
    """
    import pandas as pd
    
    context = {}
    
    # Selected tickers
    if 'selected_tickers' in context_data:
        context['selected_tickers'] = context_data['selected_tickers']
        
        # Fetch Yahoo Finance data for selected tickers
        yahoo_data = {}
        for ticker in context_data['selected_tickers']:
            try:
                ticker_data = await data_manager.get_yahoo_finance_data(ticker)
                if ticker_data:
                    # Clean ticker data to remove Timestamps - use helper function
                    yahoo_data[ticker] = _clean_dict_for_storage(ticker_data)
            except Exception as e:
                logger.warning(f"Could not fetch Yahoo Finance data for {ticker}: {e}")
        
        if yahoo_data:
            context['yahoo_data'] = yahoo_data
        
        # Fetch fundamentals data
        all_fundamentals = []
        for ticker in context_data['selected_tickers']:
            try:
                fundamentals = await data_manager.get_fundamentals_data(ticker)
                if not fundamentals.empty:
                    # Reset index if it contains Timestamps
                    if isinstance(fundamentals.index, pd.DatetimeIndex):
                        fundamentals = fundamentals.reset_index()
                    # Convert to dict format immediately to avoid Timestamp issues
                    all_fundamentals.append(fundamentals.to_dict(orient='records'))
            except Exception as e:
                logger.warning(f"Could not fetch fundamentals for {ticker}: {e}")
        
        if all_fundamentals:
            # Flatten list of records
            context['fundamentals_data'] = [item for sublist in all_fundamentals for item in sublist]
    
    # Economic data
    if 'economic_data' in context_data:
        economic_data = context_data['economic_data']
        # If it's a DataFrame, convert it
        if isinstance(economic_data, pd.DataFrame):
            # Reset index if it contains Timestamps
            if isinstance(economic_data.index, pd.DatetimeIndex):
                economic_data = economic_data.reset_index()
            context['economic_data'] = economic_data.to_dict(orient='records')
        else:
            context['economic_data'] = economic_data
    
    # Metric categories
    if 'metric_categories' in context_data:
        context['metric_categories'] = context_data['metric_categories']
    
    # 10-K data
    if '10k_data' in context_data:
        context['10k_data'] = context_data['10k_data']
    
    # 10-Q data
    if '10q_data' in context_data:
        context['10q_data'] = context_data['10q_data']
    
    # Available tickers
    context['available_tickers'] = data_manager.get_available_tickers()
    
    return context


@router.post("/analyze", response_model=ChatResponse)
async def analyze_financial_data(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze financial data using AI
    
    Args:
        request: Analysis request with prompt and context
        db: Database session
    
    Returns:
        AI-generated analysis and insight ID
    """
    try:
        # Check if analyzer is available
        try:
            analyzer = get_analyzer()
        except HTTPException as e:
            # Re-raise HTTP exceptions (like 500 for missing API key)
            raise
        except Exception as e:
            logger.error(f"Error getting analyzer: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"AI service initialization failed: {str(e)}. Please check GEMINI_API_KEY configuration."
            )
        
        data_manager = get_data_manager()
        
        # Gather context data
        full_context = await _gather_context_data(request.context_data, data_manager)
        
        # Generate analysis
        logger.info(f"Generating analysis for prompt: {request.prompt[:100]}...")
        try:
            response_text = await analyzer.analyze_financial_data(
                request.prompt,
                full_context
            )
            
            if not response_text or len(response_text.strip()) == 0:
                logger.warning("Received empty response from analyzer")
                response_text = "I apologize, but I received an empty response. Please try rephrasing your question."
            
            logger.info(f"Successfully generated response of length: {len(response_text)}")
        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            # Check if it's an API key issue
            error_msg = str(e).lower()
            if 'api key' in error_msg or 'authentication' in error_msg or 'invalid' in error_msg or 'permission' in error_msg or '403' in error_msg or '401' in error_msg:
                raise HTTPException(
                    status_code=401,
                    detail=f"Google API authentication failed: {str(e)}. Please check your GEMINI_API_KEY in the backend .env file."
                )
            raise HTTPException(
                status_code=500,
                detail=f"Error generating AI response: {str(e)}"
            )
        
        # Store insight in database
        # Clean context data for JSON serialization (remove pandas Timestamps, etc.)
        clean_context = _clean_context_for_storage(full_context)
        
        insight = Insight(
            id=str(uuid.uuid4()),
            user_id=request.context_data.get('user_id', 'anonymous'),
            chat_session_id=request.session_id or str(uuid.uuid4()),
            content={
                "prompt": request.prompt,
                "response": response_text,
                "context": clean_context
            },
            tickers=request.context_data.get('selected_tickers', []),
            summary=response_text[:500] if response_text else None  # First 500 chars as summary
        )
        
        db.add(insight)
        db.commit()
        db.refresh(insight)
        
        return ChatResponse(
            response=response_text,
            insight_id=str(insight.id),
            session_id=insight.chat_session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat analysis: {e}", exc_info=True)
        db.rollback()
        # Provide more helpful error messages
        error_str = str(e).lower()
        if 'api key' in error_str or 'gemini' in error_str or 'authentication' in error_str or 'invalid' in error_str:
            raise HTTPException(
                status_code=401,
                detail=f"Google API authentication failed: {str(e)}. Please configure GEMINI_API_KEY in your backend .env file."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing financial data: {str(e)}"
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get chat history for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of results
        session_id: Optional session ID to filter by
    
    Returns:
        List of chat sessions/insights
    """
    try:
        query = db.query(Insight).filter(Insight.user_id == user_id)
        
        # Filter by session if provided
        if session_id:
            query = query.filter(Insight.chat_session_id == session_id)
        
        insights = query.order_by(
            Insight.created_at.desc()
        ).limit(limit).all()
        
        insights_data = []
        for insight in insights:
            insights_data.append({
                "id": str(insight.id),
                "session_id": insight.chat_session_id,
                "prompt": insight.content.get("prompt", "") if isinstance(insight.content, dict) else "",
                "response": insight.content.get("response", "") if isinstance(insight.content, dict) else "",
                "summary": insight.summary,
                "tickers": insight.tickers,
                "created_at": insight.created_at.isoformat(),
                "shared": insight.shared
            })
        
        return ChatHistoryResponse(
            user_id=user_id,
            insights=insights_data,
            count=len(insights_data)
        )
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )


@router.get("/sessions")
async def get_chat_sessions(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get list of chat sessions for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of sessions
    
    Returns:
        List of sessions with metadata
    """
    try:
        # Get distinct sessions with their latest message
        sessions_query = db.query(
            Insight.chat_session_id,
            func.max(Insight.created_at).label('last_message_at'),
            func.count(Insight.id).label('message_count')
        ).filter(
            Insight.user_id == user_id
        ).group_by(
            Insight.chat_session_id
        ).order_by(
            func.max(Insight.created_at).desc()
        ).limit(limit).all()
        
        sessions_data = []
        for session in sessions_query:
            # Get all insights for this session to generate a theme summary
            session_insights = db.query(Insight).filter(
                Insight.user_id == user_id,
                Insight.chat_session_id == session.chat_session_id
            ).order_by(Insight.created_at.asc()).all()
            
            # Generate a theme summary from all prompts in the session
            summary = None
            if session_insights:
                # Extract all prompts from the session
                prompts = []
                for insight in session_insights:
                    if isinstance(insight.content, dict):
                        prompt = insight.content.get("prompt", "")
                        if prompt:
                            prompts.append(prompt)
                
                if prompts:
                    # Create a concise theme summary
                    # Take first prompt and extract key topics
                    first_prompt = prompts[0]
                    
                    # Common financial analysis themes
                    theme_keywords = {
                        'revenue': 'Revenue Analysis',
                        'profit': 'Profitability',
                        'cash flow': 'Cash Flow',
                        'balance sheet': 'Balance Sheet',
                        'valuation': 'Valuation',
                        'risk': 'Risk Assessment',
                        'market': 'Market Analysis',
                        'overview': 'Company Overview',
                        'trend': 'Trend Analysis',
                        'growth': 'Growth Analysis',
                        'debt': 'Debt Analysis',
                        'earnings': 'Earnings',
                        'margin': 'Margin Analysis',
                    }
                    
                    # Find matching theme
                    first_prompt_lower = first_prompt.lower()
                    theme = None
                    for keyword, theme_name in theme_keywords.items():
                        if keyword in first_prompt_lower:
                            theme = theme_name
                            break
                    
                    # If multiple topics, create a combined theme
                    if len(prompts) > 1:
                        # Count occurrences of different themes
                        theme_counts = {}
                        for prompt in prompts[:3]:  # Check first 3 prompts
                            prompt_lower = prompt.lower()
                            for keyword, theme_name in theme_keywords.items():
                                if keyword in prompt_lower:
                                    theme_counts[theme_name] = theme_counts.get(theme_name, 0) + 1
                        
                        if theme_counts:
                            # Get the most common theme
                            theme = max(theme_counts.items(), key=lambda x: x[1])[0]
                            if len(theme_counts) > 1:
                                # Multiple themes - create a combined summary
                                themes = list(theme_counts.keys())[:2]
                                theme = f"{themes[0]} & {themes[1]}" if len(themes) == 2 else themes[0]
                    
                    # Create summary: Theme + first prompt snippet
                    if theme:
                        # Extract a short snippet from first prompt (max 50 chars)
                        prompt_snippet = first_prompt[:50].strip()
                        if len(first_prompt) > 50:
                            prompt_snippet += "..."
                        summary = f"{theme}: {prompt_snippet}"
                    else:
                        # Fallback: use first prompt snippet
                        summary = first_prompt[:80].strip()
                        if len(first_prompt) > 80:
                            summary += "..."
            
            sessions_data.append({
                "session_id": session.chat_session_id,
                "last_message_at": session.last_message_at.isoformat(),
                "message_count": session.message_count,
                "summary": summary
            })
        
        return {
            "user_id": user_id,
            "sessions": sessions_data,
            "count": len(sessions_data)
        }
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat sessions: {str(e)}"
        )


