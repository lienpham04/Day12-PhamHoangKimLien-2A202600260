from fastapi import Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verifies the API key from X-API-Key header.
    Returns user_id if valid.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key. Please provide X-API-Key header."
        )
    
    if api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key."
        )
    
    # For this lab, we use the API key itself or a derived string as user_id
    return f"user_{api_key[:8]}"
