from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.recipes.models import Recipe
from api.users.schemas import RecipeSubscribers


async def get_recipe_subscribers(
        session: AsyncSession, 
        author_id: int,
        limit: int | None
    ):
    query = select(Recipe).where(Recipe.author_id == author_id)
    if limit:
        query = query.limit(limit)
    result = await session.execute(query)
    recipes = result.scalars().all()
    return [
        RecipeSubscribers(
            id=recipe.id,
            name=recipe.name,
            image=recipe.image,
            cooking_time=recipe.cooking_time
        )
        for recipe in recipes
    ]
