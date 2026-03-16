from fastapi import Request, HTTPException, status
from backend.auth.jwt_handler import verify_token

def get_current_user(request: Request) -> str:
    """
    Checks for a Bearer token in the Authorization header.
    Works perfectly with the provided Postman collection.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    username = verify_token(token)
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token"
        )
        
    return username