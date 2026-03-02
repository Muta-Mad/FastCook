from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.recipes.models import Recipe, RecipeIngredient, RecipeTag


async def set_recipe_ingredients(
    session: AsyncSession,
    recipe: Recipe,
    ingredients: list,
):
    await session.execute(
        delete(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe.id
        )
    )
    new_items = [
        RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=item.id,
            amount=item.amount,
        )
        for item in ingredients
    ]
    session.add_all(new_items)

async def set_recipe_tags(
    session: AsyncSession,
    recipe: Recipe,
    tags: list[int],
    ):
    await session.execute(delete(RecipeTag).where(RecipeTag.recipe_id == recipe.id))
    new_items = [
        RecipeTag(
            recipe_id=recipe.id,
            tag_id=tag_id
        )
        for tag_id in tags
    ]
    session.add_all(new_items)

