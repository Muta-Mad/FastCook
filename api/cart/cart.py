from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.cart.models import ShoppingCart
from api.cart.schemas import RecipeShort
from api.core.database import get_db
from api.core.exceptions import GlobalError
from api.dependencies import get_current_user
from api.cart.repository import get_shopping_cart_query
from api.recipes.repository.base import get_recipe, short_recipe
from api.users.models import User


router = APIRouter(prefix='/recipes/{id}/shopping_cart', tags=['Shopping Cart'])


@router.post('/', response_model=RecipeShort, status_code=status.HTTP_201_CREATED)
async def add_shopping_cart(
    id: int, 
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    result = await session.execute(get_recipe(id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        GlobalError.not_found('Рецепт не найден')
    query = await session.execute(get_shopping_cart_query(id, current_user))
    existing = query.scalar_one_or_none()
    if existing:
        GlobalError.bad_request('Рецепт уже в корзине')
    cart = ShoppingCart(
        user_id=current_user.id,
        recipe_id=recipe.id,
    )
    session.add(cart)
    await session.commit()
    return short_recipe(recipe)

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_cart(
    id: int, 
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):  
    result = await session.execute(get_recipe(id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        GlobalError.not_found('Рецепт не найден')
    result = await session.execute(get_shopping_cart_query(id, current_user))
    cart = result.scalar_one_or_none()
    if not cart:
        GlobalError.bad_request('Рецепт не в корзине')
    await session.delete(cart)
    await session.commit()
