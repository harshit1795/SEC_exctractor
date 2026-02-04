"""
User API Keys management endpoints
Handles BYOK (Bring Your Own Key) functionality
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models.user_api_keys import UserAPIKey
from app.services.encryption import get_encryption_service
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-api-keys", tags=["user-api-keys"])


class SetAPIKeyRequest(BaseModel):
    """Request model for setting an API key"""
    user_id: str
    key_type: str  # 'gemini' or 'fred'
    api_key: str


class ValidateAPIKeyRequest(BaseModel):
    """Request model for validating an API key"""
    user_id: str
    key_type: str  # 'gemini' or 'fred'


class DeleteAPIKeyRequest(BaseModel):
    """Request model for deleting an API key"""
    user_id: str
    key_type: str  # 'gemini' or 'fred'


@router.get("/status")
async def get_api_keys_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get status of user's API keys (without revealing the actual keys)
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Status of user's API keys
    """
    try:
        # Get user's API keys record
        user_keys = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == user_id
        ).first()
        
        if not user_keys:
            return {
                "user_id": user_id,
                "has_gemini_key": False,
                "has_fred_key": False,
                "gemini_key_is_valid": None,
                "fred_key_is_valid": None,
            }
        
        return user_keys.to_dict()
    except Exception as e:
        logger.error(f"Error getting API keys status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving API keys status: {str(e)}"
        )


@router.post("/set")
async def set_api_key(
    request: SetAPIKeyRequest,
    db: Session = Depends(get_db)
):
    """
    Set/update a user's API key
    
    Args:
        request: Set API key request
        db: Database session
    
    Returns:
        Success message
    """
    try:
        # Validate key type
        if request.key_type not in ['gemini', 'fred']:
            raise HTTPException(
                status_code=400,
                detail="key_type must be 'gemini' or 'fred'"
            )
        
        # Validate API key is not empty
        if not request.api_key or not request.api_key.strip():
            raise HTTPException(
                status_code=400,
                detail="API key cannot be empty"
            )
        
        # Encrypt the API key
        encryption_service = get_encryption_service()
        encrypted_key = encryption_service.encrypt_api_key(request.api_key.strip())
        
        # Get or create user's API keys record
        user_keys = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == request.user_id
        ).first()
        
        if not user_keys:
            user_keys = UserAPIKey(user_id=request.user_id)
            db.add(user_keys)
        
        # Update the appropriate key
        if request.key_type == 'gemini':
            user_keys.gemini_api_key_encrypted = encrypted_key
            user_keys.gemini_key_is_valid = None  # Reset validation status
            user_keys.gemini_key_last_validated = None
        elif request.key_type == 'fred':
            user_keys.fred_api_key_encrypted = encrypted_key
            user_keys.fred_key_is_valid = None  # Reset validation status
            user_keys.fred_key_last_validated = None
        
        db.commit()
        db.refresh(user_keys)
        
        logger.info(f"API key set for user {request.user_id}, type: {request.key_type}")
        
        return {
            "success": True,
            "message": f"{request.key_type.capitalize()} API key set successfully",
            "status": user_keys.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error setting API key: {str(e)}"
        )


