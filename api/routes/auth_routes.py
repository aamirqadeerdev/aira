from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.schemas import LoginRequest, TokenResponse, APIResponse
from api.auth import hash_password, verify_password, create_access_token, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── DEMO USERS (replace with database in production) ──
DEMO_USERS = {
    "admin@aira.com": {
        "password": hash_password("Admin@1234"),
        "role":     "admin",
        "name":     "AIRA Administrator"
    },
    "analyst@aira.com": {
        "password": hash_password("Analyst@1234"),
        "role":     "analyst",
        "name":     "AIRA Analyst"
    }
}

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    user = DEMO_USERS.get(request.email)
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    token = create_access_token(
        data={"sub": request.email, "role": user["role"]},
        expires_delta=timedelta(hours=1)
    )
    return TokenResponse(
        access_token = token,
        token_type   = "bearer",
        expires_in   = 3600,
        user_email   = request.email,
        user_role    = user["role"]
    )

@router.get("/me", tags=["Authentication"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return current authenticated user details."""
    return {"user": current_user, "status": "authenticated"}

@router.post("/logout", tags=["Authentication"])
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current user."""
    return APIResponse(success=True, message="Logged out successfully.")
