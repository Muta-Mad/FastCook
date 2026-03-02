from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import GlobalError
from api.recipes.models import Ingredient, Tag


async def validate_ingredients(
    session: AsyncSession,
    ingredient_data: list
):
    ingredien_ids = [item.id for item in ingredient_data]
    ingredien_ids_set = set(ingredien_ids)

    result = await session.execute(
        select(Ingredient.id).where(
            Ingredient.id.in_(ingredien_ids_set))
        )
    existing_ids = set(result.scalars().all())
    if ingredien_ids_set != existing_ids:
        GlobalError.bad_request('Нет такого ингредиента!')
    if len(ingredien_ids) != len(ingredien_ids_set):
        GlobalError.bad_request('Ингредиенты не должны повторяться')

async def validate_tags(
    session: AsyncSession,
    tag_ids: list
):
    tag_ids_set = set(tag_ids)
    result = await session.execute(
        select(Tag.id).where(
            Tag.id.in_(tag_ids_set))
        )
    existing_ids = set(result.scalars().all())
    if tag_ids_set != existing_ids:
        GlobalError.bad_request('Нет такого тега')
    if len(tag_ids) != len(tag_ids_set):
        GlobalError.bad_request('Теги не должны повторяться')