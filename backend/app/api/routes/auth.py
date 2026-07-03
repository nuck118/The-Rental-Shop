from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

from fastapi_csrf_protect import CsrfProtect

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.core.user import verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


@router.get(
    "/csrf-token",
    status_code=status.HTTP_200_OK,
    summary="Get CSRF token",
    description="Generate and return a CSRF token cookie for state-changing requests.",
)
def get_csrf_token(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
):
    """
    Generate a CSRF token and set it as a signed HttpOnly cookie.

    The client must read the plain token from the response body and send it back
    in the `X-CSRF-Token` header on subsequent POST/PUT/PATCH/DELETE requests.
    """
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"csrf_token": csrf_token},
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT token",
)
async def login(
    request: Request,
    login_request: LoginRequest,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
):
    """
    Authenticate user with username and password.

    **Request Body:**
    - `username` (required): User's username
    - `password` (required): User's password

    **Response:**
    Returns JWT token and user information.

    **Error Responses:**
    - `401 Unauthorized`: Invalid credentials

    **Example Request:**
    ```json
    {
      "username": "admin",
      "password": "your_password"
    }
    ```

    **Example Response:**
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": true
      }
    }
    ```
    """
    await csrf_protect.validate_csrf(request)

    user = db.query(User).filter(User.username == login_request.username).first()

    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Generate JWT token
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
            },
        },
    )
    # Refresh CSRF cookie after successful login
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response
