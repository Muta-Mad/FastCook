from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.recipes.repository.mappers import map_tag_to_read
from api.recipes.repository.queries import get_tag_query, get_tags_query
from api.recipes.schemas import TagRead
from api.core.exceptions import GlobalError


router = APIRouter(prefix='/tags', tags=['Tags'])

@router.get('/', response_model=list[TagRead])
async def get_tags(
    session: AsyncSession = Depends(get_db)):
    """Получение списка тегов"""
    query = get_tags_query()
    result = await session.execute(query)
    tags = result.scalars().all()
    return [map_tag_to_read(tag) for tag in tags]

@router.get('/{id}/', response_model=TagRead)
async def get_tag(
    id: int,
    session: AsyncSession = Depends(get_db)):
    """Получение тега по id"""
    query = get_tag_query(id)
    result = await session.execute(query)
    tag = result.scalar_one_or_none()
    if not tag:
        GlobalError.not_found('Тег не найден.')
    return map_tag_to_read(tag)
