from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.cart.schemas import RecipeShort
from api.core.database import get_db
from api.core.exceptions import GlobalError
from api.dependencies import get_current_user
from api.favorite.models import Favorite
from api.favorite.repository import get_favorite_query
from api.recipes.repository.base import get_recipe, short_recipe
from api.users.models import User


router = APIRouter(prefix='/recipes/{id}/favorite', tags=['Favorite'])

@router.post('/', response_model=RecipeShort, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Добавить в избранное"""
    result = await session.execute(get_recipe(id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        GlobalError.not_found('Рецепт не найден')
    favorite = Favorite(user_id=current_user.id, recipe_id=recipe.id)
    session.add(favorite)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        GlobalError.bad_request('Рецепт уже в избранном')
    return short_recipe(recipe)

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_cart(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Удалить из избранного"""
    result = await session.execute(get_recipe(id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        GlobalError.not_found('Рецепт не найден')
    result = await session.execute(get_favorite_query(id, current_user))
    favorite = result.scalar_one_or_none()
    if not favorite:
        GlobalError.bad_request('Рецепт не в избранном')
    await session.delete(favorite)
    await session.commit()
