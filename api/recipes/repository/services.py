from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import GlobalError
from api.recipes.models import Recipe, RecipeIngredient
from api.recipes.repository.queries import recipe_relations


async def get_full_recipe(
    session: AsyncSession,
    recipe_id: int
) -> Recipe:
    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.author),
            selectinload(Recipe.tags),
            selectinload(Recipe.recipe_ingredients)
                .selectinload(RecipeIngredient.ingredient),
        )
        .where(Recipe.id == recipe_id)
    )
    result = await session.execute(stmt)
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise GlobalError.not_found('Рецепт не найден.')
    return recipe

async def get_owned_recipe(
    session: AsyncSession,
    recipe_id: int,
    user_id: int,
) -> Recipe:
    result = await session.execute(select(Recipe).options(*recipe_relations()).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        GlobalError.not_found('Страница не найдена.')
    if recipe.author_id != user_id:
        GlobalError.forbidden('У вас недостаточно прав.')
    return recipe
