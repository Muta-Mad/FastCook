from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.cart.models import ShoppingCart
from api.favorite.models import Favorite


def get_result_favorite(user_id: int, recipe_ids: list[int]):
    return select(Favorite.recipe_id).where(
        Favorite.user_id == user_id).where(
        Favorite.recipe_id.in_(recipe_ids)
    )

def get_result_cart(user_id: int, recipe_ids: list[int]):
    return select(ShoppingCart.recipe_id).where(
        ShoppingCart.user_id == user_id).where(
            ShoppingCart.recipe_id.in_(recipe_ids)
        )

async def get_user_recipe_flags(
        session: AsyncSession, 
        user_id: int,
        recipe_ids: list[int]
    ):
    if not recipe_ids:
        return set(), set()
    favorite_stmt = get_result_favorite(user_id, recipe_ids)
    cart_stmt = get_result_cart(user_id, recipe_ids)

    favorite_ids = set((await session.execute(favorite_stmt)).scalars().all())
    cart_ids = set((await session.execute(cart_stmt)).scalars().all())
    return favorite_ids, cart_ids
