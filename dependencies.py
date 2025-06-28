# dependencies.py
from fastapi import Header, HTTPException
import os

def verify_api_key(authorization: str = Header(None)):
    """Verify the API key from headers"""
    expected = os.getenv("API_KEY")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Missing or invalid Authorization header")
    token = authorization.split(" ")[1]
    if token != expected:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return True