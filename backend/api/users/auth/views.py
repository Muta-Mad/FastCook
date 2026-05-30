from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication.strategy import Strategy

from api.core.limiter import limiter, LOGIN_RATE_LIMIT
from api.dependencies import get_current_user, get_user_manager
from api.users.auth.backend import authentication_backend
from api.users.auth.transport import token_transport
from api.users.manager import UserManager
from api.users.models import User
from api.users.schemas import EmailPassword

router = APIRouter(prefix='/auth/token', tags=['Auth'])


@router.post('/login/', response_model=dict)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(
    request: Request,
    data: EmailPassword,
    user_manager: UserManager = Depends(get_user_manager),
    strategy: Strategy = Depends(authentication_backend.get_strategy),
) -> dict:
    """Получить токен авторизации"""
    credentials = OAuth2PasswordRequestForm(
        username=data.email,
        password=data.password,
    )
    user = await user_manager.authenticate(credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверный email или пароль')
    token = await strategy.write_token(user)
    return {
        'auth_token': token,
    }


@router.post('/logout/', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: User = Depends(get_current_user),
    token: str = Depends(token_transport),
    strategy: Strategy = Depends(authentication_backend.get_strategy)
):
    """Удаление токена"""
    await strategy.destroy_token(token, user)
    return None
