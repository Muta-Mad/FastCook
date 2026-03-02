
from fastapi import APIRouter, Depends, Query, status
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.base_paginator import Paginator
from api.core.baserepository import BaseRepository
from api.core.database import get_db
from api.core.exceptions import GlobalError
from api.core.paginate_schemas import Page
from api.dependencies import get_current_user, get_repository, get_user_manager
from api.users.manager import UserManager
from api.users.models import User
from api.users.repository.mappers import get_subscribe_schema
from api.users.repository.queries import created_user, get_user_by_id, get_user_subscriptions_query
from api.users.repository.services import subscribe_user, unsubscribe_user
from api.users.schemas import (Avatar, SetPassword, UserCreate, UserRead,
                               UserResponse, SubscribeSchemas)


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/subscriptions/', response_model=Page[SubscribeSchemas])
async def subscribe(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    paginator: Paginator = Depends(Paginator),
    recipes_limit: int | None = Query(None)
):
    """Получение подписки"""
    query = get_user_subscriptions_query(user_id=current_user.id)
    paginated_response = await paginator.get_paginate(
        session=session, 
        model=User, 
        base_query=query
    )
    paginated_response['results'] = [
        await get_subscribe_schema(author, session, recipes_limit)
        for author in paginated_response['results']
    ]
    return paginated_response

@router.post('/', response_model=UserResponse, status_code=201)
async def create_user(
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_db)
)-> User | None:
    """Регистрация пользователя"""
    result = await session.execute(created_user(user_create))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        GlobalError.bad_request('Пользователь с таким username уже существует')
    try:
        user = await user_manager.create(user_create, safe=True)
        return user
    except UserAlreadyExists:
        GlobalError.bad_request('Пользователь уже существует')

@router.get('/', response_model=Page[UserRead])
async def get_users(
    session: AsyncSession = Depends(get_db),
    paginator: Paginator = Depends(Paginator) 
):
    """Список пользователей"""
    return await paginator.get_paginate(session, User)

@router.get('/me/', response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    """Текущий пользователь"""
    return user

@router.get('/{id}/', response_model=UserRead)
async def user(
    id: int,
    session: AsyncSession = Depends(get_db)
)-> User | None:
    """Профиль пользователя"""
    result = await session.execute(
        get_user_by_id(user_id=id)
    )
    user = result.scalar_one_or_none()
    if not user:
        GlobalError.not_found('Страница не найдена.')
    return user

@router.put('/me/avatar/', response_model=Avatar)
async def avatar(
    data: Avatar,
    current_user: User = Depends(get_current_user),
    repository: BaseRepository = Depends(get_repository)
    )-> Avatar:
    """Добавление аватара"""
    await repository.update(current_user, avatar=data.avatar)
    return data

@router.delete('/me/avatar/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    repository: BaseRepository = Depends(get_repository)
    ):
    """Удаление аватара"""
    await repository.update(current_user, avatar=None)

@router.post('/set_password/', status_code=status.HTTP_204_NO_CONTENT)
async def set_password(
    data: SetPassword,
    user: User = Depends(get_current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Изменение пароля"""
    verified, _ = user_manager.password_helper.verify_and_update(
        data.current_password, 
        user.hashed_password
    )
    if not verified:
        GlobalError.bad_request('Неверный пароль')
    await user_manager._update(user, {'password': data.new_password})

@router.post('/{id}/subscribe/', response_model=SubscribeSchemas, status_code=status.HTTP_201_CREATED)
async def add_subscribe(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    recipes_limit: int | None = Query(None)
):
    """Добавления подписки"""
    author = await subscribe_user(session, current_user, id)
    return await get_subscribe_schema(author, session, recipes_limit)

@router.delete('/{id}/subscribe/', status_code=status.HTTP_204_NO_CONTENT)
async def remove_subscribe(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Удаление подписки"""
    await unsubscribe_user(session, current_user, id)
    