@router.post("/validate")
async def validate_api_key(
    request: ValidateAPIKeyRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a user's API key by testing it with the respective service
    
    Args:
        request: Validate API key request
        db: Database session
    
    Returns:
        Validation result
    """
    try:
        # Validate key type
        if request.key_type not in ['gemini', 'fred']:
            raise HTTPException(
                status_code=400,
                detail="key_type must be 'gemini' or 'fred'"
            )
        
        # Get user's API keys record
        user_keys = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == request.user_id
        ).first()
        
        if not user_keys:
            raise HTTPException(
                status_code=404,
                detail="No API keys found for this user"
            )
        
        # Get the encrypted key
        if request.key_type == 'gemini':
            encrypted_key = user_keys.gemini_api_key_encrypted
        elif request.key_type == 'fred':
            encrypted_key = user_keys.fred_api_key_encrypted
        
        if not encrypted_key:
            raise HTTPException(
                status_code=404,
                detail=f"No {request.key_type} API key found for this user"
            )
        
        # Decrypt the key
        encryption_service = get_encryption_service()
        api_key = encryption_service.decrypt_api_key(encrypted_key)
        
        # Validate the key with the respective service
        is_valid = False
        error_message = None
        
        if request.key_type == 'gemini':
            # Test Gemini API key
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('models/gemini-flash-latest')
                # Simple test request
                response = model.generate_content("Test")
                is_valid = bool(response and response.text)
            except Exception as e:
                error_message = str(e)
                logger.error(f"Gemini API key validation failed: {e}")
        
        elif request.key_type == 'fred':
            # Test FRED API key
            try:
                from fredapi import Fred
                fred = Fred(api_key=api_key)
                # Simple test request
                fred.get_series('GDP', limit=1)
                is_valid = True
            except Exception as e:
                error_message = str(e)
                logger.error(f"FRED API key validation failed: {e}")
        
        # Update validation status
        if request.key_type == 'gemini':
            user_keys.gemini_key_is_valid = is_valid
            user_keys.gemini_key_last_validated = datetime.now()
        elif request.key_type == 'fred':
            user_keys.fred_key_is_valid = is_valid
            user_keys.fred_key_last_validated = datetime.now()
        
        db.commit()
        db.refresh(user_keys)
        
        return {
            "success": True,
            "is_valid": is_valid,
            "error_message": error_message if not is_valid else None,
            "status": user_keys.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error validating API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error validating API key: {str(e)}"
        )


@router.delete("/delete")
async def delete_api_key(
    user_id: str,
    key_type: str,
    db: Session = Depends(get_db)
):
    """
    Delete a user's API key
    
    Args:
        user_id: User ID
        key_type: Type of key to delete ('gemini' or 'fred')
        db: Database session
    
    Returns:
        Success message
    """
    try:
        # Validate key type
        if key_type not in ['gemini', 'fred']:
            raise HTTPException(
                status_code=400,
                detail="key_type must be 'gemini' or 'fred'"
            )
        
        # Get user's API keys record
        user_keys = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == user_id
        ).first()
        
        if not user_keys:
            raise HTTPException(
                status_code=404,
                detail="No API keys found for this user"
            )
        
        # Delete the appropriate key
        if key_type == 'gemini':
            user_keys.gemini_api_key_encrypted = None
            user_keys.gemini_key_is_valid = None
            user_keys.gemini_key_last_validated = None
        elif key_type == 'fred':
            user_keys.fred_api_key_encrypted = None
            user_keys.fred_key_is_valid = None
            user_keys.fred_key_last_validated = None
        
        db.commit()
        db.refresh(user_keys)
        
        logger.info(f"API key deleted for user {user_id}, type: {key_type}")
        
        return {
            "success": True,
            "message": f"{key_type.capitalize()} API key deleted successfully",
            "status": user_keys.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting API key: {str(e)}"
        )


def get_user_api_key(user_id: str, key_type: str, db: Session) -> Optional[str]:
    """
    Helper function to get a decrypted user API key
    Used by other services (like FinancialAnalyzer)
    
    Args:
        user_id: User ID
        key_type: Type of key ('gemini' or 'fred')
        db: Database session
    
    Returns:
        Decrypted API key or None if not found
    """
    try:
        user_keys = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == user_id
        ).first()
        
        if not user_keys:
            return None
        
        # Get the encrypted key
        if key_type == 'gemini':
            encrypted_key = user_keys.gemini_api_key_encrypted
        elif key_type == 'fred':
            encrypted_key = user_keys.fred_api_key_encrypted
        else:
            return None
        
        if not encrypted_key:
            return None
        
        # Decrypt and return
        encryption_service = get_encryption_service()
        return encryption_service.decrypt_api_key(encrypted_key)
    except Exception as e:
        logger.error(f"Error getting user API key: {e}")
        return None
