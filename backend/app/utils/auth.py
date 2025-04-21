from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer
from typing import Optional

SECRET_KEY = "your-secret-key-here"  # In production, use a secure secret key
serializer = URLSafeTimedSerializer(SECRET_KEY)

def create_session_token(username: str) -> str:
    """Create a session token for the user."""
    return serializer.dumps(username)

def get_username_from_token(token: str) -> Optional[str]:
    """Get username from session token."""
    try:
        return serializer.loads(token, max_age=3600)  # Token expires in 1 hour
    except:
        return None

def get_current_user(request: Request) -> str:
    """Get current user from session cookie."""
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    username = get_username_from_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return username

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated."""
    try:
        get_current_user(request)
        return True
    except:
        return False 