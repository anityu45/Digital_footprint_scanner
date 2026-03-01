from fastapi import APIRouter, Response

from backend.auth.jwt_handler import create_access_token

router = APIRouter()


@router.post("/login")
def login(response: Response, username: str, password: str):
    # Temporary login validation (later connect DB)
    if username == "admin" and password == "password":
        token = create_access_token({"sub": username})

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,   # True in production
            samesite="Strict"
        )

        return {"message": "Login successful"}

    return {"error": "Invalid credentials"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}