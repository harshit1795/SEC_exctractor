"""
Chat and AI analysis API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.data_source_manager import DataSourceManager
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatHistoryResponse,
    ChatSessionResponse, ChatSessionDetailResponse, ChatMessageResponse
)
import json
from typing import Optional
import uuid
import logging
import hashlib
import diskcache as dc
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Global instances (used when no BYOK key is supplied)
_analyzer: Optional[FinancialAnalyzer] = None
_data_manager: Optional[DataSourceManager] = None


def get_analyzer(byok_key: Optional[str] = None) -> FinancialAnalyzer:
    """Get or create FinancialAnalyzer instance.

    If a BYOK key is provided (from the X-Gemini-API-Key header),
    a fresh instance is created with that key for this request.
    Otherwise, the global singleton backed by the backend's .env key is used.
    """
    if byok_key:
        try:
            return FinancialAnalyzer(api_key=byok_key)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Provided Gemini API key is invalid: {str(e)}"
            )

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
    import numpy as np
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
        # Check for NaN first (only for scalar values to avoid ambiguity)
        if isinstance(v, float) and np.isnan(v):
            clean[clean_key] = None
        elif isinstance(v, (pd.Timestamp, datetime)):
            try:
                if pd.isna(v):
                    clean[clean_key] = None
                else:
                    clean[clean_key] = v.isoformat() if hasattr(v, 'isoformat') else str(v)
            except (ValueError, TypeError):
                # pd.isna() failed, use value as-is
                clean[clean_key] = v.isoformat() if hasattr(v, 'isoformat') else str(v)
        elif isinstance(v, pd.DataFrame):
            # Reset index if it contains Timestamps, then convert to records
            if isinstance(v.index, pd.DatetimeIndex):
                v = v.reset_index()
            # Convert to dict, replacing NaN with None
            records = v.to_dict(orient='records')
            clean[clean_key] = [{k: (None if pd.isna(v) else v) for k, v in record.items()} for record in records]
        elif isinstance(v, pd.Series):
            # Convert Series, handling Timestamp index and NaN values
            if isinstance(v.index, pd.DatetimeIndex):
                clean[clean_key] = {str(idx): (None if pd.isna(val) else _clean_value(val)) for idx, val in v.items()}
            else:
                clean[clean_key] = {str(k): (None if pd.isna(v) else _clean_value(v)) for k, v in v.to_dict().items()}
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
    import numpy as np
    from datetime import datetime
    
    # Handle pandas/numpy arrays and DataFrames first
    if isinstance(val, pd.DataFrame):
        if isinstance(val.index, pd.DatetimeIndex):
            val = val.reset_index()
        # Convert DataFrame to dict, replacing NaN with None
        records = val.to_dict(orient='records')
        cleaned_records = []
        for record in records:
            cleaned_record = {}
            for k, v in record.items():
                # Safe NaN check - only for scalar values
                if isinstance(v, float) and np.isnan(v):
                    cleaned_record[k] = None
                elif isinstance(v, (int, str, bool, type(None))):
                    cleaned_record[k] = v
                else:
                    # For other types, try pd.isna() with error handling
                    try:
                        if pd.isna(v):
                            cleaned_record[k] = None
                        else:
                            cleaned_record[k] = v
                    except (ValueError, TypeError):
                        # pd.isna() failed (likely array), clean recursively
                        cleaned_record[k] = _clean_value(v)
            cleaned_records.append(cleaned_record)
        return cleaned_records
    elif isinstance(val, pd.Series):
        if isinstance(val.index, pd.DatetimeIndex):
            return {str(idx): _clean_value(v) for idx, v in val.items()}
        return {str(k): _clean_value(v) for k, v in val.to_dict().items()}
    elif isinstance(val, np.ndarray):
        # Convert numpy array to list
        return [_clean_value(item) for item in val.tolist()]
    elif isinstance(val, (pd.Timestamp, datetime)):
        # Check for NaT (Not a Time) - use try/except to handle ambiguity
        try:
            if pd.isna(val):
                return None
        except (ValueError, TypeError):
            # pd.isna() failed, assume valid
            pass
        return val.isoformat() if hasattr(val, 'isoformat') else str(val)
    elif isinstance(val, float):
        # Check for NaN/Inf in scalar float values
        if np.isnan(val) or np.isinf(val):
            return None
        return val
    elif isinstance(val, (int, str, bool, type(None))):
        return val
    elif isinstance(val, dict):
        return _clean_dict_for_storage(val)
    elif isinstance(val, list):
        return [_clean_value(item) for item in val]
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
    Converts NaN values to None (null in JSON)
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import json
    
    def convert_value(val):
        """Recursively convert non-serializable values"""
        # Handle arrays first to avoid ambiguity errors
        if isinstance(val, (pd.Series, pd.DataFrame, np.ndarray)):
            # Don't check pd.isna() on arrays directly
            pass
        elif isinstance(val, (pd.Timestamp, datetime)):
            # Check for NaT (Not a Time)
            try:
                if pd.isna(val):
                    return None
            except (ValueError, TypeError):
                # If pd.isna() fails (array-like), skip the check
                pass
            return val.isoformat() if hasattr(val, 'isoformat') else str(val)
        elif isinstance(val, (int, float)):
            # Check for NaN/Inf in scalar values
            if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                return None
            return val
        elif isinstance(val, (str, bool, type(None))):
            return val
        elif isinstance(val, pd.DataFrame):
            # Convert DataFrame to list of dicts, replacing NaN with None
            records = val.to_dict(orient='records')
            cleaned_records = []
            for record in records:
                cleaned_record = {}
                for k, v in record.items():
                    # Safe NaN check - only for scalar values
                    if isinstance(v, float) and np.isnan(v):
                        cleaned_record[k] = None
                    elif isinstance(v, (int, float, str, bool, type(None))):
                        try:
                            if pd.isna(v):
                                cleaned_record[k] = None
                            else:
                                cleaned_record[k] = v
                        except (ValueError, TypeError):
                            # pd.isna() failed (likely array), use value as-is
                            cleaned_record[k] = v
                    else:
                        cleaned_record[k] = convert_value(v)
                cleaned_records.append(cleaned_record)
            return cleaned_records
        elif isinstance(val, pd.Series):
            # Convert Series to dict, replacing NaN with None
            series_dict = val.to_dict()
            cleaned_dict = {}
            for k, v in series_dict.items():
                # Safe NaN check
                if isinstance(v, float) and np.isnan(v):
                    cleaned_dict[str(k)] = None
                elif isinstance(v, (int, float, str, bool, type(None))):
                    try:
                        if pd.isna(v):
                            cleaned_dict[str(k)] = None
                        else:
                            cleaned_dict[str(k)] = convert_value(v)
                    except (ValueError, TypeError):
                        cleaned_dict[str(k)] = convert_value(v)
                else:
                    cleaned_dict[str(k)] = convert_value(v)
            return cleaned_dict
        elif isinstance(val, dict):
            return _clean_dict(val)
        elif isinstance(val, list):
            return [convert_value(item) for item in val]
        else:
            # Try to serialize, fallback to string
            try:
                json.dumps(val)
                return val
            except (TypeError, ValueError):
                return str(val)
    
    def _clean_dict(d):
        """Clean a dictionary, handling Timestamp keys and NaN values"""
        clean = {}
        for k, v in d.items():
            # Convert key if it's a Timestamp
            if isinstance(k, (pd.Timestamp, datetime)):
                clean_key = k.isoformat() if hasattr(k, 'isoformat') else str(k)
            elif isinstance(k, (int, float, str, bool, type(None))):
                clean_key = k
            else:
                clean_key = str(k)
            
            # Convert value, handling NaN safely
            if isinstance(v, float) and np.isnan(v):
                clean[clean_key] = None
            elif isinstance(v, (pd.Series, pd.DataFrame, np.ndarray)):
                # Handle arrays/DataFrames separately to avoid ambiguity
                clean[clean_key] = convert_value(v)
            else:
                # For scalar values, try pd.isna() with error handling
                try:
                    if pd.isna(v):
                        clean[clean_key] = None
                    else:
                        clean[clean_key] = convert_value(v)
                except (ValueError, TypeError):
                    # pd.isna() failed (likely array-like), use convert_value
                    clean[clean_key] = convert_value(v)
        return clean
    
    return _clean_dict(context)


def _truncate_large_data(data: dict, max_size_mb: float = 2.0) -> dict:
    """
    Truncate large datasets to reduce memory usage.
    Keeps essential data but limits size of large arrays/DataFrames.
    """
    import sys
    import json
    
    # Estimate size in MB
    try:
        size_bytes = sys.getsizeof(json.dumps(data, default=str))
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb <= max_size_mb:
            return data
    except:
        pass
    
    # Truncate large datasets
    truncated = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            # For nested dicts (like yahoo_data), truncate large arrays
            truncated[key] = {}
            for subkey, subvalue in value.items():
                if isinstance(subvalue, list) and len(subvalue) > 100:
                    # Keep only first 100 records
                    truncated[key][subkey] = subvalue[:100]
                    logger.info(f"Truncated {key}.{subkey} from {len(subvalue)} to 100 records")
                elif isinstance(subvalue, dict) and len(subvalue) > 50:
                    # For dicts, keep only first 50 items
                    truncated[key][subkey] = dict(list(subvalue.items())[:50])
                    logger.info(f"Truncated {key}.{subkey} from {len(subvalue)} to 50 items")
                else:
                    truncated[key][subkey] = subvalue
        elif isinstance(value, list) and len(value) > 500:
            # Truncate large lists
            truncated[key] = value[:500]
            logger.info(f"Truncated {key} from {len(value)} to 500 items")
        else:
            truncated[key] = value
    
    return truncated


async def _gather_context_data(context_data: dict, data_manager: DataSourceManager) -> dict:
    """
    Gather all available context data for analysis
    Similar to Streamlit version's _gather_context_data
    Optimized to reduce memory usage by limiting data size
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
                    # Limit history data size - only keep last 252 trading days (1 year)
                    if 'history_df' in ticker_data and isinstance(ticker_data['history_df'], list):
                        if len(ticker_data['history_df']) > 252:
                            ticker_data['history_df'] = ticker_data['history_df'][-252:]
                            logger.info(f"Limited history data for {ticker} to 252 records")
                    
                    # Limit history dict size
                    if 'history' in ticker_data and isinstance(ticker_data['history'], dict):
                        if len(ticker_data['history']) > 252:
                            # Keep only last 252 items
                            ticker_data['history'] = dict(list(ticker_data['history'].items())[-252:])
                    
                    # Clean ticker data to remove Timestamps - use helper function
                    yahoo_data[ticker] = _clean_dict_for_storage(ticker_data)
            except Exception as e:
                logger.warning(f"Could not fetch Yahoo Finance data for {ticker}: {e}")
        
        if yahoo_data:
            context['yahoo_data'] = yahoo_data
        
        # Fetch fundamentals data - limit size
        all_fundamentals = []
        for ticker in context_data['selected_tickers']:
            try:
                fundamentals = await data_manager.get_fundamentals_data(ticker)
                if not fundamentals.empty:
                    # Reset index if it contains Timestamps
                    if isinstance(fundamentals.index, pd.DatetimeIndex):
                        fundamentals = fundamentals.reset_index()
                    # Limit to last 20 periods to reduce size
                    if len(fundamentals) > 20:
                        fundamentals = fundamentals.tail(20)
                        logger.info(f"Limited fundamentals for {ticker} to 20 periods")
                    # Convert to dict format immediately to avoid Timestamp issues
                    all_fundamentals.append(fundamentals.to_dict(orient='records'))
            except Exception as e:
                logger.warning(f"Could not fetch fundamentals for {ticker}: {e}")
        
        if all_fundamentals:
            # Flatten list of records
            context['fundamentals_data'] = [item for sublist in all_fundamentals for item in sublist]
    
    # Economic data - limit size
    if 'economic_data' in context_data:
        economic_data = context_data['economic_data']
        # If it's a DataFrame, convert it and limit size
        if isinstance(economic_data, pd.DataFrame):
            # Reset index if it contains Timestamps
            if isinstance(economic_data.index, pd.DatetimeIndex):
                economic_data = economic_data.reset_index()
            # Limit to last 500 rows
            if len(economic_data) > 500:
                economic_data = economic_data.tail(500)
                logger.info(f"Limited economic data to 500 records")
            context['economic_data'] = economic_data.to_dict(orient='records')
        elif isinstance(economic_data, list) and len(economic_data) > 500:
            context['economic_data'] = economic_data[-500:]
        else:
            context['economic_data'] = economic_data
    
    # Metric categories
    if 'metric_categories' in context_data:
        context['metric_categories'] = context_data['metric_categories']
    
    # 10-K data - limit size (keep only summary)
    if '10k_data' in context_data:
        sec_data = context_data['10k_data']
        if isinstance(sec_data, dict):
            # Only keep essential fields, truncate large text
            context['10k_data'] = {
                'ticker': sec_data.get('ticker'),
                'filing_date': sec_data.get('filing_date'),
                'summary': sec_data.get('summary', '')[:5000] if isinstance(sec_data.get('summary'), str) else sec_data.get('summary')
            }
        else:
            context['10k_data'] = sec_data
    
    # 10-Q data - limit size (keep only summary)
    if '10q_data' in context_data:
        sec_data = context_data['10q_data']
        if isinstance(sec_data, dict):
            # Only keep essential fields, truncate large text
            context['10q_data'] = {
                'ticker': sec_data.get('ticker'),
                'filing_date': sec_data.get('filing_date'),
                'summary': sec_data.get('summary', '')[:5000] if isinstance(sec_data.get('summary'), str) else sec_data.get('summary')
            }
        else:
            context['10q_data'] = sec_data
    
    # Available tickers - don't store full list, just count
    available_tickers = data_manager.get_available_tickers()
    context['available_tickers_count'] = len(available_tickers)
    # Only store first 100 tickers as sample
    context['available_tickers_sample'] = available_tickers[:100] if len(available_tickers) > 100 else available_tickers
    
    return context


