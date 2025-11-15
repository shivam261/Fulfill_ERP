from fastapi import APIRouter, Depends
from sqlmodel import Session
from .schemas import Login_user_request, Login_user_response, Register_user_response
from src.database import get_session
from .model import User
from .service import authenticate_user, register_user
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Login_user_response,summary="User login",)
async def login(
    login_req: Login_user_request,
    session: Session = Depends(get_session)
) -> Login_user_response:
    """
    ACCEPTS username and password in the request body.
    RETURNS a success message and the username if credentials are correct.
    RAISES HTTPException 401 if credentials are incorrect.
    """
    # Authenticate user
    user = await authenticate_user(login_req.username, login_req.password, session)

    return Login_user_response(username=user.username)

@router.post("/register", response_model=Register_user_response,summary="User registration",)
async def register(
    user: User,
    session: Session = Depends(get_session)
) -> Register_user_response:
    """
    ACCEPTS user details in the request body.
    RETURNS a success message and the username upon successful registration.
    RAISES HTTPException 400 if the username already exists.
    """
    user = await register_user(user, session)

    return Register_user_response(username=user.username)