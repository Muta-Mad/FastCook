from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.recipes.repository.mappers import map_ingredient_to_read
from api.recipes.repository.queries import get_ingredient_query, get_ingredients_query
from api.recipes.schemas import IngredientRead
from api.core.exceptions import GlobalError

router = APIRouter(prefix='/ingredients', tags=['Ingredients'])

@router.get('/', response_model=list[IngredientRead])
async def get_ingredients(session: AsyncSession = Depends(get_db)):
    """Получение списка ингредиентов"""
    result = await session.execute(get_ingredients_query())
    ingredients = result.scalars().all()
    return [map_ingredient_to_read(ingredient) for ingredient in ingredients]

@router.get('/{id}/', response_model=IngredientRead)
async def get_ingredient(
    id: int,
    session: AsyncSession = Depends(get_db)):
    """Получение одного ингредиента"""
    result = await session.execute(get_ingredient_query(id))
    ingredient = result.scalar_one_or_none()
    if not ingredient:
        GlobalError.not_found('Ингредиент не найден')
    return map_ingredient_to_read(ingredient)
