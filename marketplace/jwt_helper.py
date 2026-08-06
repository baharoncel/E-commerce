import base64
import json
import hmac
import hashlib
import time
from django.conf import settings

def base64url_encode(data):
    if isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
    elif isinstance(data, str):
        data = data.encode('utf-8')
    encoded = base64.urlsafe_b64encode(data).decode('utf-8')
    return encoded.rstrip('=')

def base64url_decode(data):
    # Add padding
    rem = len(data) % 4
    if rem > 0:
        data += '=' * (4 - rem)
    return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')

def generate_jwt_token(user):
    """
    Generates a JWT token for a given CustomUser.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    # Token expires in 24 hours
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": int(time.time()) + 86400
    }
    
    header_encoded = base64url_encode(header)
    payload_encoded = base64url_encode(payload)
    
    signing_input = f"{header_encoded}.{payload_encoded}"
    secret_key = settings.SECRET_KEY.encode('utf-8')
    
    signature = hmac.new(secret_key, signing_input.encode('utf-8'), hashlib.sha256).digest()
    signature_encoded = base64url_encode(signature)
    
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def decode_jwt_token(token):
    """
    Decodes and validates a JWT token. Returns payload dict if valid, else None.
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_encoded, payload_encoded, signature_encoded = parts
        
        signing_input = f"{header_encoded}.{payload_encoded}"
        secret_key = settings.SECRET_KEY.encode('utf-8')
        
        expected_signature = hmac.new(secret_key, signing_input.encode('utf-8'), hashlib.sha256).digest()
        expected_signature_encoded = base64url_encode(expected_signature)
        
        # Verify signature
        if not hmac.compare_digest(signature_encoded, expected_signature_encoded):
            return None
            
        payload = json.loads(base64url_decode(payload_encoded))
        
        # Verify expiration
        if payload.get("exp", 0) < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None

def generate_refresh_token(user):

    """
    Generates a 30-day Refresh Token for silent auth renewal on mobile.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user_id": user.id,
        "type": "refresh",
        "exp": int(time.time()) + (86400 * 30)
    }
    header_encoded = base64url_encode(header)
    payload_encoded = base64url_encode(payload)
    signing_input = f"{header_encoded}.{payload_encoded}"
    secret_key = settings.SECRET_KEY.encode('utf-8')
    signature = hmac.new(secret_key, signing_input.encode('utf-8'), hashlib.sha256).digest()
    signature_encoded = base64url_encode(signature)
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def refresh_access_token(refresh_token):
    """
    Validates refresh token and returns a new 24h access token if valid.
    """
    payload = decode_jwt_token(refresh_token)
    if not payload or payload.get('type') != 'refresh':
        return None
    from marketplace.models import CustomUser
    try:
        user = CustomUser.objects.get(id=payload['user_id'])
        return generate_jwt_token(user)
    except CustomUser.DoesNotExist:
        return None