@router.post("/analyze", response_model=ChatResponse)
async def analyze_financial_data(
    request: ChatRequest,
    db: Session = Depends(get_db),
    x_gemini_api_key: Optional[str] = Header(default=None, alias="X-Gemini-API-Key"),
):
    """
    Agentic Chat Endpoint: Analyzes financial data autonomously.
    """
    try:
        try:
            key_debug = f"{x_gemini_api_key[:8]}...{x_gemini_api_key[-4:]}" if x_gemini_api_key else "None (Using Default Env Key)"
            logger.error(f"====== CHAT REQUEST DEBUG ======")
            logger.error(f"Endpoint hit with BYOK Key: {key_debug}")
            logger.error(f"=================================")
            analyzer = get_analyzer(byok_key=x_gemini_api_key)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting analyzer: {e}")
            raise HTTPException(status_code=500, detail="AI service initialization failed. Please check GEMINI_API_KEY.")
            
        data_manager = get_data_manager()
        
        # 1. Handle Session
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
        else:
            # Create a new session
            session = ChatSession(
                user_id=request.context_data.get('user_id', 'anonymous'),
                title=request.prompt[:50] + "..." if len(request.prompt) > 50 else request.prompt,
                context_data=request.context_data
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
        # 2. Fetch Chat History for the prompt
        db_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        chat_history = []
        for msg in db_messages:
            if msg.role in ['user', 'model']:
                chat_history.append({"role": msg.role, "content": msg.content})
                
        # 3. Formulate the current prompt with context attached
        # Gather all the Yahoo finance data locally like flutter-rebuild did
        full_context = await _gather_context_data(request.context_data, data_manager)
        
        # We STILL embed the user's manual context_data selections into the prompt
        # but now we also pass the actual fetched data to the LLM.
        context_str = ""
        # Clean the context data for the prompt to save tokens (use truncated data)
        clean_context = _clean_context_for_storage(full_context)
        clean_context = _truncate_large_data(clean_context, max_size_mb=1.0) # slightly stricter for input
        
        if clean_context:
            context_str = f"SYSTEM INSTRUCTION (Context Data for Analysis):\n{json.dumps(clean_context, default=str)}\n\n"
            
        current_prompt = f"{context_str}USER PROMPT:\n{request.prompt}"
        
        # 4. Agentic Loop
        cache = dc.Cache(settings.cache_dir)
        cache_str = current_prompt + str(chat_history) + (x_gemini_api_key or "default")
        cache_key = f"chat_{hashlib.md5(cache_str.encode()).hexdigest()}"
        
        if cache_key in cache:
            logger.info(f"Returning cached chat response for session {session.id}")
            response_text = cache[cache_key]
        else:
            if request.agentic_mode:
                logger.info(f"Triggering agentic loop for session {session.id}")
                response_text = await analyzer.analyze_with_agent(
                    prompt=current_prompt,
                    chat_history=chat_history,
                    data_manager=data_manager
                )
            else:
                logger.info(f"Triggering standard generation for session {session.id}")
                response_text = await analyzer.analyze_standard(
                    prompt=current_prompt,
                    chat_history=chat_history
                )
            cache.set(cache_key, response_text, expire=settings.cache_ttl_llm)
        
        # 5. Save the new messages to history
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.prompt
        )
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="model",
            content=response_text
        )
        db.add_all([user_msg, assistant_msg])
        
        # Update session modify time
        session.updated_at = func.now()
        db.commit()
        
        return ChatResponse(
            response=response_text,
            session_id=session.id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat analysis: {e}", exc_info=True)
        db.rollback()
        
        # Parse error for specific frontend triggers
        error_str = str(e).lower()
        
        is_daily_quota = False
        if getattr(e, 'status_code', 0) == 429 and (
            'per day' in error_str or 'daily' in error_str or
            'generate_content_free_tier_requests' in error_str or
            'free_tier_input_token_count' in error_str
        ):
            is_daily_quota = True

        # Identify Quota / Rate Limit explicitly to trigger BYOK dialog on frontend
        # Only throw 429 back to user if it's the daily/hard limit, otherwise assume
        # backend exponential backoff handled it or it's a completely different error.
        if is_daily_quota:
            raise HTTPException(
                status_code=429,
                detail="Gemini API daily quota exceeded. Please provide your own API key."
            )
        elif '429' in error_str or getattr(e, 'status_code', 0) == 429:
            # For per-minute errors that exhausted all backend retries
             raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit exceeded (too many requests per minute). Please wait a moment and try again."
            )
            
        if 'api key' in error_str or 'authentication' in error_str or 'invalid' in error_str or '400' in error_str:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid Gemini API Key provided. Please check your key. Error: {str(e)}"
            )
            
        if 'gemini' in error_str:
            raise HTTPException(
                status_code=503,
                detail=f"FinQ AI service is temporarily unavailable. Server error: {str(e)}"
            )
            
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing financial data: {str(e)}"
        )


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    user_id: str,
    title: Optional[str] = "New Chat",
    context_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    try:
        session = ChatSession(
            user_id=user_id,
            title=title,
            context_data=context_data or {}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create chat session")


@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_user_chat_sessions(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of chat sessions for a user."""
    try:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).limit(limit).all()
        return sessions
    except Exception as e:
        logger.error(f"Error getting user chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions")


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_chat_session_detail(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific chat session with all its messages."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat session")


@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        db.delete(session)
        db.commit()
        return {"status": "success", "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session {session_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete chat session")


